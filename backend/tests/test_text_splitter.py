from app.services.text_splitter import RecursiveCharacterTextSplitter


def test_text_splitter_basic():
    splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
    sample_text = (
        "Retrieval-Augmented Generation (RAG) is an AI framework. "
        "It retrieves facts from an external knowledge base. "
        "This grounds the Large Language Model and prevents hallucinations."
    )
    chunks = splitter.split_text(sample_text)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 100  # Within reasonable bounds


def test_text_splitter_split_documents():
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    docs = [
        {"text": "Page 1: Introduction to Vector Databases. Vector DB stores high-dimensional embeddings.", "page_number": 1},
        {"text": "Page 2: Cosine similarity measures angle between two vectors. It ranges from -1 to 1.", "page_number": 2}
    ]
    chunks = splitter.split_documents(docs, document_id="doc_123", filename="vectors.pdf")

    assert len(chunks) >= 2
    assert chunks[0]["metadata"]["document_id"] == "doc_123"
    assert chunks[0]["metadata"]["filename"] == "vectors.pdf"
    assert chunks[0]["metadata"]["page_number"] in [1, 2]
    assert "chunk_id" in chunks[0]
