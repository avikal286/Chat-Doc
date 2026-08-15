import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from app.config import settings
from app.models.schemas import UploadResponse, DocumentListResponse, DocumentMeta
from app.services.document_loader import DocumentLoader
from app.services.text_splitter import RecursiveCharacterTextSplitter
from app.services.embeddings import GeminiEmbeddingService
from app.services.vector_store import vector_store

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="The document file (PDF, DOCX, TXT, MD)"),
    gemini_api_key: Optional[str] = Form(None, description="Optional override Gemini API Key"),
    chunk_size: Optional[int] = Form(None, description="Chunk size in characters"),
    chunk_overlap: Optional[int] = Form(None, description="Chunk overlap in characters")
):
    """
    Ingest a document:
    1. Saves file to upload storage
    2. Extracts text & page metadata
    3. Chunks text using recursive splitter
    4. Generates vector embeddings via Gemini
    5. Indexes into ChromaDB vector database
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in DocumentLoader.SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(DocumentLoader.SUPPORTED_EXTENSIONS)}"
        )

    doc_id = str(uuid.uuid4())
    safe_filename = f"{doc_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    try:
        # 1. Save uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Extract text & pages
        raw_pages = DocumentLoader.load_document(file_path, original_filename=file.filename)

        # 3. Chunk text
        active_chunk_size = chunk_size or settings.CHUNK_SIZE
        active_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=active_chunk_size,
            chunk_overlap=active_overlap
        )
        chunks = splitter.split_documents(
            docs=raw_pages,
            document_id=doc_id,
            filename=file.filename
        )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract any readable text from the uploaded document."
            )

        # Add upload timestamp to metadata
        uploaded_at = datetime.now().isoformat()
        file_size = os.path.getsize(file_path)
        for chunk in chunks:
            chunk["metadata"]["uploaded_at"] = uploaded_at
            chunk["metadata"]["file_size_bytes"] = file_size

        # 4. Generate embeddings
        embedding_service = GeminiEmbeddingService(api_key=gemini_api_key)
        chunk_texts = [c["text"] for c in chunks]
        embeddings = embedding_service.get_embeddings(chunk_texts, api_key=gemini_api_key)

        # 5. Store in ChromaDB
        indexed_count = vector_store.add_chunks(chunks, embeddings)

        return UploadResponse(
            message="Document successfully processed and indexed into vector database.",
            document_id=doc_id,
            filename=file.filename,
            chunks_indexed=indexed_count
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("", response_model=DocumentListResponse)
def list_documents():
    """Returns a list of all currently indexed documents and chunk statistics."""
    docs = vector_store.list_documents()
    total_chunks = vector_store.count()
    return DocumentListResponse(
        documents=[DocumentMeta(**d) for d in docs],
        total_documents=len(docs),
        total_chunks=total_chunks
    )


@router.delete("/{document_id}")
def delete_document(document_id: str):
    """Deletes all chunks associated with a specific document from the vector store."""
    deleted_chunks = vector_store.delete_document(document_id)
    if deleted_chunks == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found."
        )
    return {
        "message": f"Successfully deleted document '{document_id}'",
        "deleted_chunks": deleted_chunks
    }


@router.delete("")
def clear_all_documents():
    """Clears all indexed documents and resets the vector store."""
    vector_store.clear()
    return {"message": "All indexed documents and vector collections have been cleared."}
