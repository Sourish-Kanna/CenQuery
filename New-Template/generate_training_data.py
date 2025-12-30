import json
import os
import re
import csv

from sqlalchemy.sql import text
from sqlalchemy.dialects import postgresql

# =========================
# CONFIG
# =========================
BASE_DATA_DIR = "data"  # <---- COMMON BASE FOLDER

SCHEMA_FILE = "database_schema.json"
QUESTIONS_FILE = "maharajan_questions.txt"
SQL_FILE = "maharajan_queries.sql"
OUTPUT_DIR = "training_data"
MAX_OPTIONAL_TABLES = 6  # only for NON-core tables

# =========================
# CORE TABLES (ALWAYS INCLUDED)
# =========================
CORE_TABLES = {
    "regions",
    "tru",
    "languages",
    "religions",
    "age_groups",
}

# =========================
# CSV KEYWORD LOADER
# =========================
def load_csv_keywords(filename, column):
    path = os.path.join(BASE_DATA_DIR, filename)
    keywords = set()
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = row[column].strip().lower()
            if val:
                keywords.add(val)
    return keywords

# =========================
# LOAD KEYWORDS FROM CSVs
# =========================
LANGUAGE_KEYWORDS = load_csv_keywords("languages.csv", "name")
REGION_KEYWORDS   = load_csv_keywords("regions.csv", "area_name")
RELIGION_KEYWORDS = load_csv_keywords("religions.csv", "religion_name")
TRU_KEYWORDS      = load_csv_keywords("tru.csv", "name")
AGE_GROUP_KEYWORDS = load_csv_keywords("age_groups.csv", "name")

AGE_GROUP_ALIASES = {
    "children", "child", "kids",
    "adults", "elderly", "women", "men", "youth"
}

RELIGION_ALIASES = {
    "parsi", "parsis", "zoroastrian", "zoroastrians",
    "jew", "jews", "jewish",
    "bahai", "baháʼí"
}

IMPLICIT_POPULATION_TERMS = {
    "men", "women", "male", "female",
    "children", "child", "elderly", "youth", "teenagers",
    "urban", "rural", "village", "city",
    "ratio", "gap", "difference", "percentage",
    "most", "least", "largest", "smallest",
    "more", "less", "higher", "lower",
    "twice", "double", "triple"
}

# =========================
# IMPLICIT INTENT KEYWORDS
# =========================

IMPLICIT_POPULATION_TERMS = {
    "men", "women", "male", "female",
    "children", "child", "elderly", "youth", "teenagers",
    "urban", "rural", "village", "villages", "city", "cities",
    "ratio", "gap", "difference", "percentage", "percent",
    "most", "least", "largest", "smallest",
    "more", "less", "higher", "lower",
    "twice", "double", "triple",
    "population", "people", "persons", "count", "total", "live", "living"
}

IMPLICIT_RELIGION_TERMS = {
    "religion", "religious", "community", "faith",
    "hindu", "muslim", "christian", "sikh", "buddhist", "jain",
    "parsi", "zoroastrian"
}

IMPLICIT_LANGUAGE_TERMS = {
    "language", "languages", "spoken", "speakers",
    "mother tongue", "linguistic"
}

IMPLICIT_EDUCATION_TERMS = {
    "literacy", "literate", "illiterate",
    "education", "educated", "schooling",
    "literacy rate", "education level"
}

IMPLICIT_OCCUPATION_TERMS = {
    "work", "working", "worker", "workers",
    "employment", "employed", "unemployed",
    "non-worker", "non workers",
    "workforce", "participation"
}

IMPLICIT_HEALTH_TERMS = {
    "health", "mortality", "death", "deaths",
    "fertility", "birth", "births",
    "vaccination", "anaemia", "diabetes",
    "nutrition", "disease", "illness"
}

IMPLICIT_AGE_TERMS = {
    "age", "aged",
    "children", "child", "0-6",
    "teen", "teenagers",
    "youth",
    "adult", "adults",
    "elderly", "senior", "old age",
    "working age"
}


RULES = [
    {
        "name": "religion",
        "trigger": lambda q: (
            any(r in q for r in RELIGION_KEYWORDS)
            or any(w in q for w in IMPLICIT_RELIGION_TERMS)
        ),
        "adds": {"religion_stats"},
    },

    {
        "name": "language",
        "trigger": lambda q: (
            any(l in q for l in LANGUAGE_KEYWORDS)
            or any(w in q for w in IMPLICIT_LANGUAGE_TERMS)
        ),
        "adds": {"language_stats"},
    },

    {
        "name": "population",
        "trigger": lambda q: any(w in q for w in IMPLICIT_POPULATION_TERMS),
        "adds": {"population_stats"},
    },

    {
        "name": "education",
        "trigger": lambda q: any(w in q for w in IMPLICIT_EDUCATION_TERMS),
        "adds": {"education_stats"},
        "depends_on": {
            "religion": {"religion_stats"},
        },
    },

    {
        "name": "occupation",
        "trigger": lambda q: any(w in q for w in IMPLICIT_OCCUPATION_TERMS),
        "adds": {"occupation_stats"},
        "depends_on": {
            "religion": {"religion_stats"},
        },
    },

    {
        "name": "health",
        "trigger": lambda q: any(w in q for w in IMPLICIT_HEALTH_TERMS),
        "adds": {"healthcare_stats"},
        "depends_on": {
            "religion": {"religion_stats"},
        },
    },

    {
        "name": "age",
        "trigger": lambda q: (
            any(a in q for a in AGE_GROUP_KEYWORDS)
            or any(w in q for w in IMPLICIT_AGE_TERMS)
        ),
        "adds": {"age_groups"},
    },
]

# =========================
# LOAD FULL SCHEMA
# =========================
def load_schema(schema_path):
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# RULE GRAPH
# =========================
def select_tables(question: str):
    q = question.lower()
    tables = set(CORE_TABLES)

    active_rules = set()

    # Pass 1: activate rules
    for rule in RULES:
        if rule["trigger"](q):
            tables.update(rule["adds"])
            active_rules.add(rule["name"])

    # Pass 2: resolve dependencies
    for rule in RULES:
        if rule["name"] in active_rules and "depends_on" in rule:
            for dep_name, dep_tables in rule["depends_on"].items():
                if dep_name in active_rules:
                    tables.update(dep_tables)

    # Cap only optional tables
    optional = tables - CORE_TABLES
    if len(optional) > MAX_OPTIONAL_TABLES:
        optional = set(list(optional)[:MAX_OPTIONAL_TABLES])

    return CORE_TABLES.union(optional)

# =========================
# BUILD FULL SCHEMA (ALL COLUMNS)
# =========================
def build_schema(schema_json, selected_tables):
    ddl = []

    for table in selected_tables:
        if table not in schema_json:
            continue

        cols = []
        for col in schema_json[table]["columns"]:
            col_def = f"{col['name']} {col['type']}"
            if "PK" in col.get("constraints", []):
                col_def += " PRIMARY KEY"
            cols.append(col_def)

        ddl.append(f"CREATE TABLE {table} ({', '.join(cols)});")

    return "\n".join(sorted(ddl))

# =========================
# SQL TABLE USAGE CHECK
# =========================
def validate_sql_tables(sql, selected_tables):
    used = set()
    matches = re.findall(r"\bFROM\s+(\w+)|\bJOIN\s+(\w+)", sql, re.IGNORECASE)
    for a, b in matches:
        if a: used.add(a)
        if b: used.add(b)
    return used - selected_tables

# =========================
# SQL SYNTAX VALIDATION
# =========================
def validate_sql_syntax(sql):
    try:
        stmt = text(sql)
        stmt.compile(dialect=postgresql.dialect())
        return True, None
    except Exception as e:
        return False, str(e)

# =========================
# LOAD QUESTIONS / SQL
# =========================
def load_questions(path):
    with open(path, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

# =========================
# LOAD SQL QUERIES
# =========================
def load_sql_queries(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return [q.strip() + ";" for q in content.split(";") if q.strip()]

# =========================
# FORMAT TRAINING ENTRY
# =========================
def format_entry(question, sql, schema):
    return {"text": f"""### Task
Generate a SQL query to answer the following question:
`{question}`

### Database Schema
This query will run on a database whose schema is represented in this string:
{schema}

### SQL
{sql}"""
    }

# =========================
# UNIQUE OUTPUT FILE
# =========================
def get_unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    i = 1
    out = filename
    while os.path.exists(os.path.join(directory, out)):
        out = f"{base}({i}){ext}"
        i += 1
    return os.path.join(directory, out)

# =========================
# MAIN
# =========================
def main():
    print("==================================================")
    print("🤖 CENQUERY ROBUST GENERATOR (CSV + SQL SAFE)")
    print("==================================================")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    member = input("Enter your name (e.g., Member3): ").strip().replace(" ", "_") or "Member_Unknown"
    output_path = get_unique_filename(OUTPUT_DIR, f"train_{member}.jsonl")

    schema_json = load_schema(SCHEMA_FILE)
    questions = load_questions(QUESTIONS_FILE)
    sqls = load_sql_queries(SQL_FILE)

    if len(questions) != len(sqls):
        raise ValueError(f"Mismatch: {len(questions)} questions vs {len(sqls)} SQL queries")

    with open(output_path, "w", encoding="utf-8") as out:
        for q, s in zip(questions, sqls):

            ok, err = validate_sql_syntax(s)
            if not ok:
                raise ValueError(f"❌ Invalid SQL syntax:\n{s}\n{err}")

            tables = select_tables(q)
            print("Q:", q)
            print("Tables:", tables)

            schema = build_schema(schema_json, tables)

            missing = validate_sql_tables(s, tables)
            if missing:
                print("⚠️ Auto-fixing missing tables:", missing)
                tables = tables.union(missing)
                schema = build_schema(schema_json, tables)

            out.write(json.dumps(format_entry(q, s, schema)) + "\n")

    print(f"✅ Generated {len(questions)} verified samples")
    print(f"📂 Saved to: {output_path}")
    print("=" * 50)

if __name__ == "__main__":
    main()
