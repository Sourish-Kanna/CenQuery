import pandas as pd
import re
import os

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_FILE = "input/population.xls"
OUTPUT_DIR = "output_normalized_population"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "population_stats.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_column_name(name):
    if not name: return "col"
    s = str(name).lower().strip()
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    return s[:60]

def process_population_data():
    print(f"📖 Reading: {INPUT_FILE}")
    try:
        df = pd.read_excel(INPUT_FILE)
    except Exception:
        try:
            df = pd.read_csv(INPUT_FILE)
        except Exception as e:
            print(f"❌ Error: {e}")
            return

    df.columns = [clean_column_name(c) for c in df.columns]
    
    if 'table' in df.columns:
        df.drop(columns=['table'], inplace=True)
    if 'age' in df.columns:
        df['age'] = df['age'].astype(str).str.replace('.0', '', regex=False)

    # --- FIX: Force Numeric on Raw Data ---
    print("🔢 Converting raw metrics to Numeric...")
    pop_cols = [c for c in df.columns if 'persons' in c or 'males' in c or 'females' in c]
    for col in pop_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    print("🔄 Unpivoting Data (Wide -> Long)...")
    
    # Total (1)
    df_tot = df[['state', 'age', 'total_persons', 'total_males', 'total_females']].copy()
    df_tot.columns = ['state', 'age', 'persons', 'males', 'females']
    df_tot['tru_id'] = 1

    # Rural (2)
    df_rur = df[['state', 'age', 'rural_persons', 'rural_males', 'rural_females']].copy()
    df_rur.columns = ['state', 'age', 'persons', 'males', 'females']
    df_rur['tru_id'] = 2

    # Urban (3)
    df_urb = df[['state', 'age', 'urban_persons', 'urban_males', 'urban_females']].copy()
    df_urb.columns = ['state', 'age', 'persons', 'males', 'females']
    df_urb['tru_id'] = 3

    df_norm = pd.concat([df_tot, df_rur, df_urb], ignore_index=True)
    df_norm['state'] = df_norm['state'].fillna(0).astype(int)
    
    # Save
    df_norm = df_norm[['state', 'tru_id', 'age', 'persons', 'males', 'females']]
    df_norm.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Created '{OUTPUT_CSV}' ({len(df_norm)} rows)")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        process_population_data()
    else:
        print(f"❌ File not found: {INPUT_FILE}")