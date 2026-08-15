from fastapi import APIRouter
from app.config import settings
from app.models.schemas import HealthResponse
from app.services.vector_store import vector_store

router = APIRouter(prefix="/api/v1", tags=["Health & Status"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Returns application health, collection statistics, and configuration status."""
    total_chunks = vector_store.count()
    docs = vector_store.list_documents()
    has_api_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())

    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        gemini_configured=has_api_key,
        total_indexed_chunks=total_chunks,
        total_documents=len(docs)
    )
