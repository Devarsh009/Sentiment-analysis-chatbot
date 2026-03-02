/**
 * ChatInput Component
 * =====================
 * Text input field with send button for composing messages.
 * Supports Enter key to send and Shift+Enter for new lines.
 */

import React, { useState, useRef, useEffect } from 'react';

export default function ChatInput({ onSend, isLoading }) {
  const [text, setText] = useState('');
  const inputRef = useRef(null);

  // Auto-focus on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Re-focus after loading completes
  useEffect(() => {
    if (!isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !isLoading) {
      onSend(text.trim());
      setText('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <div style={styles.inputContainer}>
        <textarea
          ref={inputRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isLoading ? 'Waiting for response...' : 'Type your message...'}
          disabled={isLoading}
          rows={1}
          style={{
            ...styles.input,
            ...(isLoading ? styles.inputDisabled : {}),
          }}
        />

        <button
          type="submit"
          disabled={!text.trim() || isLoading}
          style={{
            ...styles.sendButton,
            ...(text.trim() && !isLoading ? styles.sendButtonActive : {}),
          }}
          title="Send message"
        >
          {isLoading ? (
            <span style={styles.spinner}>⟳</span>
          ) : (
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>

      <p style={styles.hint}>
        Press <kbd style={styles.kbd}>Enter</kbd> to send ·{' '}
        <kbd style={styles.kbd}>Shift + Enter</kbd> for new line
      </p>
    </form>
  );
}

const styles = {
  form: {
    padding: '16px 24px 12px',
    borderTop: '1px solid #334155',
    background: '#0f172a',
  },
  inputContainer: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: '8px',
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '16px',
    padding: '8px 8px 8px 16px',
    transition: 'border-color 0.2s ease',
  },
  input: {
    flex: 1,
    background: 'transparent',
    border: 'none',
    outline: 'none',
    color: '#f1f5f9',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'none',
    lineHeight: 1.5,
    maxHeight: '120px',
    minHeight: '24px',
  },
  inputDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
  sendButton: {
    width: '40px',
    height: '40px',
    borderRadius: '12px',
    border: 'none',
    background: '#334155',
    color: '#64748b',
    cursor: 'not-allowed',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    transition: 'all 0.2s ease',
  },
  sendButtonActive: {
    background: '#6366f1',
    color: '#ffffff',
    cursor: 'pointer',
    boxShadow: '0 2px 8px rgba(99, 102, 241, 0.4)',
  },
  spinner: {
    display: 'inline-block',
    animation: 'spin 1s linear infinite',
    fontSize: '18px',
  },
  hint: {
    textAlign: 'center',
    fontSize: '11px',
    color: '#475569',
    marginTop: '8px',
    marginBottom: 0,
  },
  kbd: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '4px',
    padding: '1px 4px',
    fontSize: '10px',
    fontFamily: 'monospace',
    color: '#94a3b8',
  },
};
