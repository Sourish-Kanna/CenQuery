import json
import os
import re
import sys

# =========================
# CONFIG
# =========================
SCHEMA_FILE = "database_schema.json"
QUESTIONS_FILE = "questions.txt"
SQL_FILE = "queries.sql"
OUTPUT_DIR = "training_data"
MAX_TABLES = 6  # hard safety cap

# =========================
# LOAD FULL SCHEMA
# =========================
def load_schema(schema_path):
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# RULE-BASED TABLE SELECTOR
# =========================
def select_tables(question: str):
    q = question.lower()
    tables = set()

    # Geographic / scope
    if any(w in q for w in ["india", "state", "states", "region", "total"]):
        tables.update({"regions", "tru"})

    # Religion
    if any(w in q for w in ["religion", "hindu", "muslim", "christian", "sikh", "buddhist", "jain"]):
        tables.update({"religions", "religion_stats"})

    # Population
    if any(w in q for w in ["population", "people", "persons", "males", "females"]):
        tables.add("population_stats")

    # Literacy / education
    if any(w in q for w in ["literacy", "literate", "illiterate", "education", "school"]):
        tables.add("education_stats")
        if "religion" in q:
            tables.add("religion_stats")

    # Health
    if any(w in q for w in ["mortality", "fertility", "health", "vaccination", "anaemia", "diabetes"]):
        tables.add("healthcare_stats")

    # Occupation
    if any(w in q for w in ["occupation", "workers", "employment", "labour"]):
        tables.update({"occupation_stats", "age_groups"})

    # Language
    if any(w in q for w in ["language", "mother tongue", "spoken"]):
        tables.update({"languages", "language_stats"})

    # Agriculture
    if any(w in q for w in ["crop", "agriculture", "sown", "yield"]):
        tables.add("crop_stats")

    return set(list(tables)[:MAX_TABLES])

# =========================
# BUILD COMPRESSED SCHEMA
# =========================
def build_schema(schema_json, selected_tables):
    ddl = []

    for table in selected_tables:
        table_info = schema_json[table]
        columns = []

        for col in table_info["columns"]:
            col_def = f"{col['name']} {col['type']}"
            if "PK" in col.get("constraints", []):
                col_def += " PRIMARY KEY"
            columns.append(col_def)

        ddl.append(f"CREATE TABLE {table} ({', '.join(columns)});")

    return "\n".join(ddl)

# =========================
# LOAD QUESTIONS
# =========================
def load_questions(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# =========================
# LOAD SQL QUERIES
# =========================
def load_sql_queries(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    queries = []
    for q in content.split(";"):
        q = re.sub(r"\s+", " ", q.strip())
        if q:
            queries.append(q + ";")
    return queries

# =========================
# FORMAT TRAINING PROMPT
# =========================
def format_entry(question, sql, schema):
    return {
        "text": f"""### Task
Generate a SQL query to answer the following question:
`{question}`

### Database Schema
This query will run on a database whose schema is represented in this string:
{schema}

### SQL
{sql}"""
    }

# =========================
# MAIN
# =========================
def main():
    print("🚀 CENQUERY TRAINING DATA GENERATOR (Option A)")
    print("=" * 50)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    schema_json = load_schema(SCHEMA_FILE)
    questions = load_questions(QUESTIONS_FILE)
    sqls = load_sql_queries(SQL_FILE)

    if len(questions) != len(sqls):
        raise ValueError(f"Mismatch: {len(questions)} questions vs {len(sqls)} SQL queries")

    output_path = os.path.join(OUTPUT_DIR, "train.jsonl")

    with open(output_path, "w", encoding="utf-8") as out:
        for q, s in zip(questions, sqls):
            tables = select_tables(q)
            schema = build_schema(schema_json, tables)
            entry = format_entry(q, s, schema)
            out.write(json.dumps(entry) + "\n")

    print(f"✅ Generated {len(questions)} training samples")
    print(f"📂 Saved to: {output_path}")
    print("=" * 50)

if __name__ == "__main__":
    main()
