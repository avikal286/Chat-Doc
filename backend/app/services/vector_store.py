from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings


class VectorStoreService:
    """
    Manages persistent ChromaDB vector storage, indexing, and similarity search.
    """

    COLLECTION_NAME = "rag_document_chunks"

    def __init__(self, persist_directory: str = None):
        self.persist_dir = persist_directory or settings.CHROMA_PERSIST_DIR
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> int:
        """
        Inserts text chunks, their embeddings, and metadata into ChromaDB.
        """
        if not chunks or not embeddings:
            return 0

        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        # ChromaDB accepts batch upsert
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        return len(ids)

    def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Performs cosine similarity search against stored chunk embeddings.
        Returns a list of ranked chunk records with similarity scores.
        """
        total_items = self.collection.count()
        if total_items == 0:
            return []

        actual_k = min(top_k, total_items)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_k,
            include=["documents", "metadatas", "distances"]
        )

        matched_chunks = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else []
            distances = results["distances"][0] if "distances" in results else []

            for i in range(len(docs)):
                dist = distances[i] if i < len(distances) else 0.5
                # For cosine distance: cosine_distance = 1 - cosine_similarity
                # So cosine_similarity = 1 - distance (clamped between 0 and 1)
                similarity = max(0.0, min(1.0, 1.0 - dist))
                
                meta = metas[i] if i < len(metas) else {}
                matched_chunks.append({
                    "chunk_id": meta.get("chunk_id", f"chunk_{i}"),
                    "document_id": meta.get("document_id", "unknown"),
                    "filename": meta.get("filename", "unknown"),
                    "page_number": meta.get("page_number", 1),
                    "chunk_index": meta.get("chunk_index", i),
                    "text": docs[i],
                    "similarity_score": round(similarity, 4)
                })

        return matched_chunks

    def delete_document(self, document_id: str) -> int:
        """Deletes all chunks belonging to a specific document ID."""
        existing = self.collection.get(
            where={"document_id": document_id}
        )
        if existing and existing["ids"]:
            self.collection.delete(ids=existing["ids"])
            return len(existing["ids"])
        return 0

    def list_documents(self) -> List[Dict[str, Any]]:
        """Aggregates all unique documents and their chunk counts."""
        all_data = self.collection.get(include=["metadatas"])
        if not all_data or not all_data["metadatas"]:
            return []

        doc_summary: Dict[str, Dict[str, Any]] = {}
        for meta in all_data["metadatas"]:
            doc_id = meta.get("document_id", "unknown")
            filename = meta.get("filename", "Unknown Document")
            if doc_id not in doc_summary:
                doc_summary[doc_id] = {
                    "document_id": doc_id,
                    "filename": filename,
                    "total_chunks": 0,
                    "file_size_bytes": 0,
                    "uploaded_at": meta.get("uploaded_at", "")
                }
            doc_summary[doc_id]["total_chunks"] += 1

        return list(doc_summary.values())

    def count(self) -> int:
        """Returns the total number of indexed chunks."""
        return self.collection.count()

    def clear(self) -> None:
        """Removes the entire collection."""
        self.client.delete_collection(name=self.COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )


# Global singleton instance for easy import across routers
vector_store = VectorStoreService()
