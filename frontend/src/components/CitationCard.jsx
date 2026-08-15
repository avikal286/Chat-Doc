import React, { useState } from 'react';
import { Bookmark, ExternalLink, X, Percent, FileText } from 'lucide-react';

export default function CitationCard({ citation, index }) {
  const [isOpen, setIsOpen] = useState(false);

  const percentage = Math.round(citation.similarity_score * 100);

  return (
    <>
      <button
        className="citation-chip"
        onClick={() => setIsOpen(true)}
        title="Click to view retrieved chunk excerpt"
      >
        <FileText size={12} />
        <span>{citation.filename}</span>
        {citation.page_number && <span>(p. {citation.page_number})</span>}
        <span className="score-badge">{percentage}% match</span>
      </button>

      {/* Excerpt Modal */}
      {isOpen && (
        <div className="modal-overlay" onClick={() => setIsOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Bookmark size={18} color="var(--accent-cyan)" />
                <h3 className="modal-title">Source Excerpt #{index + 1}</h3>
              </div>
              <button className="btn-delete" onClick={() => setIsOpen(false)}>
                <X size={18} />
              </button>
            </div>

            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              <div><strong>Document:</strong> {citation.filename}</div>
              {citation.page_number && <div><strong>Page:</strong> {citation.page_number}</div>}
              <div><strong>Chunk Index:</strong> {citation.chunk_index}</div>
              <div><strong>Relevance Score:</strong> {percentage}%</div>
            </div>

            <div className="citation-snippet-box">
              {citation.snippet}
            </div>

            <div style={{ marginTop: '1.25rem', textAlign: 'right' }}>
              <button className="btn-icon" onClick={() => setIsOpen(false)} style={{ marginLeft: 'auto' }}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
