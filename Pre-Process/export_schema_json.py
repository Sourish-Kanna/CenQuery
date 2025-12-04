import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

# Load environment variables
load_dotenv()

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
# Database Credentials
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Connection String
DB_CONNECTION_STRING = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# Output File
OUTPUT_FILE = "database_schema.json"

# List of tables to export
TARGET_TABLES = [
    # Masters
    "regions", "tru", "religions", "languages", "age_groups",
    # Data
    "population_stats", "healthcare_stats", "pca_stats", 
    "religion_stats", "occupation_stats", "language_stats", "crop_stats"
]

def export_schema_to_json():
    print("🚀 Connecting to Database to fetch Schema...")
    
    schema_data = {}
    
    try:
        engine = create_engine(DB_CONNECTION_STRING)
        inspector = inspect(engine)
        
        # Get list of all tables actually in the DB
        existing_tables = inspector.get_table_names()
        
        for table_name in TARGET_TABLES:
            if table_name not in existing_tables:
                print(f"⚠️  Skipping {table_name} (Not found in DB)")
                continue
                
            print(f"   Processing table: {table_name}...")
            
            # 1. Fetch Columns
            columns = inspector.get_columns(table_name)
            
            # 2. Fetch Constraints
            pk_constraint = inspector.get_pk_constraint(table_name)
            primary_keys = pk_constraint.get('constrained_columns', [])
            fks = inspector.get_foreign_keys(table_name)
            
            # 3. Build Column Data
            table_columns = []
            for col in columns:
                col_name = col['name']
                col_type = str(col['type'])
                
                # Determine constraints for this specific column
                constraints = []
                if col_name in primary_keys:
                    constraints.append("PK")
                
                for fk in fks:
                    if col_name in fk['constrained_columns']:
                        ref_table = fk['referred_table']
                        ref_col = fk['referred_columns'][0]
                        constraints.append(f"FK -> {ref_table}({ref_col})")
                
                table_columns.append({
                    "name": col_name,
                    "type": col_type,
                    "constraints": constraints
                })

            # 4. Build Table Object
            schema_data[table_name] = {
                "columns": table_columns,
                "primary_key": primary_keys,
                "foreign_keys": [
                    {
                        "column": fk['constrained_columns'][0],
                        "references": f"{fk['referred_table']}({fk['referred_columns'][0]})"
                    } for fk in fks
                ]
            }
            
        # 5. Save to JSON
        with open(OUTPUT_FILE, "w") as f:
            json.dump(schema_data, f, indent=4)
            
        print(f"\n✅ Schema successfully saved to '{OUTPUT_FILE}'")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    export_schema_to_json()