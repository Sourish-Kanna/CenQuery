import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def main():
    load_dotenv()

    # Read connection parameters from environment variables
    user = os.getenv("user")
    password = os.getenv("password")
    host = os.getenv("host")
    port = os.getenv("port", "5432")
    dbname = os.getenv("dbname")

    # Validate required parameters
    if not all([user, password, host, dbname]):
        print("Error: Missing required environment variables (user, password, host, dbname)", file=sys.stderr)
        sys.exit(1)

    # Construct SQLAlchemy connection string
    connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

    try:
        engine = create_engine(connection_string)
        conn = engine.connect()

        # Enable autocommit for role creation and ALTER DEFAULT PRIVILEGES
        conn = conn.connection.connection
        conn.autocommit = True
        cur = conn.cursor()

        print("Connected to PostgreSQL database")
        username = input("Enter name: ")
        pas = input("Enter password and Remember it: ")

        # 1. CREATE THE USER/ROLE
        cur.execute(f"""
            CREATE ROLE {username} WITH
                LOGIN
                PASSWORD '{pas}'
                NOSUPERUSER
                INHERIT
                NOCREATEDB
                NOCREATEROLE
                NOREPLICATION;
        """)
        print("Created role: census_reader")

        # 2. GRANT BASE ACCESS
        cur.execute(f"GRANT CONNECT ON DATABASE {dbname} TO census_reader;")
        cur.execute("GRANT USAGE ON SCHEMA public TO census_reader;")
        print("Granted CONNECT and USAGE on schema public")

        # 3. GRANT SELECT ON EXISTING TABLES & SEQUENCES
        cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO census_reader;")
        cur.execute("GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO census_reader;")
        print("Granted SELECT on existing tables and sequences in public")

        # 4. GRANT SELECT ON FUTURE OBJECTS
        cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO census_reader;")
        cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO census_reader;")
        print("Set default privileges for future tables and sequences")

        # 5. REVOKE CREATE PRIVILEGE FROM PUBLIC
        cur.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC;")
        print("Revoked CREATE on schema public from PUBLIC")

        conn.commit()
        cur.close()

        print("\nSetup complete. Verification commands:")
        print("  SELECT has_table_privilege('census_reader', 'regions', 'SELECT');   -- Should return true")
        print("  SELECT has_table_privilege('census_reader', 'regions', 'DELETE');   -- Should return false")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
