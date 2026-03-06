/**
 * MessageBubble — Clean message row with avatar, text, and emotion badge
 */

import React from 'react';
import SentimentBadge from './SentimentBadge';

export default function MessageBubble({ message }) {
  const isUser = message.sender === 'user';
  const isError = message.isError;

  return (
    <div style={{
      ...styles.row,
      animation: 'fadeIn 0.3s ease-out',
    }}>
      <div style={styles.inner}>
        {/* Avatar */}
        <div style={{
          ...styles.avatar,
          ...(isUser ? styles.userAvatar : styles.botAvatar),
          ...(isError ? styles.errorAvatar : {}),
        }}>
          {isUser ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
            </svg>
          ) : isError ? (
            <span style={{ fontSize: 14 }}>⚠️</span>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2a10 10 0 0 1 10 10 10 10 0 0 1-10 10A10 10 0 0 1 2 12 10 10 0 0 1 12 2z" />
              <path d="M8 14s1.5 2 4 2 4-2 4-2" />
              <line x1="9" y1="9" x2="9.01" y2="9" />
              <line x1="15" y1="9" x2="15.01" y2="9" />
            </svg>
          )}
        </div>

        {/* Content */}
        <div style={styles.content}>
          <div style={styles.nameRow}>
            <span style={styles.name}>{isUser ? 'You' : 'Sentiment Bot'}</span>
            {message.timestamp && (
              <span style={styles.time}>
                {new Date(message.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            )}
          </div>

          <div style={{
            ...styles.text,
            ...(isError ? styles.errorText : {}),
          }}>
            {message.text}
          </div>

          {/* Emotion badge for bot messages */}
          {!isUser && message.sentiment && (
            <div style={{ marginTop: 8 }}>
              <SentimentBadge
                sentiment={message.sentiment}
                confidence={message.confidence}
                emotion={message.emotion}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  row: {
    padding: '18px 0',
  },
  inner: {
    display: 'flex',
    gap: 14,
    alignItems: 'flex-start',
  },
  avatar: {
    width: 34,
    height: 34,
    borderRadius: 10,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    marginTop: 2,
    transition: 'transform 0.2s ease',
  },
  userAvatar: {
    background: 'linear-gradient(135deg, #5b5fc7, #7c3aed)',
    color: '#fff',
  },
  botAvatar: {
    background: 'linear-gradient(135deg, #1a7f64, #10a37f)',
    color: '#fff',
  },
  errorAvatar: {
    background: 'rgba(239, 68, 68, 0.15)',
    border: '1px solid rgba(239, 68, 68, 0.25)',
  },
  content: {
    flex: 1,
    minWidth: 0,
  },
  nameRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    marginBottom: 4,
  },
  name: {
    fontSize: 14,
    fontWeight: 600,
    color: 'var(--color-text)',
  },
  time: {
    fontSize: 12,
    color: 'var(--color-text-muted)',
    fontVariantNumeric: 'tabular-nums',
  },
  text: {
    fontSize: 15,
    lineHeight: 1.7,
    color: 'var(--color-text)',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
  errorText: {
    color: '#fca5a5',
  },
};
