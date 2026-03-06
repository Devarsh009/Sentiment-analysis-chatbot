/**
 * App Component — Main layout with sidebar + chat panel
 */

import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import AdminDashboard from './components/AdminDashboard';
import { useChat } from './hooks/useChat';
import './App.css';

export default function App() {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    dismissError,
    messagesEndRef,
  } = useChat();

  const [showDashboard, setShowDashboard] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app">
      {/* Mobile overlay */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <Sidebar
        open={sidebarOpen}
        onNewChat={clearMessages}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main panel */}
      <div className="main-panel">
        {/* Top bar */}
        <div className="topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button
              className="mobile-menu-btn"
              onClick={() => setSidebarOpen(true)}
              title="Open menu"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: '#10a37f',
                boxShadow: '0 0 6px rgba(16, 163, 127, 0.5)',
              }} />
              <span className="topbar-title">Sentiment Chatbot</span>
            </div>
          </div>

          <div className="topbar-actions">
            <button
              className={`topbar-btn ${showDashboard ? 'active' : ''}`}
              onClick={() => setShowDashboard((p) => !p)}
              title="Toggle Analytics"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <rect x="3" y="3" width="7" height="9" rx="1" />
                <rect x="14" y="3" width="7" height="5" rx="1" />
                <rect x="14" y="12" width="7" height="9" rx="1" />
                <rect x="3" y="16" width="7" height="5" rx="1" />
              </svg>
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={dismissError} className="error-dismiss">✕</button>
          </div>
        )}

        {/* Chat + optional analytics */}
        <div style={{ display: 'flex', flex: 1, minHeight: 0 }}>
          <div className="chat-area">
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              messagesEndRef={messagesEndRef}
              onSuggestionClick={sendMessage}
            />
            <ChatInput onSend={sendMessage} isLoading={isLoading} />
          </div>

          {showDashboard && (
            <div className="analytics-panel">
              <AdminDashboard />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
