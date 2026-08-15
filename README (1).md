# Chat-Doc

A document Q&A app built using RAG (Retrieval Augmented Generation). Upload a document and ask questions about it — the app finds the relevant parts and answers using Google Gemini.

## Features

- Upload PDF, DOCX, TXT or MD files
- Automatic text extraction + chunking
- Vector search using ChromaDB
- Answers grounded in your document, with source citations
- Multi-turn chat (remembers previous questions in the conversation)
- Preview endpoint to see raw retrieved chunks without calling the LLM

## Tech Stack

**Backend:** FastAPI, ChromaDB, Google Gemini (for embeddings + generation)

**Frontend:** React + Vite

## How it works

1. You upload a document
2. Text is extracted and split into chunks
3. Each chunk is converted into an embedding (via Gemini) and stored in ChromaDB
4. When you ask a question, it's embedded too and matched against the stored chunks
5. The most relevant chunks are sent to Gemini along with your question to generate an answer

## Project Structure

```
backend/
  app/
    routers/      -> API endpoints (documents, query, health)
    services/     -> document loader, text splitter, embeddings, vector store, rag engine
    models/       -> request/response schemas
  run.py          -> starts the server

frontend/
  src/
    components/   -> chat UI, upload, citations, settings etc.
```

## Running it locally

### Backend

```bash
cd backend
pip install fastapi uvicorn chromadb pydantic-settings python-multipart python-docx pypdf google-genai
```

Create a `.env` file inside `backend/`:

```
GEMINI_API_KEY=your_gemini_api_key
```

Then run:

```bash
python run.py
```

Backend will start at `http://localhost:8000`, API docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/documents/upload` | Upload and index a document |
| GET | `/api/v1/documents` | List all indexed documents |
| DELETE | `/api/v1/documents/{id}` | Delete a document |
| DELETE | `/api/v1/documents` | Clear all documents |
| POST | `/api/v1/query` | Ask a single question |
| POST | `/api/v1/chat` | Multi-turn chat with documents |
| GET | `/api/v1/preview-retrieval` | See retrieved chunks (no LLM call) |
| GET | `/api/v1/health` | Health check |

## Note

You'll need a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) to run this.
