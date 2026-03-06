/**
 * ChatWindow — Message display + polished welcome screen
 */

import React from 'react';
import MessageBubble from './MessageBubble';

const SUGGESTIONS = [
  { text: "I'm having an amazing day!", icon: "✨", sub: "Share your joy" },
  { text: "I feel stressed about work", icon: "😔", sub: "Talk it out" },
  { text: "Tell me something interesting", icon: "💡", sub: "Get inspired" },
  { text: "I need some motivation", icon: "🚀", sub: "Get a boost" },
];

export default function ChatWindow({ messages, isLoading, messagesEndRef, onSuggestionClick }) {
  if (messages.length === 0) {
    return (
      <div style={styles.welcome}>
        <div style={styles.welcomeInner}>
          {/* Logo */}
          <div style={styles.logoCircle}>
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#10a37f" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a10 10 0 0 1 10 10 10 10 0 0 1-10 10A10 10 0 0 1 2 12 10 10 0 0 1 12 2z" />
              <path d="M8 14s1.5 2 4 2 4-2 4-2" />
              <line x1="9" y1="9" x2="9.01" y2="9" />
              <line x1="15" y1="9" x2="15.01" y2="9" />
            </svg>
          </div>

          <h1 style={styles.welcomeTitle}>How can I help you today?</h1>
          <p style={styles.welcomeSubtitle}>
            Ask me anything — I'm here to help.
          </p>

          {/* Suggestion cards */}
          <div style={styles.suggestions}>
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                style={styles.suggestionCard}
                onClick={() => onSuggestionClick(s.text)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#3a3a3a';
                  e.currentTarget.style.borderColor = '#555';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'var(--color-bg-input)';
                  e.currentTarget.style.borderColor = 'var(--color-border)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <span style={styles.suggestionIcon}>{s.icon}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <span style={styles.suggestionText}>{s.text}</span>
                  <span style={styles.suggestionSub}>{s.sub}</span>
                </div>
                <svg style={styles.suggestionArrow} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.messages}>
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isLoading && (
          <div style={styles.typingRow}>
            <div style={styles.typingInner}>
              <div style={styles.typingAvatar}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10a37f" strokeWidth="2">
                  <path d="M12 2a10 10 0 0 1 10 10 10 10 0 0 1-10 10A10 10 0 0 1 2 12 10 10 0 0 1 12 2z" />
                  <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                  <line x1="9" y1="9" x2="9.01" y2="9" />
                  <line x1="15" y1="9" x2="15.01" y2="9" />
                </svg>
              </div>
              <div style={styles.typingDots}>
                <span style={{ ...styles.dot, animationDelay: '0s' }} />
                <span style={{ ...styles.dot, animationDelay: '0.15s' }} />
                <span style={{ ...styles.dot, animationDelay: '0.3s' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

const styles = {
  container: {
    flex: 1,
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
  },
  messages: {
    maxWidth: 768,
    width: '100%',
    margin: '0 auto',
    padding: '24px 16px',
  },
  // Welcome
  welcome: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 24px',
  },
  welcomeInner: {
    textAlign: 'center',
    maxWidth: 640,
    width: '100%',
    animation: 'slideUp 0.5s ease-out',
  },
  logoCircle: {
    width: 56,
    height: 56,
    borderRadius: '50%',
    background: 'rgba(16, 163, 127, 0.1)',
    border: '1px solid rgba(16, 163, 127, 0.2)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 20px',
    animation: 'glow 3s ease-in-out infinite',
  },
  welcomeTitle: {
    fontSize: 28,
    fontWeight: 700,
    color: 'var(--color-text)',
    marginBottom: 8,
    letterSpacing: '-0.02em',
  },
  welcomeSubtitle: {
    fontSize: 15,
    color: 'var(--color-text-muted)',
    marginBottom: 20,
    lineHeight: 1.5,
  },
  emotionChips: {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 8,
    marginBottom: 32,
  },
  chip: {
    fontSize: 12,
    padding: '5px 12px',
    borderRadius: 20,
    background: 'var(--color-bg-input)',
    border: '1px solid var(--color-border)',
    color: 'var(--color-text-secondary)',
  },
  suggestions: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 10,
    textAlign: 'left',
  },
  suggestionCard: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '14px 16px',
    background: 'var(--color-bg-input)',
    border: '1px solid var(--color-border)',
    borderRadius: 14,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
    color: 'var(--color-text)',
  },
  suggestionIcon: {
    fontSize: 20,
    flexShrink: 0,
  },
  suggestionText: {
    display: 'block',
    fontSize: 13,
    lineHeight: 1.4,
    fontWeight: 500,
  },
  suggestionSub: {
    display: 'block',
    fontSize: 11,
    color: 'var(--color-text-muted)',
    marginTop: 1,
  },
  suggestionArrow: {
    color: 'var(--color-text-muted)',
    flexShrink: 0,
    opacity: 0.4,
  },
  // Typing indicator
  typingRow: {
    padding: '18px 0',
    animation: 'fadeIn 0.2s ease-out',
  },
  typingInner: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  },
  typingAvatar: {
    width: 34,
    height: 34,
    borderRadius: 10,
    background: 'linear-gradient(135deg, #1a7f64, #10a37f)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  typingDots: {
    display: 'flex',
    gap: 4,
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: '50%',
    background: 'var(--color-text-muted)',
    animation: 'dotPulse 1.2s ease-in-out infinite',
  },
};
