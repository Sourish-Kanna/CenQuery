import random

# ==========================================
# 1. DATA & CONSTANTS
# ==========================================

STATES = [
    "Jammu & Kashmir", "Himachal Pradesh", "Punjab", "Chandigarh", "Uttarakhand",
    "Haryana", "NCT of Delhi", "Rajasthan", "Uttar Pradesh", "Bihar", "Sikkim",
    "Arunachal Pradesh", "Nagaland", "Manipur", "Mizoram", "Tripura", "Meghalaya",
    "Assam", "West Bengal", "Jharkhand", "Odisha", "Chhattisgarh", "Madhya Pradesh",
    "Gujarat", "Daman & Diu", "Dadra & Nagar Haveli", "Maharashtra", "Andhra Pradesh",
    "Karnataka", "Goa", "Lakshadweep", "Kerala", "Tamil Nadu", "Puducherry",
    "Andaman & Nicobar Islands"
]

RELIGIONS = ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain"]
TRU = ["Total", "Rural", "Urban"]
LANGUAGES = ["Hindi", "Bengali", "Telugu", "Marathi", "Tamil", "Urdu", "Gujarati", "Kannada", "Odia", "Malayalam",
             "English", "Sanskrit", "Punjabi", "Assamese", "Maithili"]
CROPS = ["Rice", "Wheat", "Maize", "Pulses", "Oilseeds", "Sugarcane", "Cotton", "Jute", "Coarse Cereals", "Foodgrains",
         "Nutri Cereals"]

HEALTHCARE_METRICS = {
    "fully vaccinated children (12-23 months)": "children_age_1223_months_fully_vaccinated_based_on_informati",
    "stunted children under 5": "children_under_5_years_who_are_stunted_heightforage18_",
    "wasted children under 5": "children_under_5_years_who_are_wasted_weightforheight18_",
    "underweight children under 5": "children_under_5_years_who_are_underweight_weightforage18_",
    "mothers with at least 4 antenatal visits": "mothers_who_had_at_least_4_antenatal_care_visits_for_last_bi",
    "institutional births": "institutional_births_in_the_5_years_before_the_survey_",
    "women with high blood sugar": "women_age_15_years_and_above_with_high_141160_mgdl_blood_sug",
    "men with high blood sugar": "men_age_15_years_and_above_wih_high_141160_mgdl_blood_sugar_",
    "households using clean fuel": "hh_using_clean_fuel_for_cooking3_",
    "women who are literate": "women_age_1549_who_are_lit4_",
    "anaemic children": "children_age_659_months_who_are_anaemic_110_gdl22_",
    "women with mobile phones": "women_age_1549_years_having_a_mobile_phone_that_they_themsel",
    "households with electricity": "pop_living_in_hh_with_electricity_",
    "children breastfed within one hour": "children_under_age_3_years_breastfed_within_one_hour_of_birt"
}


# ==========================================
# 2. GENERATORS
# ==========================================

def get_healthcare_lookup():
    """Specific value lookup: Metric + State + TRU"""
    state = random.choice(STATES)
    tru = random.choice(TRU)
    desc, col = random.choice(list(HEALTHCARE_METRICS.items()))
    q = f"What is the percentage of {desc} in {tru.lower()} {state}?"
    s = f"SELECT h.{col} FROM healthcare_stats h JOIN regions r ON h.state = r.state JOIN tru t ON h.tru_id = t.id WHERE r.area_name = '{state}' AND t.name = '{tru}';"
    return q, s


def get_healthcare_rank():
    """Ranking: Metric + Order + Limit"""
    desc, col = random.choice(list(HEALTHCARE_METRICS.items()))
    order = random.choice(["DESC", "ASC"])
    adj = "highest" if order == "DESC" else "lowest"
    limit = random.choice([1, 3, 5])

    q_limit = f"top {limit}" if limit > 1 else "state"
    q = f"Which {q_limit} have the {adj} percentage of {desc}?"
    s = f"SELECT r.area_name FROM healthcare_stats h JOIN regions r ON h.state = r.state JOIN tru t ON h.tru_id = t.id WHERE t.name = 'Total' ORDER BY CAST(h.{col} AS DOUBLE PRECISION) {order} LIMIT {limit};"
    return q, s


def get_religion_count():
    """Demographics: Religion + State + TRU"""
    state = random.choice(STATES)
    rel = random.choice(RELIGIONS)
    tru = random.choice(["Rural", "Urban", "Total"])
    q = f"What is the total {rel} population in {tru.lower()} {state}?"
    s = f"SELECT rs.tot_p FROM religion_stats rs JOIN regions r ON rs.state = r.state JOIN religions rel ON rs.religion_id = rel.id JOIN tru t ON rs.tru_id = t.id WHERE r.area_name = '{state}' AND rel.religion_name = '{rel}' AND t.name = '{tru}';"
    return q, s


def get_language_count():
    """Language: Lang + State + TRU"""
    state = random.choice(STATES)
    lang = random.choice(LANGUAGES)
    tru = random.choice(["Total", "Rural", "Urban"])
    q = f"How many people speak {lang} in {tru.lower()} {state}?"
    s = f"SELECT ls.person FROM language_stats ls JOIN regions r ON ls.state = r.state JOIN languages l ON ls.language_id = l.id JOIN tru t ON ls.tru_id = t.id WHERE r.area_name = '{state}' AND l.name = '{lang}' AND t.name = '{tru}';"
    return q, s


def get_crop_data():
    """Agriculture: Crop + Metric"""
    crop = random.choice(CROPS)
    metric_type = random.choice(["area_sown_2025_26", "area_sown_2024_25", "normal_area_dafw"])
    readable = metric_type.replace("_", " ").title()
    q = f"What is the {readable} for {crop}?"
    s = f"SELECT {metric_type} FROM crop_stats WHERE crop = '{crop}';"
    return q, s


def get_education_worker():
    """Education: Worker types + State"""
    worker_cols = [
        ("marginal cultivators", "marginal_cultivator_person"),
        ("main agricultural labourers", "main_agricultural_labourers_person"),
        ("household industry workers", "main_household_industries_person"),
        ("non-workers", "non_working_person")
    ]
    name, col = random.choice(worker_cols)
    state = random.choice(STATES)
    tru = random.choice(["Total", "Rural", "Urban"])
    q = f"How many {name} are there in {tru.lower()} {state}?"
    s = f"SELECT e.{col} FROM education_stats e JOIN regions r ON e.state = r.state JOIN tru t ON e.tru_id = t.id WHERE r.area_name = '{state}' AND t.name = '{tru}';"
    return q, s


def get_complex_compare():
    """Comparison: Urban vs Rural"""
    state = random.choice(STATES)
    desc, col = random.choice(list(HEALTHCARE_METRICS.items()))
    q = f"Is the percentage of {desc} higher in Urban or Rural {state}?"
    s = (f"SELECT CASE WHEN "
         f"(SELECT h.{col} FROM healthcare_stats h JOIN regions r ON h.state = r.state JOIN tru t ON h.tru_id = t.id WHERE r.area_name = '{state}' AND t.name = 'Urban') > "
         f"(SELECT h.{col} FROM healthcare_stats h JOIN regions r ON h.state = r.state JOIN tru t ON h.tru_id = t.id WHERE r.area_name = '{state}' AND t.name = 'Rural') "
         f"THEN 'Urban' ELSE 'Rural' END;")
    return q, s


# ==========================================
# 3. MAIN LOOP
# ==========================================

unique_dataset = set()
TARGET_COUNT = 350

# List of generator functions with weights to ensure diversity
generators = [
    (get_healthcare_lookup, 30),
    (get_healthcare_rank, 15),
    (get_religion_count, 15),
    (get_language_count, 15),
    (get_crop_data, 10),
    (get_education_worker, 10),
    (get_complex_compare, 5)
]

print(f"🚀 Generating {TARGET_COUNT} unique pairs...")

attempts = 0
while len(unique_dataset) < TARGET_COUNT:
    attempts += 1

    # Pick a generator based on weights
    gen_func = random.choices(
        [g[0] for g in generators],
        weights=[g[1] for g in generators],
        k=1
    )[0]

    pair = gen_func()

    # Add to set (automatically handles deduplication)
    unique_dataset.add(pair)

    # Safety break to prevent infinite loops if templates are exhausted (unlikely)
    if attempts > 5000:
        print("⚠️ Warning: Max attempts reached. Check template variety.")
        break

# Convert to list and shuffle
final_list = list(unique_dataset)
random.shuffle(final_list)

# ==========================================
# 4. SAVE FILES
# ==========================================

with open("evaluation_questions_1.txt", "w") as fq, open("evaluation_queries_1.sql", "w") as fs:
    for q, s in final_list:
        fq.write(q + "\n")
        fs.write(s + "\n")

print(f"✅ Success! Generated {len(final_list)} unique pairs.")
print("Files saved: evaluation_questions.txt, evaluation_queries.sql")