import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';
import SettingsModal from './components/SettingsModal';
import InterviewGuideModal from './components/InterviewGuideModal';
import { api } from './services/api';

export default function App() {
  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isGuideOpen, setIsGuideOpen] = useState(false);

  // User Settings
  const [apiKey, setApiKey] = useState(localStorage.getItem('gemini_api_key') || '');
  const [topK, setTopK] = useState(Number(localStorage.getItem('top_k')) || 4);
  const [model, setModel] = useState(localStorage.getItem('rag_model') || 'gemini-2.0-flash');
  const [chunkSize, setChunkSize] = useState(600);
  const [chunkOverlap, setChunkOverlap] = useState(120);

  const fetchHealthAndDocs = async () => {
    try {
      const hData = await api.getHealth();
      setHealth(hData);
      const dData = await api.getDocuments();
      setDocuments(dData.documents || []);
    } catch (err) {
      console.warn('Backend currently unreachable, retrying...', err);
    }
  };

  useEffect(() => {
    fetchHealthAndDocs();
    const interval = setInterval(fetchHealthAndDocs, 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      {/* Header */}
      <Header
        health={health}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenInterviewGuide={() => setIsGuideOpen(true)}
      />

      {/* Main Split Layout */}
      <main className="main-layout">
        {/* Left Sidebar */}
        <aside className="sidebar">
          {/* Document Ingestion Zone */}
          <DocumentUpload
            onUploadSuccess={fetchHealthAndDocs}
            apiKey={apiKey}
            chunkSize={chunkSize}
            chunkOverlap={chunkOverlap}
          />

          {/* Quick RAG Stats */}
          <div className="rag-stats-box">
            <div className="stat-item">
              <h4>{documents.length}</h4>
              <span>Documents</span>
            </div>
            <div className="stat-item">
              <h4>{health?.total_indexed_chunks || 0}</h4>
              <span>Vector Chunks</span>
            </div>
            <div className="stat-item">
              <h4>{topK}</h4>
              <span>Top-K Chunks</span>
            </div>
          </div>

          {/* Document Manager */}
          <DocumentList
            documents={documents}
            onDocumentDeleted={fetchHealthAndDocs}
            onClearAll={fetchHealthAndDocs}
          />
        </aside>

        {/* Right Chat & Q&A Area */}
        <ChatInterface
          hasDocuments={documents.length > 0}
          apiKey={apiKey}
          topK={topK}
          model={model}
          onOpenInterviewGuide={() => setIsGuideOpen(true)}
        />
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        apiKey={apiKey}
        setApiKey={setApiKey}
        topK={topK}
        setTopK={setTopK}
        model={model}
        setModel={setModel}
        chunkSize={chunkSize}
        setChunkSize={setChunkSize}
        chunkOverlap={chunkOverlap}
        setChunkOverlap={setChunkOverlap}
      />

      {/* Interview Guide Modal */}
      <InterviewGuideModal
        isOpen={isGuideOpen}
        onClose={() => setIsGuideOpen(false)}
      />
    </div>
  );
}
