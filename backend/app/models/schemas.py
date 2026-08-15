from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str = Field(..., description="Unique ID of the document")
    filename: str = Field(..., description="Source document file name")
    page_number: Optional[int] = Field(None, description="Page number if available")
    chunk_index: int = Field(..., description="Index of chunk within the document")
    snippet: str = Field(..., description="Excerpt of the retrieved chunk")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2, description="The question to ask about the documents")
    top_k: Optional[int] = Field(default=None, ge=1, le=10, description="Number of source chunks to retrieve")
    gemini_api_key: Optional[str] = Field(default=None, description="Optional override Gemini API Key")
    model: Optional[str] = Field(default=None, description="Optional Gemini model override")


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation]
    model_used: str
    sources_count: int


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1, description="Chat conversation history")
    top_k: Optional[int] = Field(default=None, ge=1, le=10, description="Number of source chunks to retrieve")
    gemini_api_key: Optional[str] = Field(default=None, description="Optional override Gemini API Key")
    model: Optional[str] = Field(default=None, description="Optional Gemini model override")


class ChatResponse(BaseModel):
    response: str
    citations: List[Citation]
    model_used: str


class DocumentMeta(BaseModel):
    document_id: str
    filename: str
    total_chunks: int
    file_size_bytes: int
    uploaded_at: str


class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    chunks_indexed: int


class DocumentListResponse(BaseModel):
    documents: List[DocumentMeta]
    total_documents: int
    total_chunks: int


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    gemini_configured: bool
    total_indexed_chunks: int
    total_documents: int
