import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

load_dotenv()

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_DIR = "unified_outputs"

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

DB_CONNECTION_STRING = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# ==========================================
# 📋 UPLOAD ORDER & SCHEMA DEFINITION
# ==========================================
UPLOAD_SEQUENCE = [
    # --- 1. Master Tables (Lookups) ---
    ("regions.csv", "regions", ["state"]),
    ("tru.csv", "tru", ["id"]),
    ("religions.csv", "religions", ["id"]),
    ("languages.csv", "languages", ["id"]),
    ("age_groups.csv", "age_groups", ["id"]),

    # --- 2. Data Tables (Facts) ---
    ("population_stats.csv", "population_stats", None),
    ("healthcare_stats.csv", "healthcare_stats", None),
    ("education_stats.csv", "education_stats", None), # FIX: New filename & table name
    ("religion_stats.csv", "religion_stats", None),
    ("occupation_stats.csv", "occupation_stats", None),
    ("language_stats.csv", "language_stats", None),
    ("crops.csv", "crop_stats", None)
]

FOREIGN_KEYS = {
    "population_stats": [("state", "regions(state)"), ("tru_id", "tru(id)")],
    "healthcare_stats": [("state", "regions(state)"), ("tru_id", "tru(id)")],
    "education_stats":  [("state", "regions(state)"), ("tru_id", "tru(id)")], # FIX: Renamed key
    "religion_stats":   [("state", "regions(state)"), ("tru_id", "tru(id)"), ("religion_id", "religions(id)")],
    "occupation_stats": [("state", "regions(state)"), ("tru_id", "tru(id)"), ("age_group_id", "age_groups(id)")],
    "language_stats":   [("state", "regions(state)"), ("tru_id", "tru(id)"), ("language_id", "languages(id)")],
}

def clean_database(engine):
    print("\n🧹 Cleaning Database (dropping old tables)...")
    # Added education_stats to drop list
    tables_to_drop = [
        "population_stats", "healthcare_stats", "education_stats", "pca_stats", 
        "religion_stats", "occupation_stats", "language_stats", "crop_stats",
        "regions", "tru", "religions", "languages", "age_groups"
    ]
    
    with engine.begin() as conn:
        for table in tables_to_drop:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            print(f"   🗑️  Dropped {table}")
    print("✨ Database is clean.\n")

def enable_rls(table_name, engine):
    try:
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;"))
            conn.execute(text(f"DROP POLICY IF EXISTS \"Public Read\" ON {table_name};"))
            conn.execute(text(f"CREATE POLICY \"Public Read\" ON {table_name} FOR SELECT USING (true);"))
        print(f"   🔒 RLS enabled for {table_name}.")
    except Exception as e:
        print(f"   ⚠️  Warning setting RLS for {table_name}: {e}")

def add_primary_key(table_name, pk_column, engine):
    try:
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD PRIMARY KEY ({pk_column});"))
        print(f"   🔑 Primary Key set on {table_name}({pk_column})")
    except Exception as e:
        print(f"   ⚠️  PK Error (might already exist): {e}")

def add_foreign_keys(table_name, engine):
    if table_name not in FOREIGN_KEYS:
        return

    with engine.begin() as conn:
        for fk_col, ref_def in FOREIGN_KEYS[table_name]:
            ref_table, ref_col = ref_def.replace(')', '').split('(')
            constraint_name = f"fk_{table_name}_{fk_col}"
            try:
                query = f"""
                    ALTER TABLE {table_name} 
                    DROP CONSTRAINT IF EXISTS {constraint_name};
                    
                    ALTER TABLE {table_name} 
                    ADD CONSTRAINT {constraint_name} 
                    FOREIGN KEY ({fk_col}) REFERENCES {ref_table}({ref_col});
                """
                conn.execute(text(query))
                print(f"   🔗 Linked {fk_col} -> {ref_table}({ref_col})")
            except Exception as e:
                print(f"   ❌ FK Error on {table_name} ({fk_col}): {e}")

def upload_file(filename, table_name, pk_columns, engine):
    file_path = os.path.join(INPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        print(f"⏭️  Skipping {filename} (File not found)")
        return

    print(f"📤 Uploading: {filename} -> Table: {table_name}")
    
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower()
        
        df.to_sql(table_name, engine, if_exists='replace', index=False, chunksize=10000)
        print(f"   ✅ Uploaded {len(df)} rows.")
        
        if pk_columns:
            for pk in pk_columns:
                add_primary_key(table_name, pk, engine)

        add_foreign_keys(table_name, engine)
        enable_rls(table_name, engine)
        print("") 

    except Exception as e:
        print(f"   ❌ FAILED: {e}")

if __name__ == "__main__":
    print("🚀 Starting Unified Database Upload...")
    
    if not os.path.exists(INPUT_DIR):
        print(f"❌ Error: Directory '{INPUT_DIR}' does not exist. Run consolidate_outputs.py first.")
        exit()

    try:
        engine = create_engine(DB_CONNECTION_STRING, poolclass=NullPool)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database Connection Successful.")
        
        clean_database(engine)
        
        processed_files = set()
        for filename, table_name, pk_cols in UPLOAD_SEQUENCE:
            if filename not in processed_files:
                upload_file(filename, table_name, pk_cols, engine)
                processed_files.add(filename)
            
        print("🎉 All tasks completed successfully!")

    except Exception as e:
        print(f"\n❌ FATAL DB ERROR: {e}")