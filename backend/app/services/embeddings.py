from typing import List, Optional
import math
import hashlib
from app.config import settings


class GeminiEmbeddingService:
    """
    Handles generating high-dimensional vector embeddings using Google's text-embedding-004.
    Includes batching and graceful fallback for testing/offline environments.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.EMBEDDING_MODEL

    def get_embeddings(self, texts: List[str], api_key: Optional[str] = None) -> List[List[float]]:
        """
        Generates vector embeddings for a list of string chunks.
        """
        active_key = api_key or self.api_key

        if not texts:
            return []

        if active_key:
            try:
                from google import genai
                client = genai.Client(api_key=active_key)
                
                # Google Gemini supports batch embedding calls
                # For safety with rate limits, chunk batch into max 50 items per call
                batch_size = 50
                all_embeddings = []
                
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    response = client.models.embed_content(
                        model=self.model,
                        contents=batch
                    )
                    # Extract embeddings
                    if hasattr(response, "embeddings") and response.embeddings:
                        for emb in response.embeddings:
                            all_embeddings.append(emb.values)
                    else:
                        raise ValueError("No embeddings returned by Gemini API")
                
                return all_embeddings
            except Exception as e:
                # If API call fails, raise informative error or fallback if debugging
                raise RuntimeError(f"Gemini Embedding generation failed: {str(e)}")
        else:
            # Fallback for testing without API key: deterministic 768-dim normalized embedding
            return [self._mock_embedding(t, dim=768) for t in texts]

    def get_query_embedding(self, query: str, api_key: Optional[str] = None) -> List[float]:
        """Generates embedding for a single search query."""
        results = self.get_embeddings([query], api_key=api_key)
        return results[0]

    @staticmethod
    def _mock_embedding(text: str, dim: int = 768) -> List[float]:
        """Generates a deterministic pseudo-vector for local unit testing."""
        vec = []
        for i in range(dim):
            seed = f"{text}_{i}"
            h = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16)
            vec.append((h % 1000) / 1000.0 - 0.5)
        # Normalize to unit length
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]
