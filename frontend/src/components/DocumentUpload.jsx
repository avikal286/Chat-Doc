import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function DocumentUpload({ onUploadSuccess, apiKey, chunkSize, chunkOverlap }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const fileInputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file) return;

    // Check extension
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'txt', 'md'].includes(ext)) {
      setStatusMessage({
        type: 'error',
        text: 'Unsupported file type. Please upload PDF, DOCX, TXT, or MD.',
      });
      return;
    }

    setIsUploading(true);
    setStatusMessage(null);

    try {
      const res = await api.uploadDocument(file, apiKey, chunkSize, chunkOverlap);
      setStatusMessage({
        type: 'success',
        text: `Indexed "${res.filename}" into ${res.chunks_indexed} vector chunks!`,
      });
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      setStatusMessage({
        type: 'error',
        text: err.message || 'Failed to upload document.',
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  return (
    <div>
      <div className="section-title">
        <span>Ingest Document</span>
      </div>

      <div
        className={`dropzone ${isDragging ? 'active' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])}
          disabled={isUploading}
        />

        <div className="dropzone-icon">
          {isUploading ? (
            <Loader2 size={24} className="animate-spin" />
          ) : (
            <UploadCloud size={24} />
          )}
        </div>

        <div className="dropzone-text">
          {isUploading ? 'Chunking & Embedding...' : 'Upload PDF, DOCX, or TXT'}
        </div>
        <div className="dropzone-hint">Click or drag & drop file to index</div>
      </div>

      {statusMessage && (
        <div
          style={{
            marginTop: '0.75rem',
            padding: '0.6rem 0.75rem',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.78rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            background:
              statusMessage.type === 'success'
                ? 'rgba(16, 185, 129, 0.1)'
                : 'rgba(244, 63, 94, 0.1)',
            border: `1px solid ${
              statusMessage.type === 'success'
                ? 'rgba(16, 185, 129, 0.3)'
                : 'rgba(244, 63, 94, 0.3)'
            }`,
            color: statusMessage.type === 'success' ? '#6ee7b7' : '#fda4af',
          }}
        >
          {statusMessage.type === 'success' ? (
            <CheckCircle size={14} flexShrink={0} />
          ) : (
            <AlertCircle size={14} flexShrink={0} />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}
    </div>
  );
}
