/**
 * MessageBubble Component
 * =========================
 * Renders a single chat message bubble.
 * User messages appear on the right, bot messages on the left.
 * Bot messages include a sentiment badge.
 */

import React from 'react';
import SentimentBadge from './SentimentBadge';

export default function MessageBubble({ message }) {
  const isUser = message.sender === 'user';
  const isError = message.isError;

  const time = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      })
    : '';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '16px',
        animation: 'fadeIn 0.3s ease-out',
      }}
    >
      {/* Bot Avatar */}
      {!isUser && (
        <div style={styles.avatar}>
          <span>{isError ? '⚠️' : '🤖'}</span>
        </div>
      )}

      <div
        style={{
          maxWidth: '70%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: isUser ? 'flex-end' : 'flex-start',
        }}
      >
        {/* Message Bubble */}
        <div
          style={{
            ...styles.bubble,
            ...(isUser ? styles.userBubble : styles.botBubble),
            ...(isError ? styles.errorBubble : {}),
          }}
        >
          <p style={styles.text}>{message.text}</p>
        </div>

        {/* Metadata Row */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginTop: '4px',
            flexDirection: isUser ? 'row-reverse' : 'row',
          }}
        >
          {time && <span style={styles.time}>{time}</span>}
          {!isUser && message.sentiment && (
            <SentimentBadge
              sentiment={message.sentiment}
              confidence={message.confidence}
            />
          )}
        </div>
      </div>

      {/* User Avatar */}
      {isUser && (
        <div style={{ ...styles.avatar, ...styles.userAvatar }}>
          <span>👤</span>
        </div>
      )}
    </div>
  );
}

const styles = {
  avatar: {
    width: '36px',
    height: '36px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '18px',
    flexShrink: 0,
    marginTop: '4px',
    marginRight: '8px',
    background: '#1e293b',
    border: '1px solid #334155',
  },
  userAvatar: {
    marginRight: 0,
    marginLeft: '8px',
    background: '#4f46e5',
    border: '1px solid #6366f1',
  },
  bubble: {
    padding: '12px 16px',
    borderRadius: '16px',
    lineHeight: 1.5,
    wordWrap: 'break-word',
    overflowWrap: 'break-word',
  },
  userBubble: {
    background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
    color: '#ffffff',
    borderBottomRightRadius: '4px',
  },
  botBubble: {
    background: '#1e293b',
    color: '#e2e8f0',
    border: '1px solid #334155',
    borderBottomLeftRadius: '4px',
  },
  errorBubble: {
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    color: '#fca5a5',
  },
  text: {
    margin: 0,
    fontSize: '14px',
    whiteSpace: 'pre-wrap',
  },
  time: {
    fontSize: '11px',
    color: '#64748b',
  },
};
