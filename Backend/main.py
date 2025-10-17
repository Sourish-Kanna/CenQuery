import os
import csv
import time
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text, inspect
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import List, Dict, Any, Union
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration ---
load_dotenv()

GENERATION_LOG_FILE = "generation_log.csv"
LOG_FILE = "metrics_log.csv"
# Use the DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please add it to your .env file.")

# Check for Groq API key
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY environment variable not set. Please add it to your .env file.")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Text-to-SQL API",
    description="An API with separate endpoints to generate SELECT queries, generate other SQL commands, and execute any SQL.",
    version="3.0.0"
)

# --- CORS Middleware ---
# This is the new section to handle CORS errors.
# It allows your frontend (e.g., running on localhost:3000) to communicate with the backend.
origins = [
    "http://localhost",
    "http://localhost:3000", # Add the origin of your React app
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# --- Database Connection ---
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
      print("Database connection successful.")
except Exception as e:
    print(f"Failed to connect to the database: {e}")
    print("Please ensure the PostgreSQL server is running and the DATABASE_URL is correct.")
    # Exit if DB connection fails
    exit()

# --- Pydantic Models ---
class GenerateSQLRequest(BaseModel):
    question: str = Field(..., description="The natural language instruction to convert to SQL.")

class GenerateSQLResponse(BaseModel):
    question: str
    sql_query: str

class ExecuteSQLRequest(BaseModel):
    sql_query: str = Field(..., description="The SQL query to execute.")
    question: str | None = Field(None, description="The original question (optional, for logging purposes).")

class ExecuteSQLResponse(BaseModel):
    sql_query: str
    result: Union[List[Dict[str, Any]], Dict[str, int], str]
    latency_ms: float
    status: str

# --- Logging ---
def log_generation(question: str, sql_query: str):
    """Logs the user question and the generated SQL query to a separate CSV file."""
    file_exists = os.path.isfile(GENERATION_LOG_FILE)
    with open(GENERATION_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["question", "generated_sql_query"])
        writer.writerow([question, sql_query])

def log_metrics(question: str | None, sql_query: str, latency: float, status: str):
    """Logs the performance and result of a query to a CSV file."""
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["question", "sql_query", "latency_ms", "status"])
        writer.writerow([question or "N/A", sql_query, latency, status])

# --- Core Logic ---
def get_schema(engine):
    """Retrieves the schema for all tables in the public schema for PostgreSQL."""
    try:
        inspector = inspect(engine)
        schema_info = []
        table_names = inspector.get_table_names(schema='public')
        for table_name in table_names:
            columns = inspector.get_columns(table_name, schema='public')
            column_names = ", ".join([col['name'] for col in columns])
            schema_info.append(f"Table '{table_name}' has columns: {column_names}")
        return "\n".join(schema_info)
    except Exception as e:
        print(f"Error retrieving schema: {e}")
        return "Could not retrieve schema from the database."

def _generate_query(question: str, prompt_template: str) -> GenerateSQLResponse:
    """Helper function to invoke the LLM for SQL generation."""
    db_schema = get_schema(engine)
    if "Could not retrieve" in db_schema:
         raise HTTPException(status_code=500, detail="Could not retrieve database schema.")
    
    prompt = PromptTemplate(
        input_variables=["schema", "question"],
        template=prompt_template
    )
    
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    sql_generation_chain = prompt | llm
    
    try:
        response_content = sql_generation_chain.invoke({"schema": db_schema, "question": question}).content
        sql_query = response_content.strip().replace("`", "").replace("sql", "") # Clean up LLM output
        # Log the successful generation
        log_generation(question, sql_query)
        return GenerateSQLResponse(question=question, sql_query=sql_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {e}")

# --- API Endpoints ---
@app.post("/generate-select-sql", response_model=GenerateSQLResponse)
async def generate_select_sql(request: GenerateSQLRequest):
    """
    Accepts a natural language question and returns a `SELECT` SQL query.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    prompt_template = """
    You are an expert in converting English questions to **read-only SELECT** queries for a PostgreSQL database.
    Given the database schema below, write a SQL query that answers the user's question. The query may require joining tables.
    **Only output a SELECT query.** Do not output any other type of SQL statement.
    **Important**: For any text-based filtering (e.g., in a WHERE clause), use the `ILIKE` operator for case-insensitive matching. The correct syntax is `column_name ILIKE 'value'`. For example: `WHERE district ILIKE 'pune'`. Do not use `ILIKE column_name = 'value'`.
    Carefully select only the columns asked for in the question.

    Schema:
    {schema}

    Question: {question}

    SQL SELECT Query:
    """
    return _generate_query(request.question, prompt_template)

@app.post("/generate-other-sql", response_model=GenerateSQLResponse)
async def generate_other_sql(request: GenerateSQLRequest):
    """
    Accepts a natural language instruction and returns a DML (INSERT, UPDATE, DELETE) or DDL (CREATE, ALTER) SQL command.
    **Warning:** Use with caution as this can modify the database.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Instruction cannot be empty.")

    prompt_template = """
    You are an expert in converting English instructions into data modification (DML) or schema modification (DDL) SQL commands for a PostgreSQL database.
    Given the database schema below, write a single SQL command that performs the requested action.
    **This is for expert use. The generated query can be INSERT, UPDATE, DELETE, CREATE, ALTER, or DROP.**

    For INSERT statements, you can add multiple records at once if the instruction implies it. For example, the instruction "Add population data for Thane (1.8m male, 1.6m female) and Dombivli (600k male, 550k female) in Maharashtra for 2011" should generate:
    INSERT INTO population (state, district, year, male, female, total) VALUES
    ('Maharashtra', 'Thane', 2011, 1800000, 1600000, 3400000),
    ('Maharashtra', 'Dombivli', 2011, 600000, 550000, 1150000);
    Remember to calculate the 'total' column yourself by adding male and female.

    **Important**: For any text-based filtering (e.g., in a WHERE clause), use the `ILIKE` operator for case-insensitive matching. The correct syntax is `column_name ILIKE 'value'`. For example: `WHERE district ILIKE 'pune'`. Do not use `ILIKE column_name = 'value'`.
    Carefully select only the columns asked for in the question. And dont use \\n in the output.

    Schema:
    {schema}

    Instruction: {question}

    SQL Command:
    """
    return _generate_query(request.question, prompt_template)

@app.post("/execute-sql", response_model=ExecuteSQLResponse)
async def execute_sql(request: ExecuteSQLRequest):
    """
    Executes a given SQL query and returns the result from the database.
    """
    if not request.sql_query.strip():
        raise HTTPException(status_code=400, detail="SQL query cannot be empty.")

    start_time = time.time()
    try:
        with engine.connect() as connection:
            # For queries that don't return rows (like INSERT, UPDATE, DELETE), use a transaction
            if any(keyword in request.sql_query.strip().upper() for keyword in ["INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP"]):
                 with connection.begin(): # Start transaction
                    result_proxy = connection.execute(text(request.sql_query))
                    result = {"rows_affected": result_proxy.rowcount}
            else: # For SELECT queries
                df = pd.read_sql_query(sql=text(request.sql_query), con=connection)
                result = df.to_dict(orient='records')

            status = "success"
    except Exception as e:
        result = str(e)
        status = "error"
        
    latency = (time.time() - start_time) * 1000
    log_metrics(request.question, request.sql_query, latency, status)
    
    return ExecuteSQLResponse(
        sql_query=request.sql_query,
        result=result,
        latency_ms=latency,
        status=status
    )

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Text-to-SQL API is running. Go to /docs for the API documentation."}

