import os
import time
import re
import json
import requests
import pandas as pd
import difflib
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from typing import Set, Any, Dict
from constants import INTENTS, RULES

# --- Configuration ---
load_dotenv()

DATABASE_URL = os.getenv("DB_CONNECTION_STRING", "")
LLM_ENGINE_URL = os.getenv("LLM_ENGINE_URL", "")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")
if not LLM_ENGINE_URL:
    raise ValueError("LLM_ENGINE_URL not set. Generation endpoint will fail if called.")

# --- Globals for Schema Caching ---
FULL_SCHEMA_CACHE = {}
ALL_COLUMN_NAMES = set()

# --- Config & keywords ---
MAX_OPTIONAL_TABLES = 6
CORE_TABLES = {"regions", "tru", "languages", "religions", "age_groups"}

# --- Database Connection & Schema Caching ---
try:
    # UPDATED FOR SUPABASE: Added pooling parameters and pre-ping
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,          # Standard pool size
        max_overflow=20,       # Allow up to 20 extra connections during spikes
        pool_pre_ping=True,    # CRITICAL: Checks if the Supabase connection is still alive before querying
        pool_recycle=1800      # Recycles connections every 30 minutes to prevent timeouts
    )
    
    with engine.connect() as connection:
        print("✅ Supabase database connection successful.")

    # 2. Build Schema Cache from FILE (Not Database Inspection)
    print("⏳ Building Schema Cache from 'database_schema.json'...")
    
    # Ensure the path is correct relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(script_dir, "database_schema.json")
    
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

        FULL_SCHEMA_CACHE[table_name] = {"columns": cols_list}

    print(f"✅ Schema Cache Built from file ({len(FULL_SCHEMA_CACHE)} tables)")
except Exception as e:
    print(f"❌ Initialization Error: {e}")

# --- Logic Functions ---
def detect_intents(question: str) -> Set[str]:
    q = question.lower()
    active = set()

    # NEW: Specific Worker/Cultivator Mapping
    worker_keywords = ["cultivator", "labourer", "worker", "household industry", "marginal", "main"]
    if any(k in q for k in worker_keywords):
        active.add("occupation")
        
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
    q = question.lower()

    # FIX: Stop 'population' table hallucination for Agriculture
    if "agriculture" in intents and "labourer" not in q:
        return {"crop_stats", "regions"}

    tables = set(CORE_TABLES)

    # FIX: Priority Routing
    # If it's about workers, Force occupation_stats and DROP education_stats to avoid EM mismatch
    if "occupation" in intents:
        tables.add("occupation_stats")
        if "literacy" not in q and "education" not in q:
            # Remove education_stats if it's strictly a worker query
            tables.discard("education_stats")

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
             return bad_sql.replace(f'"{clean_bad_col}"', f"'{clean_bad_col}'")
    return bad_sql

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
        patched_sql = patched_sql.replace(" BIGINT ", " ").replace("BIGINT ", " ")

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
            "tot_p": "total_person", "p_lit": "literates_person", "p_ill": "illiterate_persons",
            "no_hh": "no_of_households", "tot_m": "total_male", "tot_f": "total_female",
            "p_06": "population_in_the_age_group_06_person"
        }
        for bad_col, good_col in column_map.items():
            patched_sql = patched_sql.replace(f".{bad_col}", f".{good_col}").replace(f" {bad_col}", f" {good_col}").replace(f",{bad_col}", f",{good_col}")

    # --- FIX 3: Agriculture Specifics (Crop Stats) ---
    if "crop_stats" in patched_sql:
        patched_sql = re.sub(r"\bAND\s+state_name\s+ILIKE\s+'[^']+'", "", patched_sql, flags=re.IGNORECASE)
        patched_sql = re.sub(r"\bWHERE\s+state_name\s+ILIKE\s+'[^']+'", "WHERE 1=1", patched_sql, flags=re.IGNORECASE)
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
            if ".tru_id" in patched_sql: patched_sql = re.sub(pattern_a, bridge_replacer, patched_sql, flags=re.IGNORECASE)
            if ".language_id" in patched_sql: patched_sql = re.sub(pattern_b, bridge_replacer, patched_sql, flags=re.IGNORECASE)
            if ".state" in patched_sql: patched_sql = re.sub(pattern_c, bridge_replacer, patched_sql, flags=re.IGNORECASE)
        except Exception as e:
            print(f"⚠️ Patch failed: {e}")

    return patched_sql



# --- Public Exported Functions ---
def generate_sql(question: str, use_adapter: bool = True) -> Dict[str, Any]:
    relevant_tables = select_tables(question)
    schema_string = build_schema_ddl(relevant_tables)
    if not schema_string:
        raise ValueError("Schema generation failed.")

    formatted_prompt = f"""### Task
Generate a SQL query to answer the following question:
`{question}`

### Database Schema
{schema_string}

### Instructions
- Output ONLY the SQL query.
- Use ILIKE for text comparisons.
- NEVER use hardcoded IDs (e.g., state=10). Always JOIN with 'regions' and filter by 'area_name'.
- Do NOT use SUM() or aggregates unless the question asks for "total", "sum", or "percentage".
- If the column name contains dots (e.g. col.1), use double quotes (e.g. "col.1").

### SQL
"""

    # Route to the correct vLLM / HuggingFace endpoint based on benchmarking needs
    base_url = LLM_ENGINE_URL.rstrip("/")
    endpoint_path = "/generate/adapter" if use_adapter else "/generate/base"
    endpoint = f"{base_url}{endpoint_path}"
    
    model_type = "adapter" if use_adapter else "base"
    print(f"⏳ Sending to {model_type} endpoint: {endpoint} (Tables: {len(relevant_tables)})")

    response = requests.post(endpoint, json={"prompt": formatted_prompt}, timeout=120)
    response.raise_for_status()

    raw_sql = response.json().get("sql", "")
    sql_query = raw_sql.replace("```sql", "").replace("```", "").strip()
    if ";" in sql_query: sql_query = sql_query.split(";")[0] + ";"

    # Standard sanitization for base string formatting
    sql_query = sanitize_dot_columns(sql_query)
    print(f"✅ Received SQL from Service A: {sql_query}")
    
    return {
        "question": question, 
        "sql_query": sql_query, 
        "schema_selected": ", ".join(sorted(relevant_tables)),
        "model_type": model_type
    }

def execute_bare(sql_query: str, question: str | None = None) -> Dict[str, Any]:
    """
    Bare execution for exact-match benchmarking. 
    NO sanitization, NO patching, NO error healing.
    """
    start_time = time.time()
    status = "error"
    result = []
    
    try:
        with engine.connect() as connection:
            if any(k in sql_query.lower() for k in ["insert", "update", "delete", "create", "alter", "drop"]):
                 with connection.begin():
                    res = connection.execute(text(sql_query))
                    result = {"rows_affected": res.rowcount}
            else:
                df = pd.read_sql_query(sql=text(sql_query), con=connection)
                if len(df) > 1000: df = df.head(1000)
                result = df.astype(object).where(pd.notnull(df), None).to_dict(orient='records') #type: ignore
            status = "success"
    except Exception as e:
        result = str(e)
        status = "error"

    latency = (time.time() - start_time) * 1000

    return {
        "sql_query": sql_query,
        "result": result,
        "question": question,
        "latency_ms": latency,
        "status": status,
        "healed": False
    }

def execute_and_heal(sql_query: str, question: str | None = None) -> Dict[str, Any]:
    """
    Production execution with full robust patching and error-loop healing.
    """
    start_time = time.time()
    current_sql = sanitize_dot_columns(sql_query)
    patched_sql = patch_broken_sql(current_sql)
    healed = False
    
    if patched_sql != current_sql:
        print(f"🩹 Applied SQL Patch: \nOld: {current_sql}\nNew: {patched_sql}\n")
        current_sql = patched_sql
        healed = True
        
    status = "error"
    result = []
    
    for attempt in range(2):
        try:
            with engine.connect() as connection:
                if any(k in current_sql.lower() for k in ["insert", "update", "delete", "create", "alter", "drop"]):
                     with connection.begin():
                        res = connection.execute(text(current_sql))
                        result = {"rows_affected": res.rowcount}
                else:
                    df = pd.read_sql_query(sql=text(current_sql), con=connection)
                    if len(df) > 1000: df = df.head(1000)
                    result = df.astype(object).where(pd.notnull(df), None).to_dict(orient='records') #type: ignore
                status = "success"
                break
        except Exception as e:
            error_str = str(e).lower()
            if attempt == 0 and ("column" in error_str and "does not exist" in error_str):
                new_sql = heal_sql_query(current_sql, str(e))
                if new_sql != current_sql:
                    current_sql = new_sql
                    healed = True
                    continue
            result = str(e)
            status = "error"
            break

    latency = (time.time() - start_time) * 1000

    return {
        "sql_query": current_sql,
        "result": result,
        "question": question,
        "latency_ms": latency,
        "status": status,
        "healed": healed
    }