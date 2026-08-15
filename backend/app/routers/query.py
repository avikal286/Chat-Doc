from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query as FastQuery, status
from app.models.schemas import QueryRequest, QueryResponse, ChatRequest, ChatResponse, Citation
from app.services.rag_engine import rag_engine
from app.services.embeddings import GeminiEmbeddingService
from app.services.vector_store import vector_store

router = APIRouter(prefix="/api/v1", tags=["RAG & Query"])


@router.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    """
    Execute single-turn RAG:
    1. Embed query
    2. Retrieve top-k chunks from ChromaDB
    3. Ground prompt and generate factual response using Google Gemini
    4. Return answer + source citations
    """
    try:
        return rag_engine.query(
            question=request.question,
            top_k=request.top_k,
            api_key=request.gemini_api_key,
            model=request.model
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponse)
def chat_with_documents(request: ChatRequest):
    """
    Multi-turn Conversational RAG:
    Maintains message history + retrieves relevant chunks for the latest question.
    """
    try:
        return rag_engine.chat(
            messages=request.messages,
            top_k=request.top_k,
            api_key=request.gemini_api_key,
            model=request.model
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat execution failed: {str(e)}"
        )


@router.get("/preview-retrieval", response_model=List[Citation])
def preview_retrieval(
    question: str = FastQuery(..., min_length=2, description="Search query"),
    top_k: int = FastQuery(4, ge=1, le=10, description="Top-K results"),
    gemini_api_key: Optional[str] = FastQuery(None, description="Optional API key")
):
    """
    Debug & Inspection endpoint:
    Performs purely vector similarity search and returns retrieved chunks with relevance scores without calling LLM.
    """
    try:
        embedding_service = GeminiEmbeddingService(api_key=gemini_api_key)
        q_emb = embedding_service.get_query_embedding(question, api_key=gemini_api_key)
        chunks = vector_store.search_similar(q_emb, top_k=top_k)
        return [
            Citation(
                document_id=c["document_id"],
                filename=c["filename"],
                page_number=c.get("page_number"),
                chunk_index=c["chunk_index"],
                snippet=c["text"][:300] + ("..." if len(c["text"]) > 300 else ""),
                similarity_score=c["similarity_score"]
            )
            for c in chunks
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval preview failed: {str(e)}"
        )
