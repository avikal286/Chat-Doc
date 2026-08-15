import React from 'react';
import { Layers, Settings, BookOpen, Database, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Header({
  health,
  onOpenSettings,
  onOpenInterviewGuide
}) {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-logo">
          <Layers size={20} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h1 className="brand-title">DocuRAG</h1>
            <span className="brand-badge">Gemini RAG</span>
          </div>
        </div>
      </div>

      <div className="header-actions">
        {/* Backend status pill */}
        <div className="status-pill">
          <span className={`status-dot ${isHealthy ? '' : 'disconnected'}`}></span>
          <span>{isHealthy ? 'Backend Connected' : 'Connecting...'}</span>
          {isHealthy && (
            <span style={{ color: 'var(--accent-cyan)', marginLeft: '0.25rem', fontWeight: 600 }}>
              ({health.total_indexed_chunks} chunks)
            </span>
          )}
        </div>

        {/* Interview Guide Button */}
        <button
          className="btn-icon btn-interview"
          onClick={onOpenInterviewGuide}
          title="Learn the 4-Stage RAG Pipeline for Interviews"
        >
          <BookOpen size={16} />
          <span>Interview Guide</span>
        </button>

        {/* Settings Button */}
        <button
          className="btn-icon"
          onClick={onOpenSettings}
          title="Configure API Key & Search Parameters"
        >
          <Settings size={16} />
          <span>Settings</span>
        </button>
      </div>
    </header>
  );
}
