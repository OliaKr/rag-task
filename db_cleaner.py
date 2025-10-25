# Clean up database records

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))


def clean_db(filename=None):
    """Remove records from database."""
    try:
        with engine.connect() as conn:
            if filename:
                # Count records before deletion
                count_query = text(
                    "SELECT COUNT(*) FROM document_chunks WHERE source_file = :filename")
                count_result = conn.execute(
                    count_query, {"filename": filename})
                count = count_result.fetchone()[0]

                if count == 0:
                    print(f"No records found for '{filename}'")
                    return

                # Delete records
                delete_query = text(
                    "DELETE FROM document_chunks WHERE source_file = :filename")
                conn.execute(delete_query, {"filename": filename})
                conn.commit()

                print(f"Deleted {count} records for '{filename}'")
            else:
                # Count all records
                count_query = text("SELECT COUNT(*) FROM document_chunks")
                count_result = conn.execute(count_query)
                count = count_result.fetchone()[0]

                if count == 0:
                    print("No records found in database")
                    return

                # Confirm deletion
                confirm = input(
                    f"Are you sure you want to delete ALL {count} records? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("Deletion cancelled")
                    return

                # Delete all records
                delete_query = text("DELETE FROM document_chunks")
                conn.execute(delete_query)
                conn.commit()

                print(f"Deleted all {count} records")

    except Exception as e:
        print("Cleanup failed")


def reset_db():
    """Reset database by dropping and recreating tables."""
    try:
        with engine.connect() as conn:
            # Drop table
            drop_query = text("DROP TABLE IF EXISTS document_chunks")
            conn.execute(drop_query)
            conn.commit()
            print("Table dropped")

            # Recreate table
            create_query = text("""
                CREATE TABLE document_chunks (
                    id SERIAL PRIMARY KEY,
                    chunk_content TEXT NOT NULL,
                    embedding REAL[] NOT NULL,
                    source_file TEXT NOT NULL,
                    chunking_method TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute(create_query)
            conn.commit()
            print("Table recreated")

    except Exception as e:
        print("Reset failed")


if __name__ == "__main__":
    print("Database Cleanup Utility")
    print("1. Clean specific file")
    print("2. Clean all records")
    print("3. Reset database")

    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        filename = input("Enter filename to clean: ").strip()
        clean_db(filename)
    elif choice == "2":
        clean_db()
    elif choice == "3":
        confirm = input(
            "This will delete ALL data. Are you sure? (yes/no): ")
        if confirm.lower() == 'yes':
            reset_db()
        else:
            print("Reset cancelled")
    else:
        print("Invalid choice")
