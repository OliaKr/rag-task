# Check database contents

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))


def inspect_database(filename=None):
    try:
        with engine.connect() as conn:
            if filename:
                query = text("""
                    SELECT id, chunk_content, source_file, chunking_method, created_at
                    FROM document_chunks 
                    WHERE source_file = :filename 
                    LIMIT 5
                """)
                result = conn.execute(query, {"filename": filename})
                print(f"Inspecting records for '{filename}':")
            else:
                query = text("""
                    SELECT id, chunk_content, source_file, chunking_method, created_at
                    FROM document_chunks 
                    LIMIT 5
                """)
                result = conn.execute(query)
                print("Inspecting all records:")

            rows = result.fetchall()

            if not rows:
                print("No records found in database.")
                return

            print(f"Found {len(rows)} sample records:")
            print("-" * 80)

            for i, row in enumerate(rows, 1):
                print(f"   Record {i}:")
                print(f"   ID: {row.id}")
                print(f"   File: {row.source_file}")
                print(f"   Method: {row.chunking_method}")
                print(f"   Created: {row.created_at}")
                print(f"   Content: {row.chunk_content[:100]}...")
                print("-" * 80)

    except Exception as e:
        print(f"Database inspection failed: {e}")


def get_database_stats():
    try:
        with engine.connect() as conn:
            total_result = conn.execute(
                text("SELECT COUNT(*) FROM document_chunks"))
            total_count = total_result.fetchone()[0]

            file_result = conn.execute(text("""
                SELECT source_file, COUNT(*) as count 
                FROM document_chunks 
                GROUP BY source_file
            """))
            file_counts = file_result.fetchall()

            print("    Database Statistics:")
            print(f"   Total records: {total_count}")
            print("   Records by file:")
            for file_name, count in file_counts:
                print(f"     {file_name}: {count} chunks")

    except Exception as e:
        print(f"Failed to get database stats: {e}")


if __name__ == "__main__":
    filename = input(
        "Enter filename to inspect (or press Enter for all): ").strip() or None
    inspect_database(filename)
    get_database_stats()
