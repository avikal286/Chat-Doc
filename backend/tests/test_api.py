import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "total_indexed_chunks" in data
    assert "total_documents" in data


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "docs_url" in data


def test_upload_and_query_workflow():
    # 1. Clear documents first
    client.delete("/api/v1/documents")

    # 2. Upload sample text document
    sample_content = (
        "Antigravity Flight System Manual\n"
        "Model: AG-9000 Enterprise\n"
        "Max Speed: Mach 12 with quantum propulsion.\n"
        "Safety Protocol: Engage magnetic stabilization before orbital reentry.\n"
    )
    file_bytes = io.BytesIO(sample_content.encode("utf-8"))

    upload_response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("flight_manual.txt", file_bytes, "text/plain")}
    )
    assert upload_response.status_code == 201
    upload_data = upload_response.json()
    assert upload_data["chunks_indexed"] >= 1
    doc_id = upload_data["document_id"]

    # 3. List documents
    list_response = client.get("/api/v1/documents")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total_documents"] >= 1
    assert any(d["filename"] == "flight_manual.txt" for d in list_data["documents"])

    # 4. Preview retrieval
    preview_response = client.get("/api/v1/preview-retrieval?question=What is the max speed?")
    assert preview_response.status_code == 200
    citations = preview_response.json()
    assert len(citations) >= 1
    assert citations[0]["filename"] == "flight_manual.txt"

    # 5. Clean up document
    del_response = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_response.status_code == 200
