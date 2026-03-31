import os
import csv
from pydantic import BaseModel, Field
from typing import Any


def load_csv_keywords(filename: str, column: str):
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

# Get the directory of the current script for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(SCRIPT_DIR, "data"))
LANGUAGE_KEYWORDS = load_csv_keywords("languages.csv", "name")
RELIGION_KEYWORDS = load_csv_keywords("religions.csv", "religion_name")
AGE_GROUP_KEYWORDS = load_csv_keywords("age_groups.csv", "name")


# --- Pydantic Models ---
class GenerateSQLRequest(BaseModel):
    question: str = Field(..., description="Natural language question.")

class GenerateSQLResponse(BaseModel):
    question: str
    sql_query: str
    schema_selected: str | None = None
    model_type: str | None = None

class ExecuteSQLRequest(BaseModel):
    sql_query: str
    question: str | None = None

class ExecuteSQLResponse(BaseModel):
    sql_query: str
    result: Any
    question: str | None = None
    latency_ms: float
    status: str
    healed: bool = False


# --- Intent to Schema Mapping Rules ---
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
