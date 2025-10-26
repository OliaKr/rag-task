# Simple RAG Pipeline

This project implements a RAG (Retrieval-Augmented Generation) pipeline that answers questions about recipe documents. It works by embedding document chunks and retrieving the most relevant ones to generate accurate answers.

The project uses Google Gemini API for text embeddings, OpenAI GPT-4o-mini for answer generation, and PostgreSQL for storing chunks and embeddings. Document processing is handled through LangChain.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Set up PostgreSQL locally or using Docker:

```bash
docker run --name rag-postgres -e POSTGRES_USER=youruser -e POSTGRES_PASSWORD=yourpassword -e POSTGRES_DB=rag_db -p 5432:5432 -d postgres
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
POSTGRES_URL=postgresql+psycopg2://<user>:<password>@localhost:5432/<db_name>
OPENAI_API_KEY=your_openai_api_key_here
```

## Dependencies

- python-dotenv
- langchain
- langchain-community
- langchain-google-genai
- langchain-openai
- psycopg2-binary
- SQLAlchemy
- pypdf
- docx2txt
- numpy

## Usage

Initialize the database:

```bash
python database_init.py
```

Index the recipe document:

```bash
python index_documents.py
```

Run queries:

```bash
python search_documents.py
```

## Example

**Query:** What ingredients do I need for beef in beer?

**Response:**

```
For the Beef in Beer recipe, you will need the following ingredients:

- 500g of cheap beef pieces (stewing steak is usually a good option)
- 500 mls of real ale
- 4 large onions
- 2 fat cloves of garlic
- 1 tablespoon of plain flour

These ingredients will help you prepare a delicious dish!
```

## How It Works

### Document Indexing (`index_documents.py`)

This script processes the recipe PDF and prepares it for search:

- Loads the PDF document
- Splits it into 600-character chunks with 60-character overlap
- Generates embeddings for each chunk using Google Gemini
- Stores chunks and embeddings in PostgreSQL

### Query System (`search_documents.py`)

This script searches and generates answers for user queries:

- Converts your question into an embedding
- Finds the most similar chunks using cosine similarity
- Passes relevant chunks to OpenAI GPT as context
- Generates an answer based on the retrieved information

You can ask questions interactively or press Enter to use the default example.

### Database Schema

The PostgreSQL table stores document chunks and their embeddings.

CREATE TABLE IF NOT EXISTS document_chunks (
id SERIAL PRIMARY KEY,
chunk_content TEXT NOT NULL,
embedding REAL[] NOT NULL,
source_file TEXT NOT NULL,
chunking_method TEXT NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

The field names in my table are functionally identical to those in the assignment,
with only minor naming adjustments for consistency:

`chunk_content` = `chunk_text`

`source_file` = `filename`

`chunking_method` = `split_strategy`

### Data Cleaning and Normalization

No additional data cleaning or text normalization was performed.
The source document (“Easy Recipes.pdf”) was already clean and well-structured.
In larger or unstructured datasets, cleaning and normalization would be essential
to ensure consistent chunking and embedding quality.

### Additional files

- `database_init.py` - Sets up the PostgreSQL database and creates the schema
- `db_inspector.py` - View stored chunks and database statistics
- `db_cleaner.py` - Clean up or reset database records
