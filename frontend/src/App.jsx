/**
 * App Component
 * ===============
 * Root component that assembles the entire chatbot application.
 * Manages the layout: Header, ChatWindow, ChatInput, and AdminDashboard.
 */

import React, { useState } from 'react';
import Header from './components/Header';
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

  return (
    <div className="app">
      <Header
        onClearChat={clearMessages}
        onToggleDashboard={() => setShowDashboard((prev) => !prev)}
        showDashboard={showDashboard}
      />

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={dismissError} className="error-dismiss">
            ✕
          </button>
        </div>
      )}

      <div className="app-body">
        {/* Main Chat Area */}
        <div className="chat-area">
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            messagesEndRef={messagesEndRef}
          />
          <ChatInput onSend={sendMessage} isLoading={isLoading} />
        </div>

        {/* Analytics Dashboard (toggle) */}
        {showDashboard && <AdminDashboard />}
      </div>
    </div>
  );
}
