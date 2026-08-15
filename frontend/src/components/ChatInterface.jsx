import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, BookOpen, ArrowRight, CornerDownLeft } from 'lucide-react';
import CitationCard from './CitationCard';
import { api } from '../services/api';

export default function ChatInterface({
  hasDocuments,
  apiKey,
  topK,
  model,
  onOpenInterviewGuide
}) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (questionText) => {
    const textToSend = questionText || input.trim();
    if (!textToSend || isLoading) return;

    const userMessage = { role: 'user', content: textToSend };
    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    try {
      // Call chat API
      const res = await api.chat(updatedMessages, topK, apiKey, model);
      
      const assistantMessage = {
        role: 'assistant',
        content: res.response,
        citations: res.citations || [],
        model_used: res.model_used,
      };

      setMessages([...updatedMessages, assistantMessage]);
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: `❌ **Error:** ${err.message || 'Failed to generate answer.'}`,
        citations: [],
      };
      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-area">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: '50%',
                background: 'rgba(59, 130, 246, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem',
                color: 'var(--accent-blue)',
              }}
            >
              <Sparkles size={24} />
            </div>

            <h2 className="welcome-title">Ask Anything About Your Documents</h2>
            <p className="welcome-subtitle">
              Retrieval-Augmented Generation (RAG) grounds answers directly in your uploaded documents.
              Every response is supported by exact citations and semantic relevance scores.
            </p>

            <div className="quick-prompts">
              <button
                className="quick-prompt-btn"
                onClick={() =>
                  handleSend('Summarize the main topics and key takeaways from the documents.')
                }
              >
                <span>Summarize key takeaways</span>
                <ArrowRight size={14} opacity={0.6} />
              </button>

              <button
                className="quick-prompt-btn"
                onClick={() =>
                  handleSend('What are the specific requirements, rules, or policies mentioned?')
                }
              >
                <span>Extract rules or policies</span>
                <ArrowRight size={14} opacity={0.6} />
              </button>

              <button
                className="quick-prompt-btn"
                onClick={() =>
                  handleSend('List all numbers, metrics, or financial data found in the text.')
                }
              >
                <span>Find numbers & key metrics</span>
                <ArrowRight size={14} opacity={0.6} />
              </button>

              <button
                className="quick-prompt-btn"
                onClick={onOpenInterviewGuide}
                style={{ borderColor: 'rgba(59, 130, 246, 0.3)' }}
              >
                <span style={{ color: '#93c5fd' }}>How RAG works (Interview Q&A)</span>
                <BookOpen size={14} color="#93c5fd" />
              </button>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.role}`}>
              <div className={`avatar ${msg.role === 'user' ? 'user' : 'ai'}`}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>

              <div className="message-bubble">
                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>

                {/* Citations section for AI messages */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="citations-section">
                    <div className="citations-header">
                      <BookOpen size={12} />
                      <span>Retrieved Sources & Citations ({msg.citations.length})</span>
                    </div>
                    <div className="citation-grid">
                      {msg.citations.map((citation, cIdx) => (
                        <CitationCard key={cIdx} citation={citation} index={cIdx} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="message-row assistant">
            <div className="avatar ai">
              <Bot size={16} />
            </div>
            <div className="message-bubble">
              <div style={{ fontSize: '0.82rem', color: 'var(--accent-cyan)', marginBottom: '0.3rem' }}>
                Searching vector index & generating grounded answer...
              </div>
              <div className="typing-indicator">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="chat-input-bar">
        <div className="input-wrapper">
          <input
            type="text"
            className="chat-input"
            placeholder={
              hasDocuments
                ? 'Ask a question about your documents...'
                : 'Upload a document on the left, then ask a question...'
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            className="btn-send"
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            title="Send query"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
