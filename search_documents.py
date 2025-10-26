"""
Search and answer generation for recipe queries.

Handles the retrieval side of the RAG pipeline:
- Converts user questions to embeddings (Gemini)
- Searches for similar chunks using cosine similarity
- Generates answers with OpenAI GPT based on retrieved context

The embeddings are stored as arrays in PostgreSQL. When a query comes in,
we calculate similarity scores against all stored chunks and pass the most
relevant ones to the LLM for answer generation.
"""

import os
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI

load_dotenv()

engine = create_engine(os.getenv("POSTGRES_URL"))
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY"))  # Gemini for embeddings
# OpenAI for answer generation
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY"))


def cosine_similarity(vec1, vec2):
    """Calculate similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)


def search_similar_chunks(query, top_k=5):
    """Find chunks most similar to the query."""
    print(f"Searching for: '{query}'")

    # Generate embedding for the query
    query_embedding = embeddings.embed_query(query)

    try:
        with engine.connect() as conn:
            # Get all chunks from database
            result = conn.execute(text("""
                SELECT id, chunk_content, embedding, source_file, chunking_method
                FROM document_chunks
            """))

            chunks = []
            for row in result:
                # Calculate similarity
                similarity = cosine_similarity(query_embedding, row.embedding)
                chunks.append({
                    "id": row.id,
                    "text": row.chunk_content,
                    "filename": row.source_file,
                    "split_strategy": row.chunking_method,
                    "similarity": similarity
                })

            # Sort by similarity and get top results
            chunks.sort(key=lambda x: x["similarity"], reverse=True)
            top_chunks = chunks[:top_k]

            print(f"\nFound {len(top_chunks)} relevant chunks:")
            for i, chunk in enumerate(top_chunks, 1):
                print(
                    f"{i}. Similarity: {chunk['similarity']:.4f} | File: {chunk['filename']}")

            return top_chunks

    except Exception as e:
        print(f"Error searching database: {e}")
        return []


def generate_answer(query, context_chunks):
    """Generate answer using retrieved context."""
    if not context_chunks:
        return "No relevant information found in the database."

    # Build context from retrieved chunks
    context = "\n\n".join([f"Context {i+1}:\n{chunk['text']}"
                           for i, chunk in enumerate(context_chunks)])

    # Create prompt for LLM
    prompt = f"""You are helpful assistant specialized in recipe questions. Use the context to provide clear and accurate answers.

{context}

User Query: {query}

Your Answer:"""

    print("\nGenerating answer...")
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Error generating answer."


def ask_question(query, top_k=5):
    """Main function to ask a question and get an answer."""
    print("=" * 60)
    print(f"Query: {query}")
    print("=" * 60)

    # Search for relevant chunks
    relevant_chunks = search_similar_chunks(query, top_k)

    if not relevant_chunks:
        print("\nNo relevant information found.")
        return None

    # Generate answer
    answer = generate_answer(query, relevant_chunks)

    print("\n" + "=" * 60)
    print("ANSWER:")
    print("=" * 60)
    print(answer)
    print("=" * 60)

    return answer


if __name__ == "__main__":

    print("Recipe Assistant\n")

    query = input(
        "Ask your question about recipes : ").strip()

    if not query:
        query = "How do I make egg fried rice?"

    ask_question(query, top_k=3)
