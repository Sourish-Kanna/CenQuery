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
QUESTIONS_FILE = "question_eval.txt"
SQL_FILE = "queries_eval.sql"
OUTPUT_DIR = "eval_data"

MAX_OPTIONAL_TABLES = 6

# These tables are ALWAYS included
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
# INTENT DEFINITIONS (FINAL_V4)
# ==================================================
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
            # FIX: Added keywords for Q446 "household industries (Marginal)"
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
            # General Agricultural Terms
            "agriculture", "agricultural", "crop", "crops", "farming",
            "sown", "sowing", "harvest", "harvesting", "yield", "production",
            "area", "dafw", "hectare", "hectares", "tonnes", "metric",

            # Specific Crop Names (from your logs and common Indian crops)
            "rice", "wheat", "maize", "jute", "sugarcane", "cotton",
            "oilseeds", "pulses", "cereals", "millet", "millets",
            "foodgrains", "nutri", "soybean", "barley", "groundnut",
            "ragi", "jowar", "bajra", "tur", "gram", "lentil"
        },
        "weak": {
            "normal", "season", "growth"
        }
    },
}

# ==================================================
# RULE GRAPH (FINAL)
# ==================================================
RULES = [
    # Basic mappings
    {"intent": "religion",   "adds": {"religion_stats"}},
    {"intent": "language",   "adds": {"language_stats"}},
    {"intent": "population", "adds": {"population_stats"}},
    {"intent": "health",     "adds": {"healthcare_stats"}},
    
    # Age questions often need population counts
    {"intent": "age",        "adds": {"population_stats"}},

    # FIX: Occupation queries need all three stats tables to handle complex joins
    {"intent": "occupation", "adds": {"occupation_stats", "healthcare_stats", "education_stats"}},
    
    # Education data is spread across multiple tables
    {"intent": "education",  "adds": {"education_stats", "religion_stats", "healthcare_stats"}},

    # Agriculture / Crop Production
    {"intent": "agriculture", "adds": {"crop_stats"}},
]


# ==================================================
# SCHEMA
# ==================================================
def load_schema(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ==================================================
# INTENT DETECTION
# ==================================================
def detect_intents(question: str):
    q = question.lower()
    active = set()

    # Strong first
    for intent, groups in INTENTS.items():
        # Using regex \b for word boundaries prevents partial matches
        if any(re.search(r'\b' + re.escape(t) + r'\b', q) for t in groups["strong"]):
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
    return {
        "question": question,
        "sql": sql,
        "instruction": "Generate a SQL query to answer the following question and only based on given schema and don't invent new column names.",
        "schema": schema,
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
    print("🤖 CENQUERY ROBUST GENERATOR (FINAL_V4)")
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
            
            # Helper to check for missing real tables (ignores CTEs)
            missing = used_tables(s) - tables
            real_missing = {t for t in missing if t in schema_json}
            
            if real_missing:
                print("-" * 60)
                print(f"🧠 Question {n}:")
                print(q)
                print("📊 Selected tables:", sorted(tables))
                print("⚠️ Missing tables:", real_missing)
            
            # Auto-fix for output generation
            tables |= real_missing

            schema = build_schema(schema_json, tables)
            out.write(json.dumps(format_entry(q, s, schema)) + "\n")
            n+=1

    print(f"✅ Generated {len(questions)} samples")
    print(f"📂 Saved to {out_path}")
    print(f"🧾 Log: {LOG_FILE}")


if __name__ == "__main__":
    main()