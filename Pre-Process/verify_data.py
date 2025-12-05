import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Database Config
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
DB_CONNECTION_STRING = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

def verify_join():
    print("🚀 Connecting to Database to verify Joins...")
    try:
        engine = create_engine(DB_CONNECTION_STRING)
        
        # FINAL CLEAN QUERY
        # No casting needed because your ETL pipeline now enforces numeric types!
        query = """
        SELECT 
            r.area_name AS state,
            t.name AS area_type,
            -- Education Data (Literacy Rate)
            (SUM(p.literates_person) * 100.0 / SUM(p.total_person)) AS literacy_rate,
            -- Healthcare Data (Infant Mortality)
            AVG(h.infant_mortality_rate_per_1000_live_births) AS infant_mortality_rate
        FROM regions r
        JOIN education_stats p ON p.state = r.state
        JOIN healthcare_stats h ON h.state = r.state
        JOIN tru t ON t.id = p.tru_id AND t.id = h.tru_id
        WHERE r.area_name ILIKE 'Kerala' AND t.name ILIKE 'Rural'
        GROUP BY r.area_name, t.name;
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(query))
            # Use list(result.keys()) to keep Pandas happy
            df = pd.DataFrame(result.fetchall(), columns=list(result.keys()))
            
        if not df.empty:
            print("\n✅ JOIN SUCCESSFUL! Here is the data:")
            print(df.to_string(index=False))
            print("\n🎉 Success! Your Education and Healthcare data are perfectly linked.")
        else:
            print("\n❌ Query returned no data. Check your State/TRU IDs.")

    except Exception as e:
        print(f"\n❌ SQL Error: {e}")

if __name__ == "__main__":
    verify_join()