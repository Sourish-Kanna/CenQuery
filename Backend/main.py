import os
import csv
import time
import json
import httpx
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
INFERENCE_SERVER_URL = os.getenv("INFERENCE_SERVER_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
GENERATION_LOG_FILE = "generation_log.csv"
LOG_FILE = "metrics_log.csv"
JSON_SCHEMA_PATH = "database_schema.json"  # Ensure this file exists in Backend folder

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is missing in .env")
if not INFERENCE_SERVER_URL:
    print("⚠️ WARNING: INFERENCE_SERVER_URL is missing. LLM calls will fail.")

# Initialize App & DB
app = FastAPI(title="CenQuery Backend Orchestrator")
engine = create_engine(DATABASE_URL)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- DATA MODELS ---
class QueryRequest(BaseModel):
    question: str


# --- LOGGING FUNCTIONS ---
def log_generation(question: str, sql_query: str):
    """Logs the prompt and generated SQL."""
    file_exists = os.path.isfile(GENERATION_LOG_FILE)
    try:
        with open(GENERATION_LOG_FILE, "a", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["question", "generated_sql_query"])
            writer.writerow([question, sql_query])
    except Exception as e:
        print(f"⚠️ Log Generation Error: {e}")


def log_metrics(question: str | None, sql_query: str, latency: float, status: str):
    """Logs performance metrics."""
    file_exists = os.path.isfile(LOG_FILE)
    try:
        with open(LOG_FILE, "a", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["question", "sql_query", "latency_ms", "status"])
            writer.writerow([question or "N/A", sql_query, latency, status])
    except Exception as e:
        print(f"⚠️ Log Metrics Error: {e}")


# --- SCHEMA MANAGEMENT (Caching + Fallback) ---
# Global cache variable
SCHEMA_CACHE = {
    "text": None,
    "last_updated": 0
}
CACHE_TTL = 3600  # 1 Hour in seconds


def get_schema_from_json():
    """Parses local database_schema.json into SQL DDL format."""
    try:
        if not os.path.exists(JSON_SCHEMA_PATH):
            return None

        with open(JSON_SCHEMA_PATH, 'r') as f:
            data = json.load(f)

        # Assumption: JSON structure is {"table_name": ["col1 type", "col2 type"]...}
        # Adjust parsing logic if your JSON structure is different
        schema_text = ""
        for table, cols in data.items():
            # Handle if cols are dicts or lists
            if isinstance(cols, list):
                col_str = ", ".join(cols)
            elif isinstance(cols, dict):
                col_str = ", ".join([f"{k} {v}" for k, v in cols.items()])
            else:
                col_str = str(cols)
            schema_text += f"CREATE TABLE {table} ({col_str});\n"
        return schema_text
    except Exception as e:
        print(f"⚠️ JSON Parse Error: {e}")
        return None


def get_database_schema():
    """
    1. Checks Cache
    2. Tries Live DB Fetch
    3. Fallback to JSON File
    4. Fallback to Hardcoded String
    """
    global SCHEMA_CACHE
    current_time = time.time()

    # 1. Return Cache if valid
    if SCHEMA_CACHE["text"] and (current_time - SCHEMA_CACHE["last_updated"] < CACHE_TTL):
        return SCHEMA_CACHE["text"]

    schema_prompt = ""

    # 2. Try Live DB Fetch
    try:
        print("🔄 Fetching fresh schema from DB...")
        with engine.connect() as conn:
            tables = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )).fetchall()

            for table in tables:
                t_name = table[0]
                columns = conn.execute(text(
                    f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t_name}'"
                )).fetchall()
                col_str = ", ".join([f"{c[0]} {c[1]}" for c in columns])
                schema_prompt += f"CREATE TABLE {t_name} ({col_str});\n"

        # Update Cache
        if schema_prompt:
            SCHEMA_CACHE["text"] = schema_prompt
            SCHEMA_CACHE["last_updated"] = current_time
            return schema_prompt

    except Exception as e:
        print(f"⚠️ Live Schema Fetch Failed: {e}")

    # 3. Fallback to JSON
    print("⚠️ Attempting JSON Fallback...")
    json_schema = get_schema_from_json()
    if json_schema:
        print("✅ Loaded Schema from JSON.")
        SCHEMA_CACHE["text"] = json_schema
        SCHEMA_CACHE["last_updated"] = current_time  # Cache the JSON version too
        return json_schema

    # 4. Ultimate Fallback
    print("❌ All Schema Sources Failed. Using Minimal Hardcoded Schema.")
    return "CREATE TABLE regions (state BIGINT, area_name TEXT);"


# --- MAIN ENDPOINT ---
@app.post("/generate-and-execute")
async def process_query(request: QueryRequest):
    start_time = time.time()

    # 1. Get Schema (Cached/Live/JSON)
    schema_context = get_database_schema()

    # 2. Call Inference Server
    generated_sql = ""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{INFERENCE_SERVER_URL}/generate",
                json={
                    "question": request.question,
                    "schema_context": schema_context
                },
                timeout=60.0
            )
            response.raise_for_status()
            generated_sql = response.json().get("sql")

    except Exception as e:
        log_metrics(request.question, "ERROR", (time.time() - start_time) * 1000, "llm_failure")
        raise HTTPException(status_code=500, detail=f"Inference Error: {e}")

    # 3. Clean SQL
    clean_sql = generated_sql.replace("```sql", "").replace("```", "").strip()
    if clean_sql.endswith(";"):
        clean_sql = clean_sql[:-1]

    # LOG GENERATION
    log_generation(request.question, clean_sql)

    # 4. Execute on Supabase
    query_results = []
    status = "success"
    error_message = None

    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(clean_sql), conn)
            df = df.where(pd.notnull(df), None)
            query_results = df.to_dict(orient='records')

    except Exception as e:
        status = "error"
        error_message = str(e)

    latency = (time.time() - start_time) * 1000

    # LOG METRICS
    log_metrics(request.question, clean_sql, latency, status)

    return {
        "question": request.question,
        "generated_sql": clean_sql,
        "results": query_results,
        "status": status,
        "error": error_message,
        "latency_ms": round(latency, 2)
    }


@app.get("/health")
@app.get("/", include_in_schema=False)
def health_check():
    return {
        "status": "online",
        "schema_cached": bool(SCHEMA_CACHE["text"]),
        "schema_last_updated": SCHEMA_CACHE["last_updated"],
        "schema": SCHEMA_CACHE["text"][:100] + "..." if SCHEMA_CACHE["text"] else None
    }

