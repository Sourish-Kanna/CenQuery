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
    """Standardizes column names: lowercase, underscores, no special chars."""
    if not name: return "col"
    s = str(name).lower().strip()
    s = re.sub(r'\s+', '_', s)            # Replace spaces with underscore
    s = re.sub(r'[^a-z0-9_]', '', s)      # Remove special chars
    return s[:60]

def process_population_data():
    print(f"📖 Reading: {INPUT_FILE}")
    try:
        df = pd.read_excel(INPUT_FILE)
        print("   ✅ Detected Excel format.")
    except Exception:
        try:
            df = pd.read_csv(INPUT_FILE)
            print("   ✅ Detected CSV format.")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None

    # 1. Clean Column Names
    df.columns = [clean_column_name(c) for c in df.columns]
    
    # 2. Basic Cleaning
    # Drop the 'table' column if it exists
    if 'table' in df.columns:
        df.drop(columns=['table'], inplace=True)
        
    # Clean Age
    if 'age' in df.columns:
        df['age'] = df['age'].astype(str).str.replace('.0', '', regex=False)

    # 3. Unpivot (Wide -> Long) to create TRU_ID
    print("🔄 Unpivoting Data (Wide -> Long)...")
    
    # We will create three dataframes and stack them
    
    # --- A. Total (tru_id = 1) ---
    df_tot = df[['state', 'age', 'total_persons', 'total_males', 'total_females']].copy()
    df_tot.rename(columns={
        'total_persons': 'persons', 
        'total_males': 'males', 
        'total_females': 'females'
    }, inplace=True)
    df_tot['tru_id'] = 1

    # --- B. Rural (tru_id = 2) ---
    df_rur = df[['state', 'age', 'rural_persons', 'rural_males', 'rural_females']].copy()
    df_rur.rename(columns={
        'rural_persons': 'persons', 
        'rural_males': 'males', 
        'rural_females': 'females'
    }, inplace=True)
    df_rur['tru_id'] = 2

    # --- C. Urban (tru_id = 3) ---
    df_urb = df[['state', 'age', 'urban_persons', 'urban_males', 'urban_females']].copy()
    df_urb.rename(columns={
        'urban_persons': 'persons', 
        'urban_males': 'males', 
        'urban_females': 'females'
    }, inplace=True)
    df_urb['tru_id'] = 3

    # 4. Combine
    df_norm = pd.concat([df_tot, df_rur, df_urb], ignore_index=True)
    
    # 5. Final Formating
    # Ensure State is int (Handles NaN if any)
    df_norm['state'] = df_norm['state'].fillna(0).astype(int)
    
    # Select and Reorder Columns
    cols = ['state', 'tru_id', 'age', 'persons', 'males', 'females']
    df_norm = df_norm[cols]

    # Save
    df_norm.to_csv(OUTPUT_CSV, index=False)
    print(f"💾 Saved Clean CSV to: {OUTPUT_CSV}")
    print(f"📊 Rows Generated: {len(df_norm)}")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
    else:
        process_population_data()