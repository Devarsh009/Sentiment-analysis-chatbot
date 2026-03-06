/**
 * ChatInput — Polished centered input bar with smooth interactions
 */

import React, { useState, useRef, useEffect } from 'react';

export default function ChatInput({ onSend, isLoading }) {
  const [text, setText] = useState('');
  const [focused, setFocused] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!isLoading) textareaRef.current?.focus();
  }, [isLoading]);

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 200) + 'px';
    }
  }, [text]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !isLoading) {
      onSend(text.trim());
      setText('');
      if (textareaRef.current) textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const canSend = text.trim() && !isLoading;

  return (
    <div style={styles.wrapper}>
      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={{
          ...styles.inputBox,
          borderColor: focused ? 'rgba(16, 163, 127, 0.5)' : 'var(--color-border)',
          boxShadow: focused ? '0 0 0 1px rgba(16, 163, 127, 0.15)' : 'none',
        }}>
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Message Sentiment Bot..."
            disabled={isLoading}
            rows={1}
            style={styles.textarea}
          />

          <button
            type="submit"
            disabled={!canSend}
            style={{
              ...styles.sendBtn,
              ...(canSend ? styles.sendBtnActive : {}),
            }}
            title="Send message"
          >
            {isLoading ? (
              <svg width="18" height="18" viewBox="0 0 24 24" style={{ animation: 'spin 1s linear infinite' }} fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3.478 2.405a.75.75 0 0 0-.926.94l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.405z" />
              </svg>
            )}
          </button>
        </div>
      </form>
      <p style={styles.disclaimer}>
        Emotion detection powered by DistilBERT + Groq. Responses may vary.
      </p>
    </div>
  );
}

const styles = {
  wrapper: {
    padding: '0 16px 16px',
    background: 'var(--color-bg-main)',
  },
  form: {
    maxWidth: 768,
    margin: '0 auto',
  },
  inputBox: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: 8,
    background: 'var(--color-bg-input)',
    border: '1px solid var(--color-border)',
    borderRadius: 16,
    padding: '10px 12px 10px 18px',
    transition: 'border-color 0.25s ease, box-shadow 0.25s ease',
  },
  textarea: {
    flex: 1,
    background: 'transparent',
    border: 'none',
    outline: 'none',
    color: 'var(--color-text)',
    fontSize: 15,
    fontFamily: 'inherit',
    resize: 'none',
    lineHeight: 1.5,
    maxHeight: 200,
    minHeight: 24,
    paddingTop: 2,
  },
  sendBtn: {
    width: 34,
    height: 34,
    borderRadius: 10,
    border: 'none',
    background: '#4a4a4a',
    color: '#8e8ea0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    cursor: 'not-allowed',
    transition: 'all 0.2s ease',
  },
  sendBtnActive: {
    background: 'var(--color-accent)',
    color: '#fff',
    cursor: 'pointer',
    boxShadow: '0 2px 8px rgba(16, 163, 127, 0.3)',
  },
  disclaimer: {
    textAlign: 'center',
    fontSize: 12,
    color: 'var(--color-text-muted)',
    marginTop: 10,
    marginBottom: 0,
    lineHeight: 1.4,
    maxWidth: 768,
    margin: '10px auto 0',
    opacity: 0.7,
  },
};
