"""
Document indexing for the RAG pipeline.

Takes PDF documents and prepares them for semantic search by:
- Loading and extracting text from PDFs
- Splitting into 600-character chunks with 60-char overlap
- Generating embeddings using Google Gemini API
- Storing everything in PostgreSQL

The chunking size was chosen to work well with recipe documents while keeping
context intact. Batch processing helps avoid hitting API rate limits.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np

load_dotenv()

# Set up database and AI components
engine = create_engine(os.getenv("POSTGRES_URL"))
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


def load_pdf(file_path):

    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"Loaded {len(documents)} pages from {file_path}")
        return documents
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return []


def chunk_documents(documents, chunk_size=600, chunk_overlap=60):
    """Split documents into fixed-size chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    return chunks


def create_embeddings(chunks):
    """Generate embeddings for document chunks."""
    print("Generating embeddings...")
    texts = [chunk.page_content for chunk in chunks]

    # Process in small batches to avoid API limits
    batch_size = 2
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print(
            f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")

        try:
            batch_embeddings = embeddings.embed_documents(batch)
            all_embeddings.extend(batch_embeddings)
            print(f"Generated {len(batch_embeddings)} embeddings for batch")

            # Small delay between batches
            if i + batch_size < len(texts):
                print("Waiting 2 seconds before next batch...")
                import time
                time.sleep(2)

        except Exception as e:
            print(f"Error processing batch: {e}")
            break

    print(f"Generated {len(all_embeddings)} embeddings total")
    return all_embeddings


def store_chunks(chunks, embeddings_list, source_file):
    """Save processed chunks and their embeddings to the database."""
    try:
        with engine.connect() as conn:
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
                # CURRENT_TIMESTAMP is a PostgreSQL function that automatically sets the timestamp
                # No need to pass created_at as a parameter - the database handles it
                insert_query = text("""
                    INSERT INTO document_chunks (chunk_content, embedding, source_file, chunking_method, created_at)
                    VALUES (:chunk_content, :embedding, :source_file, :chunking_method, CURRENT_TIMESTAMP)
                """)

                conn.execute(insert_query, {
                    "chunk_content": chunk.page_content,
                    "embedding": embedding,
                    "source_file": source_file,
                    "chunking_method": "fixed_size_600_60"
                })

            conn.commit()
            print(f"Stored {len(chunks)} chunks in database")

    except Exception as e:
        print(f"Error storing chunks: {e}")


def process_document(file_path):
    print(f"Processing document: {file_path}")

    documents = load_pdf(file_path)
    if not documents:
        return

    chunks = chunk_documents(documents)
    if not chunks:
        return

    embeddings_list = create_embeddings(chunks)

    store_chunks(chunks, embeddings_list, os.path.basename(file_path))

    print("Document processing complete!")


if __name__ == "__main__":
    pdf_path = "Easy recipes.pdf"
    if os.path.exists(pdf_path):
        process_document(pdf_path)
    else:
        print(f"File not found: {pdf_path}")
