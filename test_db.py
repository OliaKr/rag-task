import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("Database connection successful!")
        print(f"PostgreSQL version: {result.fetchone()[0]}")
except Exception as e:
    print(f"Database connection failed: {e}")
