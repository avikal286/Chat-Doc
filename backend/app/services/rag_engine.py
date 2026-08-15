from typing import List, Dict, Any, Optional
from app.config import settings
from app.models.schemas import Citation, QueryResponse, ChatMessage, ChatResponse
from app.services.embeddings import GeminiEmbeddingService
from app.services.vector_store import vector_store


class RAGEngine:
    """
    Orchestrates the 4-Stage RAG Pipeline:
    1. Query Embedding
    2. Context Retrieval (Semantic Search)
    3. Prompt Augmentation & Grounding
    4. LLM Generation with Citations
    """

    SYSTEM_PROMPT = """You are an intelligent, factual Document Q&A assistant.
Your task is to answer the user's question accurately and strictly based on the provided document excerpts (Context).

Rules:
1. Base your answer ONLY on the provided context excerpts. Do not fabricate information.
2. If the context does not contain sufficient information to answer the question, state: "Based on the provided documents, I could not find information to answer this question." Do not make up facts.
3. Be clear, concise, well-structured (use bullet points or markdown when helpful).
4. Explicitly refer to the relevant source document name and page number when discussing facts.
"""

    def __init__(self):
        self.embedding_service = GeminiEmbeddingService()

    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> QueryResponse:
        """
        Executes single-turn RAG: retrieves relevant chunks, augments prompt, and calls Gemini LLM.
        """
        k = top_k or settings.TOP_K_RESULTS
        active_key = api_key or settings.GEMINI_API_KEY
        active_model = model or settings.LLM_MODEL

        # Step 1: Embed Query
        query_embedding = self.embedding_service.get_query_embedding(question, api_key=active_key)

        # Step 2: Retrieve Top-K Chunks from Vector Store
        retrieved_chunks = vector_store.search_similar(query_embedding, top_k=k)

        # Build Citations
        citations: List[Citation] = []
        for c in retrieved_chunks:
            citations.append(
                Citation(
                    document_id=c["document_id"],
                    filename=c["filename"],
                    page_number=c.get("page_number"),
                    chunk_index=c["chunk_index"],
                    snippet=c["text"][:300] + ("..." if len(c["text"]) > 300 else ""),
                    similarity_score=c["similarity_score"]
                )
            )

        if not retrieved_chunks:
            return QueryResponse(
                question=question,
                answer="No documents have been uploaded or indexed yet. Please upload a PDF, DOCX, or TXT document first!",
                citations=[],
                model_used=active_model,
                sources_count=0
            )

        # Step 3: Augment Context
        context_str = self._format_context(retrieved_chunks)
        user_prompt = f"### Document Context:\n{context_str}\n\n### User Question:\n{question}\n\n### Answer:"

        # Step 4: Generate Answer with Gemini
        answer = self._generate_response(
            system_instruction=self.SYSTEM_PROMPT,
            prompt=user_prompt,
            api_key=active_key,
            model=active_model
        )

        return QueryResponse(
            question=question,
            answer=answer,
            citations=citations,
            model_used=active_model,
            sources_count=len(citations)
        )

    def chat(
        self,
        messages: List[ChatMessage],
        top_k: Optional[int] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> ChatResponse:
        """
        Executes multi-turn conversational RAG using recent message history and retrieved context.
        """
        k = top_k or settings.TOP_K_RESULTS
        active_key = api_key or settings.GEMINI_API_KEY
        active_model = model or settings.LLM_MODEL

        # Get latest user question
        user_messages = [m for m in messages if m.role == "user"]
        latest_question = user_messages[-1].content if user_messages else ""

        if not latest_question:
            return ChatResponse(
                response="Please provide a message to chat.",
                citations=[],
                model_used=active_model
            )

        # Step 1 & 2: Embed and Retrieve
        query_embedding = self.embedding_service.get_query_embedding(latest_question, api_key=active_key)
        retrieved_chunks = vector_store.search_similar(query_embedding, top_k=k)

        citations: List[Citation] = [
            Citation(
                document_id=c["document_id"],
                filename=c["filename"],
                page_number=c.get("page_number"),
                chunk_index=c["chunk_index"],
                snippet=c["text"][:300] + ("..." if len(c["text"]) > 300 else ""),
                similarity_score=c["similarity_score"]
            )
            for c in retrieved_chunks
        ]

        # Step 3: Format Context & Conversation History
        context_str = self._format_context(retrieved_chunks)
        history_text = "\n".join([f"{m.role.capitalize()}: {m.content}" for m in messages[:-1]])

        prompt = f"### Document Context:\n{context_str}\n\n"
        if history_text:
            prompt += f"### Previous Conversation:\n{history_text}\n\n"
        prompt += f"### Current User Question:\n{latest_question}\n\n### Answer:"

        # Step 4: Generate Answer
        response_text = self._generate_response(
            system_instruction=self.SYSTEM_PROMPT,
            prompt=prompt,
            api_key=active_key,
            model=active_model
        )

        return ChatResponse(
            response=response_text,
            citations=citations,
            model_used=active_model
        )

    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        formatted = []
        for i, c in enumerate(chunks):
            page_info = f", Page {c['page_number']}" if c.get("page_number") else ""
            header = f"[Excerpt {i+1} | Source: {c['filename']}{page_info} | Relevance: {int(c['similarity_score']*100)}%]"
            formatted.append(f"{header}\n{c['text']}")
        return "\n\n---\n\n".join(formatted)

    def _generate_response(
        self,
        system_instruction: str,
        prompt: str,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash"
    ) -> str:
        """Calls Gemini API or provides testing mock response."""
        active_key = api_key or settings.GEMINI_API_KEY
        if active_key:
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=active_key)
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2, # Low temperature for factual precision
                    )
                )
                return response.text.strip() if response.text else "No response generated."
            except Exception as e:
                return f"Error communicating with Gemini API: {str(e)}"
        else:
            return (
                "⚠️ **Gemini API Key is not configured.**\n\n"
                "To generate live AI answers, please configure your `GEMINI_API_KEY` in the `.env` file or enter it in the header settings in the UI.\n\n"
                "*(The vector search and chunk retrieval pipeline worked successfully and retrieved the matching citations listed below!)*"
            )


# Global singleton
rag_engine = RAGEngine()
