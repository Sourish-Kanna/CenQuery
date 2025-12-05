import pandas as pd
import re
import os

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_FILE = "input/Language.xlsx"
OUTPUT_DIR = "output_normalized_language"
LANGUAGES_FILE = os.path.join(OUTPUT_DIR, "languages.csv")
TRU_FILE = os.path.join(OUTPUT_DIR, "tru.csv")
LANGUAGE_STATS_FILE = os.path.join(OUTPUT_DIR, "language_stats.csv")
REGIONS_FILE = os.path.join(OUTPUT_DIR, "regions.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_area_name(text):
    if not isinstance(text, str): return text
    text = str(text).replace('State - ', '')
    text = re.sub(r'\s*\(\d+\)', '', text)
    return text.strip()

def clean_language_name(text):
    if not isinstance(text, str): return text
    text = re.sub(r'^\d+\s+', '', text)
    return text.strip().title()

def process_language_data():
    print(f"📖 Reading: {INPUT_FILE}")
    column_names = [
        "table_code", "state_code", "district_code", "sub_district_code", "area_name",
        "language_code", "language_name",
        "tot_p", "tot_m", "tot_f", "rur_p", "rur_m", "rur_f", "urb_p", "urb_m", "urb_f"
    ]

    try:
        df = pd.read_excel(INPUT_FILE, skiprows=6, header=None, names=column_names, dtype={'state_code': str})
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    df = df.dropna(subset=['state_code'])
    df['area_name'] = df['area_name'].apply(clean_area_name)
    df['language_name_clean'] = df['language_name'].apply(clean_language_name)

    languages_df = df[['language_code', 'language_name_clean']].drop_duplicates()
    languages_df.rename(columns={'language_name_clean': 'name', 'language_code': 'id'}, inplace=True)
    languages_df.to_csv(LANGUAGES_FILE, index=False)
    
    regions_df = df[['state_code', 'area_name']].drop_duplicates()
    regions_df.to_csv(REGIONS_FILE, index=False)

    print("   Standardizing TRU...")
    tru_data = [{'id': 1, 'name': 'Total'}, {'id': 2, 'name': 'Rural'}, {'id': 3, 'name': 'Urban'}]
    pd.DataFrame(tru_data).to_csv(TRU_FILE, index=False)

    print("🔄 Unpivoting Data...")
    normalized_rows = []
    for _, row in df.iterrows():
        base_info = {'state': row['state_code'], 'language_id': row['language_code']}
        
        # Get raw values (might be string or int)
        t_p, t_m, t_f = row['tot_p'], row['tot_m'], row['tot_f']
        r_p, r_m, r_f = row['rur_p'], row['rur_m'], row['rur_f']
        u_p, u_m, u_f = row['urb_p'], row['urb_m'], row['urb_f']

        normalized_rows.append({**base_info, 'tru_id': 1, 'person': t_p, 'male': t_m, 'female': t_f})
        normalized_rows.append({**base_info, 'tru_id': 2, 'person': r_p, 'male': r_m, 'female': r_f})
        normalized_rows.append({**base_info, 'tru_id': 3, 'person': u_p, 'male': u_m, 'female': u_f})

    df_norm = pd.DataFrame(normalized_rows)
    
    # --- FIX: Force Numeric Conversion ---
    print("🔢 Converting metrics to Numeric (Int)...")
    for c in ['person', 'male', 'female']:
        df_norm[c] = pd.to_numeric(df_norm[c], errors='coerce').fillna(0).astype(int)
        
    # Ensure keys are int
    df_norm['state'] = pd.to_numeric(df_norm['state'], errors='coerce').fillna(0).astype(int)

    df_norm.to_csv(LANGUAGE_STATS_FILE, index=False)
    print(f"✅ Created '{LANGUAGE_STATS_FILE}'")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        process_language_data()
    else:
        print(f"❌ File not found: {INPUT_FILE}")