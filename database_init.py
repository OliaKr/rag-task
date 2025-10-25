import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))


def create_tables():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS document_chunks (
        id SERIAL PRIMARY KEY,
        chunk_content TEXT NOT NULL,
        embedding REAL[] NOT NULL,
        source_file TEXT NOT NULL,
        chunking_method TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    with engine.connect() as conn:
        conn.execute(text(create_table_query))
        conn.commit()
        print("Database tables created successfully.")


def verify_database():
    try:
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'document_chunks'
                );
            """))
            table_exists = result.fetchone()[0]

            if table_exists:
                print("Table 'document_chunks' exists")

                # Count records
                count_result = conn.execute(
                    text("SELECT COUNT(*) FROM document_chunks"))
                count = count_result.fetchone()[0]
                print(f"Records in database: {count}")
            else:
                print("Table 'document_chunks' does not exist")

    except Exception as e:
        print(f"Database verification failed: {e}")


if __name__ == "__main__":
    print("Initializing database...")
    create_tables()
    verify_database()
    print("Database initialization complete!")
