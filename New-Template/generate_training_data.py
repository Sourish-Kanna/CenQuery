import json
import os
import re
import csv
import sys
from datetime import datetime

from sqlalchemy.sql import text
from sqlalchemy.dialects import postgresql

# ==================================================
# LOGGING
# ==================================================
class DualLogger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()


sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
sys.stderr.reconfigure(encoding="utf-8")  # type: ignore

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(
    LOG_DIR, f"cenquery_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)

sys.stdout = DualLogger(LOG_FILE)
sys.stderr = sys.stdout


# ==================================================
# CONFIG
# ==================================================
BASE_DATA_DIR = "data"

SCHEMA_FILE = "database_schema.json"
QUESTIONS_FILE = "question.txt"
SQL_FILE = "queries.sql"
OUTPUT_DIR = "training_data"

MAX_OPTIONAL_TABLES = 6

CORE_TABLES = {
    "regions",
    "tru",
    "languages",
    "religions",
    "age_groups",
}


# ==================================================
# CSV LOADERS
# ==================================================
def load_csv_keywords(filename, column):
    path = os.path.join(BASE_DATA_DIR, filename)
    out = set()
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            v = row[column].strip().lower()
            if v:
                out.add(v)
    return out


LANGUAGE_KEYWORDS = load_csv_keywords("languages.csv", "name")
RELIGION_KEYWORDS = load_csv_keywords("religions.csv", "religion_name")
AGE_GROUP_KEYWORDS = load_csv_keywords("age_groups.csv", "name")


# ==================================================
# INTENT DEFINITIONS (SINGLE SOURCE OF TRUTH)
# ==================================================
INTENTS = {
    "population": {
        "strong": {
            "population", "people", "persons", "count", "total",
            "live", "living"
        },
        "weak": {
            "most", "least", "largest", "smallest",
            "more", "less", "higher", "lower",
            "ratio", "gap", "difference", "percentage", "percent"
        }
    },

    "religion": {
        "strong": RELIGION_KEYWORDS | {
            "religion", "religious", "faith", "community"
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
            "education", "educated", "schooling"
        },
        "weak": {"rate"}
    },

    "occupation": {
        "strong": {
            "work", "working", "worker", "employment",
            "non-worker", "workforce", "participation"
        },
        "weak": set()
    },

    "health": {
        "strong": {
            "health", "mortality", "fertility",
            "disease", "anaemia", "diabetes"
        },
        "weak": set()
    },

    "age": {
        "strong": AGE_GROUP_KEYWORDS | {
            "age", "children", "elderly", "youth",
            "adult", "working age"
        },
        "weak": set()
    }
}


# ==================================================
# RULE GRAPH
# ==================================================
RULES = [
    {"intent": "religion",   "adds": {"religion_stats"}},
    {"intent": "language",   "adds": {"language_stats"}},
    {"intent": "population", "adds": {"population_stats"}},
    {"intent": "education",  "adds": {"education_stats"}, "requires": {"religion"}},
    {"intent": "occupation", "adds": {"occupation_stats"}, "requires": {"religion"}},
    {"intent": "health",     "adds": {"healthcare_stats"}, "requires": {"religion"}},
]


# ==================================================
# SCHEMA
# ==================================================
def load_schema(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ==================================================
# INTENT DETECTION (FIXED)
# ==================================================
def detect_intents(question: str):
    q = question.lower()
    active = set()

    # Strong first
    for intent, groups in INTENTS.items():
        if any(t in q for t in groups["strong"]):
            active.add(intent)

    # Weak only if something already active
    if active:
        for intent, groups in INTENTS.items():
            if any(t in q for t in groups["weak"]):
                active.add(intent)

    return active


def select_tables(question: str):
    intents = detect_intents(question.lower())
    tables = set(CORE_TABLES)

    for rule in RULES:
        if rule["intent"] not in intents:
            continue
        if "requires" in rule and not rule["requires"].issubset(intents):
            continue
        tables |= rule["adds"]

    optional = tables - CORE_TABLES
    if len(optional) > MAX_OPTIONAL_TABLES:
        optional = set(list(optional)[:MAX_OPTIONAL_TABLES])

    return CORE_TABLES | optional


# ==================================================
# SCHEMA BUILD
# ==================================================
def build_schema(schema_json, tables):
    ddl = []
    for t in sorted(tables):
        if t not in schema_json:
            continue
        cols = []
        for c in schema_json[t]["columns"]:
            d = f"{c['name']} {c['type']}"
            if "PK" in c.get("constraints", []):
                d += " PRIMARY KEY"
            cols.append(d)
        ddl.append(f"CREATE TABLE {t} ({', '.join(cols)});")
    return "\n".join(ddl)


# ==================================================
# SQL VALIDATION
# ==================================================
def validate_sql_syntax(sql):
    try:
        text(sql).compile(dialect=postgresql.dialect())
        return True, None
    except Exception as e:
        return False, str(e)


def used_tables(sql):
    found = set()
    for a, b in re.findall(r"\bFROM\s+(\w+)|\bJOIN\s+(\w+)", sql, re.I):
        if a: found.add(a)
        if b: found.add(b)
    return found
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
# ==================================================
def main():
    print("🤖 CENQUERY ROBUST GENERATOR (FINAL, FIXED)")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    member = input("Enter your name: ").strip().replace(" ", "_") or "Member"
    out_path = get_unique_filename(OUTPUT_DIR, f"train_{member}.jsonl")

    schema_json = load_schema(SCHEMA_FILE)
    questions = load_questions(QUESTIONS_FILE)
    sqls = load_sql_queries(SQL_FILE)

    assert len(questions) == len(sqls), "Question/SQL count mismatch"
    n= 1
    with open(out_path, "w", encoding="utf-8") as out:
        for q, s in zip(questions, sqls):
            ok, err = validate_sql_syntax(s)
            if not ok:
                raise ValueError(f"❌ Invalid SQL syntax:\n{s}\n{err}")

            tables = select_tables(q)
            print("-" * 60)
            print(f"🧠 Question {n}:")
            print(q)

            print("📊 Selected tables:")
            print(sorted(tables))
            missing = used_tables(s) - tables
            if missing:
                print("⚠️ Missing tables (selector issue):", missing)
            tables |= {t for t in missing if t in schema_json}

            schema = build_schema(schema_json, tables)

            out.write(json.dumps(format_entry(q, s, schema)))
            n+=1

    print(f"✅ Generated {len(questions)} samples")
    print(f"📂 Saved to {out_path}")
    print(f"🧾 Log: {LOG_FILE}")


if __name__ == "__main__":
    main()
