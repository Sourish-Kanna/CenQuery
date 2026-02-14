import os
import csv
import time
import json
import re
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
from typing import List, Dict, Any, Union, Set
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration ---
load_dotenv()

GENERATION_LOG_FILE = "generation_log.csv"
LOG_FILE = "metrics_log.csv"
DATA_DIR = os.getenv("DATA_DIR", "data")  # Point this to where your CSVs are (optional)

# 1. Database & Service Config
DATABASE_URL = os.getenv("DATABASE_URL", "")
LLM_ENGINE_URL = os.getenv("LLM_ENGINE_URL", "")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

# --- Globals for Schema Caching ---
# We will cache the DB structure here so we don't inspect it on every request
FULL_SCHEMA_CACHE = {}

# --- Intent & Table Config (From your script) ---
MAX_OPTIONAL_TABLES = 6
CORE_TABLES = {
    "regions",
    "tru",
    "languages",
    "religions",
    "age_groups",
}


# Load keywords helper (Safe version)
def load_csv_keywords(filename, column):
    path = os.path.join(DATA_DIR, filename)
    out = set()
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    v = row.get(column, "").strip().lower()
                    if v: out.add(v)
            print(f"✅ Loaded {len(out)} keywords from {filename}")
        except Exception as e:
            print(f"⚠️ Could not load {filename}: {e}")
    return out


# Initialize Keywords (Empty by default, populates if files exist)
LANGUAGE_KEYWORDS = load_csv_keywords("languages.csv", "name")
RELIGION_KEYWORDS = load_csv_keywords("religions.csv", "religion_name")
AGE_GROUP_KEYWORDS = load_csv_keywords("age_groups.csv", "name")

INTENTS = {
    "population": {
        "strong": {
            "population", "people", "persons", "count", "total",
            "live", "living", "men", "women", "male", "female",
            "boys", "girls", "sex ratio", "gender", "households",
            "dwellers", "villagers", "citizens", "residents"
        },
        "weak": {
            "most", "least", "largest", "smallest", "fewest",
            "more", "less", "higher", "lower",
            "ratio", "gap", "difference", "percentage", "percent"
        }
    },
    "religion": {
        "strong": RELIGION_KEYWORDS | {
            "religion", "religious", "faith", "community",
            "parsi", "parsis", "zoroastrian", "zoroastrians"
        },
        "weak": set()
    },
    "language": {
        "strong": LANGUAGE_KEYWORDS | {
            "language", "languages", "spoken", "speakers", "mother tongue"
        },
        "weak": set()
    },
    "education": {
        "strong": {
            "literacy", "literate", "illiterate",
            "education", "educated", "schooling", "school",
            "university", "college", "degree", "diploma", "pre-primary"
        },
        "weak": {"rate"}
    },
    "occupation": {
        "strong": {
            "work", "working", "worker", "employment",
            "non-worker", "workforce", "participation",
            "job", "jobs", "employed", "unemployed", "cultivator",
            "labourer", "agricultural", "paid", "cash",
            "marginal", "main", "industry", "industries", "engaged"
        },
        "weak": set()
    },
    "health": {
        "strong": {
            "health", "mortality", "fertility", "disease", "anaemia", "diabetes",
            "vaccinated", "vaccination", "vaccine", "vaccines",
            "stunting", "stunted", "wasting", "wasted",
            "underweight", "overweight", "obese", "obesity", "bmi",
            "birth", "births", "delivery", "deliveries", "antenatal", "postnatal",
            "breastfed", "breastfeeding", "diet", "nutrition",
            "blood sugar", "blood pressure", "hypertension",
            "hygienic", "menstruation", "sanitation", "clean fuel", "cooking fuel",
            "electricity", "drinking water", "water", "toilet",
            "internet", "bank account", "mobile phone", "insurance",
            "violence", "crime", "tobacco", "alcohol", "smoking",
            "fever", "ari", "diarrhoea", "treatment", "advice",
            "vitamin", "iodized", "salt", "cancer", "screening", "c-section",
            "hiv", "aids", "condom", "knowledge",
            "anaemic", "pregnant", "pregnancy", "married", "marriage",
            "waist", "hip", "folic", "acid", "decision", "owning", "house", "land",
            "registered", "registration", "authority"
        },
        "weak": set()
    },
    "age": {
        "strong": AGE_GROUP_KEYWORDS | {
            "age", "children", "elderly", "youth",
            "adult", "adults", "working age", "teenagers", "seniors",
            "0-6", "15-49", "60+"
        },
        "weak": set()
    },
    "agriculture": {
        "strong": {
            "agriculture", "agricultural", "crop", "crops", "farming",
            "sown", "sowing", "harvest", "harvesting", "yield", "production",
            "area", "dafw", "hectare", "hectares", "tonnes", "metric",
            "rice", "wheat", "maize", "jute", "sugarcane", "cotton",
            "oilseeds", "pulses", "cereals", "millet", "millets",
            "foodgrains", "nutri", "soybean", "barley", "groundnut",
            "ragi", "jowar", "bajra", "tur", "gram", "lentil"
        },
        "weak": {"normal", "season", "growth"}
    },
}

RULES = [
    {"intent": "religion", "adds": {"religion_stats"}},
    {"intent": "language", "adds": {"language_stats"}},
    {"intent": "population", "adds": {"population_stats"}},
    {"intent": "health", "adds": {"healthcare_stats"}},
    {"intent": "age", "adds": {"population_stats"}},
    {"intent": "occupation", "adds": {"occupation_stats", "healthcare_stats", "education_stats"}},
    {"intent": "education", "adds": {"education_stats", "religion_stats", "healthcare_stats"}},
    {"intent": "agriculture", "adds": {"crop_stats"}},
]

# --- FastAPI App ---
app = FastAPI(title="CenQuery API (Service B)", version="5.0.0")

origins = ["http://localhost", "http://localhost:3000", "https://cenquery-frontend.onrender.com"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

# --- Database Connection & Caching ---
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("✅ Database connection successful.")

        # --- BUILD SCHEMA CACHE ON STARTUP ---
        print("⏳ Building Schema Cache...")
        inspector = inspect(engine)
        table_names = inspector.get_table_names(schema='public')
        for table in table_names:
            cols = inspector.get_columns(table, schema='public')
            # Store in format compatible with your build_schema logic
            FULL_SCHEMA_CACHE[table] = {
                "columns": [{"name": c["name"], "type": str(c["type"])} for c in cols]
                # You can add constraints here if needed, but simple types usually suffice
            }
        print(f"✅ Schema Cache Built ({len(FULL_SCHEMA_CACHE)} tables)")

except Exception as e:
    print(f"❌ DB Error: {e}")


# --- Pydantic Models ---
class GenerateSQLRequest(BaseModel):
    question: str = Field(..., description="The natural language instruction.")


class GenerateSQLResponse(BaseModel):
    question: str
    sql_query: str


class ExecuteSQLRequest(BaseModel):
    sql_query: str
    question: str | None = None


class ExecuteSQLResponse(BaseModel):
    sql_query: str
    result: Union[List[Dict[str, Any]], Dict[str, int], str]
    latency_ms: float
    status: str


# --- Logging ---
def log_generation(question: str, sql_query: str):
    try:
        with open(GENERATION_LOG_FILE, "a", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            if not os.path.isfile(GENERATION_LOG_FILE): writer.writerow(["question", "generated_sql_query"])
            writer.writerow([question, sql_query])
    except:
        pass


def log_metrics(question, sql, latency, status):
    try:
        with open(LOG_FILE, "a", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            if not os.path.isfile(LOG_FILE): writer.writerow(["question", "sql_query", "latency_ms", "status"])
            writer.writerow([question or "N/A", sql, latency, status])
    except:
        pass


# --- Logic: Intent Detection & Schema Building ---
def detect_intents(question: str) -> Set[str]:
    q = question.lower()
    active = set()
    # Strong
    for intent, groups in INTENTS.items():
        if any(t in q for t in groups["strong"]):
            active.add(intent)
    # Weak
    if active:
        for intent, groups in INTENTS.items():
            if any(t in q for t in groups["weak"]):
                active.add(intent)
    return active


def select_tables(question: str) -> Set[str]:
    intents = detect_intents(question)
    tables = set(CORE_TABLES)

    for rule in RULES:
        if rule["intent"] not in intents: continue
        tables |= rule["adds"]

    optional = tables - CORE_TABLES
    if len(optional) > MAX_OPTIONAL_TABLES:
        optional = set(list(optional)[:MAX_OPTIONAL_TABLES])

    return CORE_TABLES | optional


def build_schema_ddl(selected_tables: Set[str]) -> str:
    ddl = []
    for t in sorted(selected_tables):
        if t not in FULL_SCHEMA_CACHE: continue
        cols = []
        for c in FULL_SCHEMA_CACHE[t]["columns"]:
            cols.append(f"{c['name']} {c['type']}")
        ddl.append(f"CREATE TABLE {t} ({', '.join(cols)});")
    return "\n".join(ddl)


def _call_remote_llm(question: str) -> GenerateSQLResponse:
    # 1. Select Tables based on Question
    relevant_tables = select_tables(question)

    # 2. Build DDL (Schema String)
    schema_string = build_schema_ddl(relevant_tables)
    if not schema_string:
        # Fallback if cache is empty or no tables selected
        raise HTTPException(status_code=500, detail="Schema generation failed.")

    # 3. Format Prompt (Style 2)
    # NOTE: We do NOT include the "### SQL" answer part, just the header.
    formatted_prompt = f"""### Task
Generate a SQL query to answer the following question:
`{question}`

### Database Schema
This query will run on a database whose schema is represented in this string:
{schema_string}

### SQL
"""

    if not LLM_ENGINE_URL:
        raise HTTPException(status_code=503, detail="LLM Engine URL not configured.")

    try:
        endpoint = f"{LLM_ENGINE_URL}/generate" if not LLM_ENGINE_URL.endswith("/generate") else LLM_ENGINE_URL
        print(f"⏳ Sending to Service A... (Tables: {len(relevant_tables)})")

        response = requests.post(
            endpoint,
            json={"prompt": formatted_prompt},
            timeout=60
        )
        response.raise_for_status()

        # 4. Clean SQL
        raw_sql = response.json().get("sql", "")
        # Remove Markdown and trailing artifacts
        sql_query = raw_sql.replace("```sql", "").replace("```", "").strip()
        # Stop at first semicolon if multiple are generated
        if ";" in sql_query:
            sql_query = sql_query.split(";")[0] + ";"

        log_generation(question, sql_query)
        return GenerateSQLResponse(question=question, sql_query=sql_query)

    except Exception as e:
        print(f"LLM Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- API Endpoints ---
@app.post("/generate-select-sql", response_model=GenerateSQLResponse)
async def generate_select_sql(request: GenerateSQLRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Empty question.")
    return _call_remote_llm(request.question)


@app.post("/generate-other-sql", response_model=GenerateSQLResponse)
async def generate_other_sql(request: GenerateSQLRequest):
    # For DML/DDL, we might want to expose ALL tables or a different logic.
    # For now, we reuse the same logic but you might want to force all tables.
    return _call_remote_llm(request.question)


@app.post("/execute-sql", response_model=ExecuteSQLResponse)
async def execute_sql(request: ExecuteSQLRequest):
    start_time = time.time()
    try:
        with engine.connect() as connection:
            q_lower = request.sql_query.lower()
            if any(k in q_lower for k in ["insert", "update", "delete", "create", "alter", "drop"]):
                with connection.begin():
                    result_proxy = connection.execute(text(request.sql_query))
                    result = {"rows_affected": result_proxy.rowcount}
            else:
                df = pd.read_sql_query(sql=text(request.sql_query), con=connection)
                if len(df) > 1000: df = df.head(1000)
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
    return {"message": "CenQuery Service B (Style 2 Enabled) is Online"}