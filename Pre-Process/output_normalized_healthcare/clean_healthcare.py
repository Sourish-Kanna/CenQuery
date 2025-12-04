import pandas as pd
import re
import os

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_FILE = "input/Healthcare.xls"
OUTPUT_DIR = "output_normalized_healthcare"

# Master Files
REGIONS_FILE = os.path.join(OUTPUT_DIR, "regions.csv")
TRU_FILE = os.path.join(OUTPUT_DIR, "tru.csv")

# Output for this specific dataset
STATS_FILE = os.path.join(OUTPUT_DIR, "healthcare_stats.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# 🗺️ MASTER STATE MAPPING (Census 2011 + New)
# ==========================================
# This ensures IDs match Population (1-35) while accommodating new states
MASTER_STATES = {
    0: "India",
    1: "Jammu & Kashmir",
    2: "Himachal Pradesh",
    3: "Punjab",
    4: "Chandigarh",
    5: "Uttarakhand",
    6: "Haryana",
    7: "NCT of Delhi",
    8: "Rajasthan",
    9: "Uttar Pradesh",
    10: "Bihar",
    11: "Sikkim",
    12: "Arunachal Pradesh",
    13: "Nagaland",
    14: "Manipur",
    15: "Mizoram",
    16: "Tripura",
    17: "Meghalaya",
    18: "Assam",
    19: "West Bengal",
    20: "Jharkhand",
    21: "Odisha",
    22: "Chhattisgarh",
    23: "Madhya Pradesh",
    24: "Gujarat",
    25: "Daman & Diu",
    26: "Dadra & Nagar Haveli",
    27: "Maharashtra",
    28: "Andhra Pradesh",
    29: "Karnataka",
    30: "Goa",
    31: "Lakshadweep",
    32: "Kerala",
    33: "Tamil Nadu",
    34: "Puducherry",
    35: "Andaman & Nicobar Islands",
    # --- New / Merged Entities ---
    36: "Dadra and Nagar Haveli and Daman and Diu",
    37: "Ladakh",
    38: "Telangana"
}

def clean_column_name(name):
    """Shortens verbose healthcare column names."""
    if not name: return "col"
    s = str(name).lower().strip()
    replacements = {
        'per 1,000 live births': '',
        'per 100,000 live births': '',
        'percentage': 'pct',
        'population': 'pop',
        'households': 'hh',
        'children under age 5 years': 'child_u5',
        'women age 15-49 years': 'women_15_49',
        'men age 15-54 years': 'men_15_54',
        'literate': 'lit',
        'attended school': 'school',
        'sex ratio': 'sex_ratio',
        'births': 'births',
        'deaths': 'deaths'
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    return s[:60]

def get_state_id(name):
    """Maps input state names to the Master IDs."""
    if pd.isna(name): return None
    name = str(name).strip().lower()
    
    # Standardize common variations
    name = name.replace('&', 'and').replace(' and ', ' & ')
    name = name.replace('odisha', 'orissa') # Handle legacy names if needed
    name = name.replace('orissa', 'odisha') # Standardize to Odisha
    name = name.replace('chhattisgarh', 'chhatisgarh').replace('chhatisgarh', 'chhattisgarh')
    
    # Reverse lookup from MASTER_STATES (Case insensitive)
    for pid, pname in MASTER_STATES.items():
        # Exact match check
        if pname.lower() == name:
            return pid
            
        # Handle Merged UT case specific to Healthcare
        if "dadra" in name and "daman" in name:
            return 36 # The new ID for merged UT
            
        # Handle Ladakh
        if "ladakh" in name:
            return 37
            
        # Handle Telangana
        if "telangana" in name:
            return 38
            
    return None

def process_healthcare_data():
    print(f"📖 Reading: {INPUT_FILE}")
    try:
        # Attempt to find the header row dynamically
        df = pd.read_excel(INPUT_FILE, header=0)
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # 1. Clean Columns
    df.columns = [clean_column_name(c) for c in df.columns]
    
    # 2. Generate Master Regions File
    print("🗺️  Generating Master Regions Lookup...")
    regions_df = pd.DataFrame(list(MASTER_STATES.items()), columns=['state', 'area_name'])
    regions_df.to_csv(REGIONS_FILE, index=False)
    print(f"   ✅ Created '{REGIONS_FILE}' with {len(regions_df)} regions.")

    # 3. Map Data to Master IDs
    print("🔄 Mapping Healthcare Data to Standard IDs...")
    
    # Find state column
    state_col = next((c for c in df.columns if 'state' in c or 'india' in c), None)
    if not state_col:
        # Fallback: assume first column
        state_col = df.columns[0]

    # Apply mapping
    df['state'] = df[state_col].apply(get_state_id)
    
    # Check for unmapped states
    unmapped = df[df['state'].isnull()][state_col].unique()
    if len(unmapped) > 0:
        print(f"⚠️  Warning: Could not map these states: {unmapped}")
        # Drop rows we can't map (usually footnotes or empty lines)
        df = df.dropna(subset=['state'])
    
    df['state'] = df['state'].astype(int)

    # 4. Process TRU
    print("🏙️  Processing TRU (Area)...")
    tru_map = {"Total": 1, "Rural": 2, "Urban": 3}
    
    # Create TRU lookup file
    tru_df = pd.DataFrame(list(tru_map.items()), columns=['name', 'id'])[['id', 'name']]
    tru_df.to_csv(TRU_FILE, index=False)
    
    # Find Area column
    area_col = next((c for c in df.columns if 'area' in c or 'urban' in c), None)
    
    if area_col:
        df['tru_id'] = df[area_col].astype(str).str.title().map(tru_map)
        df['tru_id'] = df['tru_id'].fillna(1).astype(int)
    else:
        print("   ⚠️  No Area column found. Defaulting to Total (1).")
        df['tru_id'] = 1

    # 5. Cleanup & Save
    cols_to_drop = [state_col, area_col] if area_col else [state_col]
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True, errors='ignore')

    # Reorder
    cols = list(df.columns)
    for col in ['tru_id', 'state']:
        if col in cols:
            cols.insert(0, cols.pop(cols.index(col)))
    df = df[cols]
    
    df.to_csv(STATS_FILE, index=False)
    print(f"✅ Created '{STATS_FILE}'")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        process_healthcare_data()
    else:
        print(f"❌ File not found: {INPUT_FILE}")