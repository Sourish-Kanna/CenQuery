import json
import os
import csv
import time
import re
import requests
import pandas as pd
import difflib  # <--- NEW: For Fuzzy Matching
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from typing import Any, Set
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration ---
load_dotenv()

GENERATION_LOG_FILE = "generation_log.csv"
LOG_FILE = "metrics_log.csv"
DATA_DIR = os.getenv("DATA_DIR", "data")  # Point this to where your CSVs are (optional)

# 1. Database & Service Config
DATABASE_URL = os.getenv("DB_CONNECTION_STRING", "")
LLM_ENGINE_URL = os.getenv("LLM_ENGINE_URL", "")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")
if not LLM_ENGINE_URL:
    raise ValueError("LLM_ENGINE_URL not set. Generation endpoint will fail if called.")

# --- Globals for Schema Caching ---
# We will cache the DB structure here so we don't inspect it on every request
FULL_SCHEMA_CACHE = {}
ALL_COLUMN_NAMES = set()  # Optimized set for fast lookup

# --- Config & keywords (Same as before) ---
MAX_OPTIONAL_TABLES = 6
CORE_TABLES = {"regions", "tru", "languages", "religions", "age_groups"}


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
    {"intent": "occupation", "adds": {"occupation_stats", "education_stats"}}, # "healthcare_stats"}},
    {"intent": "education", "adds": {"education_stats", "religion_stats"}}, #"healthcare_stats"}},
    {"intent": "agriculture", "adds": {"crop_stats"}},
]

app = FastAPI(title="CenQuery API (Self-Healing)", version="5.2.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

# --- Database Connection & Schema Caching ---
try:
    # 1. Establish DB Connection (Still needed for execution)
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("✅ Database connection successful.")

    # 2. Build Schema Cache from FILE (Not Database Inspection)
    print("⏳ Building Schema Cache from 'database_schema.json'...")
    
    # Ensure the path is correct relative to where you run the script
    schema_path = "database_schema.json" 
    
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at {schema_path}")

    with open(schema_path, "r") as f:
        file_schema = json.load(f)

    for table_name, details in file_schema.items():
        # JSON Structure: { "table": { "columns": [ {"name": "x", "type": "y"}, ... ] } }
        cols_list = []
        for col in details.get("columns", []):
            c_name = col["name"]
            c_type = col["type"]
            
            cols_list.append({"name": c_name, "type": c_type})
            
            # Add to global set for fuzzy matching
            ALL_COLUMN_NAMES.add(c_name)

        FULL_SCHEMA_CACHE[table_name] = {
            "columns": cols_list
        }

    print(f"✅ Schema Cache Built from file ({len(FULL_SCHEMA_CACHE)} tables)")

except Exception as e:
    print(f"❌ Initialization Error: {e}")


# --- Pydantic Models ---
class GenerateSQLRequest(BaseModel):
    question: str = Field(..., description="Natural language question.")

class GenerateSQLResponse(BaseModel):
    question: str
    sql_query: str
    schema_selected: str | None = None

class ExecuteSQLRequest(BaseModel):
    sql_query: str
    question: str | None = None

class ExecuteSQLResponse(BaseModel):
    sql_query: str
    result: Any
    question: str | None = None
    latency_ms: float
    status: str
    healed: bool = False  # Flag to show if we fixed it

# --- Logging ---
def log_generation(question: str, sql_query: str):
    try:
        with open(GENERATION_LOG_FILE, "a", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            if not os.path.isfile(GENERATION_LOG_FILE): writer.writerow(["question", "generated_sql_query", "schema_selected"])
            writer.writerow([question, sql_query, None])  # schema_selected is None for generation logs
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
    if "agriculture" in intents:
        print("🌾 Agriculture Intent Detected: Isolating crop_stats.")
        return {"crop_stats"}

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
            # Quote weird column names in the schema definition too, to help the LLM
            col_name = c['name']
            if "." in col_name or " " in col_name:
                col_name = f'"{col_name}"'
            cols.append(f"{col_name} {c['type']}")
        ddl.append(f"CREATE TABLE {t} ({', '.join(cols)});")
    return "\n".join(ddl)


def sanitize_dot_columns(sql_query: str) -> str:
    """Pre-execution fixer for unquoted dot columns."""
    pattern_alias = r'\b([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+\.[0-9]+)\b'
    return re.sub(pattern_alias, r'\1."\2"', sql_query)


def heal_sql_query(bad_sql: str, error_msg: str) -> str:
    """
    Parses DB error message, finds the closest valid column OR fixes quoted identifiers.
    """
    print(f"🚑 Attempting to heal SQL. Error: {error_msg}")

    # Regex to extract the missing column from PG error
    match = re.search(r'column "([^"]+)" does not exist', error_msg)
    if not match:
        match = re.search(r'column ([^ ]+) does not exist', error_msg)

    if match:
        bad_col = match.group(1)
        clean_bad_col = bad_col.split(".")[-1] # Remove table alias if present

        # STRATEGY 1: Fuzzy Match Column Name (Typo Fix)
        matches = difflib.get_close_matches(clean_bad_col, ALL_COLUMN_NAMES, n=1, cutoff=0.5)
        if matches:
            good_col = matches[0]
            print(f"🩹 Healing: Replaced '{clean_bad_col}' with '{good_col}'")
            replacement = f'"{good_col}"' if "." in good_col else good_col
            return bad_sql.replace(clean_bad_col, replacement)

        # STRATEGY 2: Literal vs Identifier Fix (The "Rice" Fix)
        # If the "missing column" starts with Uppercase or has spaces, it's likely a value.
        # Example: SELECT "Rice" -> SELECT 'Rice'
        if clean_bad_col and (clean_bad_col[0].isupper() or " " in clean_bad_col):
             print(f"🩹 Healing: Converting identifier \"{clean_bad_col}\" to string literal")
             # Replace double quotes with single quotes for this specific token
             return bad_sql.replace(f'"{clean_bad_col}"', f"'{clean_bad_col}'")

    return bad_sql


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
{schema_string}

### Instructions
- Output ONLY the SQL query.
- Use ILIKE for text comparisons.
- IMPORTANT: If a column name contains dots (e.g. col.1), you MUST enclose it in double quotes (e.g. "col.1").

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

        raw_sql = response.json().get("sql", "")
        sql_query = raw_sql.replace("```sql", "").replace("```", "").strip()
        if ";" in sql_query: sql_query = sql_query.split(";")[0] + ";"

        # Apply Regex Fixer
        sql_query = sanitize_dot_columns(sql_query)

        log_generation(question, sql_query)
        print(f"✅ Received SQL from Service A: {sql_query}")
        return GenerateSQLResponse(question=question, sql_query=sql_query, schema_selected=", ".join(sorted(relevant_tables)))

    except Exception as e:
        print(f"LLM Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def patch_broken_sql(sql_query: str) -> str:
    """
    Emergency patch function to fix common LLM hallucinations 
    before execution.
    """
    # 0. Safety Guard
    if len(sql_query) > 2000: return sql_query

    patched_sql = sql_query

    # --- FIX 0: Syntax Hallucinations (BIGINT) ---
    if "BIGINT" in patched_sql:
        patched_sql = patched_sql.replace(" BIGINT ", " ")
        patched_sql = patched_sql.replace("BIGINT ", " ")

    # --- FIX 1: Pluralization Errors ---
    replacements = {
        "illiterate_person ": "illiterate_persons ",
        "illiterate_person,": "illiterate_persons,",
        "illiterate_person)": "illiterate_persons)",
        "scheduled_castes_population_person": "scheduled_castes_person",
        "scheduled_tribes_population_person": "scheduled_tribes_person",
        "language_name": "name"
    }
    for bad, good in replacements.items():
        if bad in patched_sql:
            patched_sql = patched_sql.replace(bad, good)

    # --- FIX 2: Cross-Schema Hallucinations (Religion -> Education) ---
    if "education_stats" in patched_sql and "religion_stats" not in patched_sql:
        column_map = {
            "tot_p": "total_person",
            "p_lit": "literates_person",
            "p_ill": "illiterate_persons",
            "no_hh": "no_of_households",
            "tot_m": "total_male",
            "tot_f": "total_female",
            "p_06": "population_in_the_age_group_06_person"
        }
        for bad_col, good_col in column_map.items():
            patched_sql = patched_sql.replace(f".{bad_col}", f".{good_col}")
            patched_sql = patched_sql.replace(f" {bad_col}", f" {good_col}")
            patched_sql = patched_sql.replace(f",{bad_col}", f",{good_col}")

    # --- FIX 3: Agriculture Specifics (Crop Stats) ---
    if "crop_stats" in patched_sql:
        # Remove "state_name" filters (Hallucinated column)
        # Matches: AND state_name ILIKE '%...%'
        patched_sql = re.sub(r"\bAND\s+state_name\s+ILIKE\s+'[^']+'", "", patched_sql, flags=re.IGNORECASE)
        patched_sql = re.sub(r"\bWHERE\s+state_name\s+ILIKE\s+'[^']+'", "WHERE 1=1", patched_sql, flags=re.IGNORECASE)
        
        # Proactive "Rice" fix: SELECT "Rice" -> SELECT 'Rice'
        patched_sql = patched_sql.replace('SELECT "Rice"', "SELECT 'Rice'")

    # --- FIX 4: Broken Language Joins ---
    if "languages" in patched_sql and "language_stats" not in patched_sql:
        pattern_a = r"JOIN\s+languages\s+(\w+)\s+ON\s+(\w+)\.tru_id\s*=\s*\1\.tru_id"
        pattern_b = r"JOIN\s+languages\s+(\w+)\s+ON\s+(\w+)\.language_id\s*=\s*\1\.id"
        pattern_c = r"JOIN\s+languages\s+(\w+)\s+ON\s+(\w+)\.[\w]+\s*=\s*\1\.state"

        def bridge_replacer(match):
            l_alias = match.group(1)
            stats_alias = match.group(2)
            bridge_alias = f"ls_{l_alias}"
            
            join_condition = f"{stats_alias}.state = {bridge_alias}.state"
            if stats_alias != 'r': 
                 join_condition += f" AND {stats_alias}.tru_id = {bridge_alias}.tru_id"

            return (f"JOIN language_stats {bridge_alias} ON {join_condition} "
                    f"JOIN languages {l_alias} ON {bridge_alias}.language_id = {l_alias}.id")

        try:
            if ".tru_id" in patched_sql:
                patched_sql = re.sub(pattern_a, bridge_replacer, patched_sql, flags=re.IGNORECASE)
            if ".language_id" in patched_sql:
                patched_sql = re.sub(pattern_b, bridge_replacer, patched_sql, flags=re.IGNORECASE)
            if ".state" in patched_sql:
                patched_sql = re.sub(pattern_c, bridge_replacer, patched_sql, flags=re.IGNORECASE)
        except Exception as e:
            print(f"⚠️ Patch failed: {e}")

    return patched_sql


# --- API Endpoints ---
@app.post("/generate-select-sql", response_model=GenerateSQLResponse)
async def generate_select_sql(request: GenerateSQLRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Empty question.")
    print(f"Received question: {request.question}")
    return _call_remote_llm(request.question)


@app.post("/generate-other-sql", response_model=GenerateSQLResponse)
async def generate_other_sql(request: GenerateSQLRequest):
    # For DML/DDL, we might want to expose ALL tables or a different logic.
    # For now, we reuse the same logic, but you might want to force all tables.
    print(f"Received question: {request.question}")
    return _call_remote_llm(request.question)


@app.post("/execute-sql", response_model=ExecuteSQLResponse)
async def execute_sql(request: ExecuteSQLRequest):
    start_time = time.time()
    print(f"Executing SQL: {request.sql_query}\n")
    current_sql = sanitize_dot_columns(request.sql_query)
    # print(f"Sanitized SQL: {current_sql}\n")
    patched_sql = patch_broken_sql(current_sql)
    # print(f"Patched SQL: {patched_sql}\n")
    healed = False
    if patched_sql != current_sql:
        print(f"🩹 Applied SQL Patch: \nOld: {current_sql}\nNew: {patched_sql}\n")
        current_sql = patched_sql
        healed = True
    print(f"Final SQL to Execute: {current_sql}")
    status = "error"
    result = []
    
    # RETRY LOOP (Max 2 attempts: Original -> Healed)
    for attempt in range(2):
        try:
            with engine.connect() as connection:
                # Detect DML
                if any(k in current_sql.lower() for k in ["insert", "update", "delete", "create", "alter", "drop"]):
                     with connection.begin():
                        res = connection.execute(text(current_sql))
                        result = {"rows_affected": res.rowcount}
                else:
                    df = pd.read_sql_query(sql=text(current_sql), con=connection)
                    if len(df) > 1000: df = df.head(1000)
                    result = df.astype(object).where(pd.notnull(df), None).to_dict(orient='records')  # type: ignore
                
                status = "success"
                break # Success! Exit loop

        except Exception as e:
            error_str = str(e).lower()
            # Check if it's a "column not found" error, and we haven't tried healing yet
            if attempt == 0 and ("column" in error_str and "does not exist" in error_str):
                new_sql = heal_sql_query(current_sql, str(e))
                if new_sql != current_sql:
                    current_sql = new_sql
                    healed = True
                    continue # Retry with new SQL
            
            # If we get here, healing failed or wasn't applicable
            result = str(e)
            status = "error"
            break

    latency = (time.time() - start_time) * 1000
    print(f"Execution completed in {latency:.2f} ms with status: {status}")
    print(f"Result: {result}")
    
    log_metrics(request.question, current_sql, latency, status)

    return ExecuteSQLResponse(
        sql_query=current_sql, # Return the potentially healed SQL
        result=result,
        question=request.question,
        latency_ms=latency,
        status=status,
        healed=healed
    )


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "CenQuery Service B (Style 2 Enabled) is Online"}