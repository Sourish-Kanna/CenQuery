import pandas as pd
import re
import os

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_FILE = "input/education.xls"
OUTPUT_DIR = "output_normalized_education"
TRU_FILE = os.path.join(OUTPUT_DIR, "tru.csv")
# FIX: Renamed output file
PCA_STATS_FILE = os.path.join(OUTPUT_DIR, "education_stats.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_column_name(name):
    if not name: return "col"
    s = str(name).lower().strip()
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    s = s.replace('population_person', 'person')
    s = s.replace('population_male', 'male')
    s = s.replace('population_female', 'female')
    return s[:60]

def process_pca_data():
    print(f"📖 Reading: {INPUT_FILE}")
    try:
        df = pd.read_csv(INPUT_FILE)
    except:
        try:
            df = pd.read_excel(INPUT_FILE)
        except Exception as e:
            print(f"❌ Error: {e}")
            return

    df.columns = [clean_column_name(c) for c in df.columns]
    
    if 'state_code' in df.columns:
        df.rename(columns={'state_code': 'state'}, inplace=True)
    
    print("   Standardizing TRU...")
    tru_map = {"Total": 1, "Rural": 2, "Urban": 3}
    pd.DataFrame(list(tru_map.items()), columns=['name', 'id'])[['id', 'name']].to_csv(TRU_FILE, index=False)

    df['tru_clean'] = df['tru'].astype(str).str.title()
    df['tru_id'] = df['tru_clean'].map(tru_map)

    print("🔢 Converting metrics to Numeric (Int)...")
    keys = ['state', 'tru_id']
    for col in df.columns:
        if col not in keys and col not in ['tru', 'tru_clean', 'name', 'level']:
            if col in ['district_code', 'subdistt_code', 'townvillage_code', 'state_code1', 'ward_code', 'eb_code']: 
                continue
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    cols_to_drop = ['district_code', 'subdistt_code', 'townvillage_code', 'state_code1', 'ward_code', 'eb_code', 'level', 'name', 'tru', 'tru_clean']
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True, errors='ignore')

    if 'state' in df.columns:
        df['state'] = df['state'].fillna(0).astype(int)

    df.to_csv(PCA_STATS_FILE, index=False)
    print(f"✅ Created '{PCA_STATS_FILE}'")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        process_pca_data()
    else:
        print(f"❌ File not found: {INPUT_FILE}")