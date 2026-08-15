const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  // Check backend health & statistics
  async getHealth() {
    const res = await fetch(`${API_BASE_URL}/api/v1/health`);
    if (!res.ok) throw new Error('Failed to fetch backend health');
    return res.json();
  },

  // List all uploaded documents
  async getDocuments() {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents`);
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  // Upload document file
  async uploadDocument(file, apiKey = '', chunkSize = 600, chunkOverlap = 120) {
    const formData = new FormData();
    formData.append('file', file);
    if (apiKey) formData.append('gemini_api_key', apiKey);
    if (chunkSize) formData.append('chunk_size', chunkSize);
    if (chunkOverlap) formData.append('chunk_overlap', chunkOverlap);

    const res = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to upload document');
    }
    return res.json();
  },

  // Delete a specific document
  async deleteDocument(documentId) {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete document');
    return res.json();
  },

  // Clear all indexed documents
  async clearAllDocuments() {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to clear documents');
    return res.json();
  },

  // Ask a single question
  async query(question, topK = 4, apiKey = '', model = 'gemini-2.0-flash') {
    const res = await fetch(`${API_BASE_URL}/api/v1/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        top_k: topK,
        gemini_api_key: apiKey || null,
        model: model || null,
      }),
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to execute query');
    }
    return res.json();
  },

  // Multi-turn chat
  async chat(messages, topK = 4, apiKey = '', model = 'gemini-2.0-flash') {
    const res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages,
        top_k: topK,
        gemini_api_key: apiKey || null,
        model: model || null,
      }),
    });
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to execute chat');
    }
    return res.json();
  },
};
