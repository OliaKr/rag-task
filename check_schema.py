import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))

print("Checking PostgreSQL schema...\n")

try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'document_chunks'
            ORDER BY ordinal_position
        """))

        columns = result.fetchall()

        if columns:
            print("Columns in 'document_chunks' table:")
            print("-" * 40)
            for col_name, col_type in columns:
                print(f"  {col_name}: {col_type}")
            print("-" * 40)
        else:
            print("Table 'document_chunks' does not exist or has no columns")

except Exception as e:
    print(f"Error: {e}")
