import React, { useState } from 'react';
import { X, Key, Sliders, ShieldCheck, Check } from 'lucide-react';

export default function SettingsModal({
  isOpen,
  onClose,
  apiKey,
  setApiKey,
  topK,
  setTopK,
  model,
  setModel,
  chunkSize,
  setChunkSize,
  chunkOverlap,
  setChunkOverlap,
}) {
  const [localKey, setLocalKey] = useState(apiKey || '');
  const [localTopK, setLocalTopK] = useState(topK || 4);
  const [localModel, setLocalModel] = useState(model || 'gemini-2.0-flash');
  const [localChunkSize, setLocalChunkSize] = useState(chunkSize || 600);
  const [localOverlap, setLocalOverlap] = useState(chunkOverlap || 120);
  const [isSaved, setIsSaved] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    setApiKey(localKey);
    setTopK(localTopK);
    setModel(localModel);
    setChunkSize(localChunkSize);
    setChunkOverlap(localOverlap);

    localStorage.setItem('gemini_api_key', localKey);
    localStorage.setItem('top_k', localTopK);
    localStorage.setItem('rag_model', localModel);

    setIsSaved(true);
    setTimeout(() => {
      setIsSaved(false);
      onClose();
    }, 600);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Sliders size={20} color="var(--accent-blue)" />
            <h2 className="modal-title">RAG & Model Settings</h2>
          </div>
          <button className="btn-delete" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div>
          {/* Gemini API Key */}
          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Key size={14} />
              <span>Google Gemini API Key</span>
            </label>
            <input
              type="password"
              className="form-input"
              placeholder="AIzaSy..."
              value={localKey}
              onChange={(e) => setLocalKey(e.target.value)}
            />
            <div className="form-help">
              Stored locally in your browser. If left empty, the server's `.env` key is used.
            </div>
          </div>

          {/* Model Selector */}
          <div className="form-group">
            <label className="form-label">Gemini Generation Model</label>
            <select
              className="form-select"
              value={localModel}
              onChange={(e) => setLocalModel(e.target.value)}
            >
              <option value="gemini-2.0-flash">gemini-2.0-flash (Fastest & Recommended)</option>
              <option value="gemini-1.5-flash">gemini-1.5-flash</option>
              <option value="gemini-1.5-pro">gemini-1.5-pro (High Reasoning)</option>
            </select>
          </div>

          {/* Top-K Chunks */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
              <label className="form-label" style={{ margin: 0 }}>
                Top-K Chunks Retrieved: <strong>{localTopK}</strong>
              </label>
            </div>
            <input
              type="range"
              min="1"
              max="8"
              step="1"
              value={localTopK}
              onChange={(e) => setLocalTopK(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--accent-blue)' }}
            />
            <div className="form-help">
              Number of most similar text chunks passed to the LLM as context.
            </div>
          </div>

          {/* Chunk Size & Overlap */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Chunk Size (chars)</label>
              <input
                type="number"
                className="form-input"
                value={localChunkSize}
                onChange={(e) => setLocalChunkSize(Number(e.target.value))}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Chunk Overlap (chars)</label>
              <input
                type="number"
                className="form-input"
                value={localOverlap}
                onChange={(e) => setLocalOverlap(Number(e.target.value))}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '1.5rem' }}>
            <button className="btn-icon" onClick={onClose}>
              Cancel
            </button>
            <button
              className="btn-icon"
              onClick={handleSave}
              style={{
                background: isSaved ? 'var(--accent-emerald)' : 'var(--accent-blue)',
                color: 'white',
                border: 'none',
              }}
            >
              {isSaved ? <Check size={16} /> : null}
              <span>{isSaved ? 'Saved!' : 'Save Settings'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
