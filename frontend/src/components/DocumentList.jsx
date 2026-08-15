import React from 'react';
import { FileText, Trash2, Database, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function DocumentList({ documents, onDocumentDeleted, onClearAll }) {
  const handleDelete = async (docId, filename) => {
    if (confirm(`Remove "${filename}" and its vector embeddings?`)) {
      try {
        await api.deleteDocument(docId);
        if (onDocumentDeleted) onDocumentDeleted();
      } catch (err) {
        alert(err.message || 'Failed to delete document');
      }
    }
  };

  const handleClearAll = async () => {
    if (confirm('Clear all indexed documents and reset vector store?')) {
      try {
        await api.clearAllDocuments();
        if (onClearAll) onClearAll();
      } catch (err) {
        alert(err.message || 'Failed to clear documents');
      }
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
      <div className="section-title">
        <span>Indexed Documents ({documents.length})</span>
        {documents.length > 0 && (
          <button
            onClick={handleClearAll}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: '0.72rem',
              cursor: 'pointer',
              textDecoration: 'underline',
            }}
          >
            Clear All
          </button>
        )}
      </div>

      {documents.length === 0 ? (
        <div
          style={{
            padding: '1.25rem',
            textAlign: 'center',
            color: 'var(--text-muted)',
            fontSize: '0.8rem',
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: 'var(--radius-md)',
            border: '1px dashed var(--border-color)',
          }}
        >
          <Database size={20} style={{ margin: '0 auto 0.4rem', opacity: 0.5 }} />
          <div>No documents indexed yet.</div>
          <div style={{ fontSize: '0.72rem', marginTop: '0.2rem' }}>
            Upload a file above to begin Q&A.
          </div>
        </div>
      ) : (
        <div className="doc-list">
          {documents.map((doc) => (
            <div key={doc.document_id} className="doc-card">
              <div className="doc-info">
                <FileText size={16} className="doc-icon" />
                <div className="doc-meta">
                  <span className="doc-name" title={doc.filename}>
                    {doc.filename}
                  </span>
                  <span className="doc-stats">
                    {doc.total_chunks} {doc.total_chunks === 1 ? 'chunk' : 'chunks'}
                  </span>
                </div>
              </div>
              <button
                className="btn-delete"
                onClick={() => handleDelete(doc.document_id, doc.filename)}
                title="Delete document"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
