import os
from sqlalchemy import create_engine, text
import pandas as pd
import json
from dotenv import load_dotenv

# --- Configuration ---
# Default to a local PG instance if the environment variable is not set.
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please add it to your .env file.") 
POPULATION_TABLE = "population"
LITERACY_TABLE = "literacy"
HOUSING_TABLE = "housing"

def setup_database():
    """
    Connects to a PostgreSQL database and appends sample census data.
    If the tables do not exist, they will be created.
    """
    print(f"Connecting to database at: {DATABASE_URL}")
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Database connection successful.")
            
            # --- Sample Data Generation ---

            # Population Data
            population_data = {
                'state': ['Maharashtra', 'Maharashtra', 'Tamil Nadu', 'Tamil Nadu'],
                'district': ['Mumbai', 'Pune', 'Chennai', 'Coimbatore'],
                'year': [2011, 2011, 2011, 2011],
                'male': [9800000, 4700000, 4300000, 2100000],
                'female': [8600000, 4500000, 4100000, 2000000],
                'total': [18400000, 9200000, 8400000, 4100000]
            }
            df_pop = pd.DataFrame(population_data)

            # Literacy Data
            literacy_data = {
                'state': ['Maharashtra', 'Maharashtra', 'Tamil Nadu', 'Tamil Nadu'],
                'district': ['Mumbai', 'Pune', 'Chennai', 'Coimbatore'],
                'year': [2011, 2011, 2011, 2011],
                'literate': [16200000, 8000000, 7500000, 3500000],
                'illiterate': [2200000, 1200000, 900000, 600000]
            }
            df_lit = pd.DataFrame(literacy_data)

            # Housing Data
            housing_data = {
                'state': ['Maharashtra', 'Maharashtra', 'Tamil Nadu', 'Tamil Nadu'],
                'district': ['Mumbai', 'Pune', 'Chennai', 'Coimbatore'],
                'year': [2011, 2011, 2011, 2011],
                'households': [4500000, 2300000, 2100000, 1000000],
                'amenities': [
                    json.dumps({'electricity': True, 'water': True, 'internet': True}),
                    json.dumps({'electricity': True, 'water': True, 'internet': False}),
                    json.dumps({'electricity': True, 'water': True, 'internet': True}),
                    json.dumps({'electricity': True, 'water': False, 'internet': False})
                ]
            }
            df_house = pd.DataFrame(housing_data)
            
            # --- Write to Database ---
            
            # Use a transaction to ensure all tables are written to or none are.
            with connection.begin():
                # Append data to the tables. If they don't exist, pandas creates them.
                df_pop.to_sql(POPULATION_TABLE, connection, if_exists='append', index=False)
                df_lit.to_sql(LITERACY_TABLE, connection, if_exists='append', index=False)
                df_house.to_sql(HOUSING_TABLE, connection, if_exists='append', index=False)
            
            print(f"Data appended to tables: '{POPULATION_TABLE}', '{LITERACY_TABLE}', and '{HOUSING_TABLE}'.")
            
            # --- Verify Data ---
            print("\nVerifying data from all tables (showing total row count):")
            for table in [POPULATION_TABLE, LITERACY_TABLE, HOUSING_TABLE]:
                result = connection.execute(text(f"SELECT COUNT(*) FROM {table};"))
                row_count = result.scalar()
                print(f"- Table '{table}' now contains {row_count} rows.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure the PostgreSQL server is running and the DATABASE_URL is correct.")

if __name__ == "__main__":
    setup_database()

