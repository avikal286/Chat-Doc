import React from 'react';
import { X, BookOpen, Layers, Search, Cpu, CheckCircle, HelpCircle } from 'lucide-react';

export default function InterviewGuideModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 760 }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <BookOpen size={20} color="var(--accent-blue)" />
            <h2 className="modal-title">RAG Architecture & Interview Cheatsheet</h2>
          </div>
          <button className="btn-delete" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Quick Pitch */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(6, 182, 212, 0.1))',
              border: '1px solid rgba(59, 130, 246, 0.25)',
              borderRadius: 'var(--radius-md)',
              padding: '1rem',
            }}
          >
            <h3 style={{ fontSize: '0.95rem', color: '#93c5fd', marginBottom: '0.35rem' }}>
              🎯 How to explain this project in an interview (The 30-Second Pitch)
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#e2e8f0', lineHeight: 1.6 }}>
              "I built an end-to-end <strong>Document Question-Answering system using Retrieval-Augmented Generation (RAG)</strong>.
              The backend uses <strong>FastAPI</strong> and <strong>ChromaDB</strong> with <strong>Google Gemini (text-embedding-004)</strong> for vector embeddings and <strong>Gemini 2.0 Flash</strong> for grounded generation.
              When a user uploads a PDF/DOCX, it splits the text into overlapping semantic chunks, vectorizes them into a high-dimensional index, and on each question performs cosine similarity retrieval to inject top-ranked context into the LLM with strict grounding instructions to eliminate hallucinations."
            </p>
          </div>

          {/* 4 Steps */}
          <div>
            <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
              The 4-Stage RAG Pipeline
            </h3>

            <div className="guide-step">
              <h4>1. Document Ingestion & Chunking (`document_loader.py` & `text_splitter.py`)</h4>
              <p>
                Extract text page-by-page from PDFs/DOCX. We use a <strong>Recursive Character Splitter</strong> with a chunk size of 600 characters and 120-character overlap.
                <em> Why overlap?</em> To preserve semantic context across chunk boundaries so phrases aren't cut in half.
              </p>
            </div>

            <div className="guide-step">
              <h4>2. Vector Embedding & Storage (`embeddings.py` & `vector_store.py`)</h4>
              <p>
                Each chunk is passed to <strong>text-embedding-004</strong>, converting text into a 768-dimensional dense vector.
                Vectors and metadata (filename, page number, chunk index) are stored in <strong>ChromaDB</strong> with HNSW indexing.
              </p>
            </div>

            <div className="guide-step">
              <h4>3. Semantic Retrieval (`vector_store.py`)</h4>
              <p>
                When a user asks a question, the query is embedded into the same 768-dim space. ChromaDB computes <strong>Cosine Similarity</strong> to return the top-K most semantically relevant chunks.
              </p>
            </div>

            <div className="guide-step">
              <h4>4. Prompt Augmentation & Grounded Generation (`rag_engine.py`)</h4>
              <p>
                The retrieved chunks are assembled into a structured prompt with system instructions: <em>"Answer strictly based on the provided context excerpts."</em>
                Gemini generates the answer and provides precise citation links with similarity percentages.
              </p>
            </div>
          </div>

          {/* Common Interview Questions */}
          <div>
            <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
              Top Interview Questions & Answers
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ background: 'var(--bg-primary)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-cyan)', marginBottom: '0.25rem' }}>
                  Q: Why use RAG instead of fine-tuning an LLM?
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  RAG is cost-effective, updates dynamically in real-time (just add/delete documents without re-training), provides verifiable citations, and prevents hallucination of private/proprietary data.
                </div>
              </div>

              <div style={{ background: 'var(--bg-primary)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-cyan)', marginBottom: '0.25rem' }}>
                  Q: How do you choose Chunk Size and Overlap?
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  Small chunks (200-400 chars) are specific but risk losing surrounding context. Large chunks (1000+ chars) preserve full context but dilute semantic search precision. Overlap (10-20%) ensures sentences split at chunk boundaries don't lose meaning.
                </div>
              </div>

              <div style={{ background: 'var(--bg-primary)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-cyan)', marginBottom: '0.25rem' }}>
                  Q: How do you prevent hallucinations in RAG?
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  1) Low temperature (0.0 - 0.2) for deterministic responses. 2) Strict system prompt instructing the model to say "I don't know" if facts are absent. 3) Outputting citation mappings for human verification.
                </div>
              </div>
            </div>
          </div>

          <div style={{ textAlign: 'right', marginTop: '0.5rem' }}>
            <button className="btn-icon" onClick={onClose} style={{ marginLeft: 'auto' }}>
              Close Guide
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
