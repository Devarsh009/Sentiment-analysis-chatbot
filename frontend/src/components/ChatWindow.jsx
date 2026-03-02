/**
 * ChatWindow Component
 * ======================
 * Main chat area that displays messages and the typing indicator.
 * Shows a welcome screen when no messages exist.
 */

import React from 'react';
import MessageBubble from './MessageBubble';

export default function ChatWindow({ messages, isLoading, messagesEndRef }) {
  // Welcome screen when no messages
  if (messages.length === 0) {
    return (
      <div style={styles.welcome}>
        <div style={styles.welcomeContent}>
          <span style={styles.welcomeIcon}>🤖</span>
          <h2 style={styles.welcomeTitle}>Welcome to Sentiment Chatbot!</h2>
          <p style={styles.welcomeText}>
            I'm an AI chatbot that understands your emotions. Send me a message
            and I'll detect your sentiment and respond accordingly.
          </p>
          <div style={styles.features}>
            <div style={styles.featureCard}>
              <span>😊</span>
              <span>Positive → Enthusiastic replies</span>
            </div>
            <div style={styles.featureCard}>
              <span>😔</span>
              <span>Negative → Empathetic support</span>
            </div>
            <div style={styles.featureCard}>
              <span>😐</span>
              <span>Neutral → Helpful information</span>
            </div>
          </div>
          <p style={styles.tryText}>Try saying something like:</p>
          <div style={styles.suggestions}>
            <span style={styles.suggestion}>"I'm having a great day!"</span>
            <span style={styles.suggestion}>"I feel frustrated with my work."</span>
            <span style={styles.suggestion}>"What's the weather like?"</span>
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

        {/* Typing Indicator */}
        {isLoading && (
          <div style={styles.typingContainer}>
            <div style={styles.typingAvatar}>🤖</div>
            <div style={styles.typingBubble}>
              <div style={styles.typingDots}>
                <span style={{ ...styles.dot, animationDelay: '0s' }}>●</span>
                <span style={{ ...styles.dot, animationDelay: '0.2s' }}>●</span>
                <span style={{ ...styles.dot, animationDelay: '0.4s' }}>●</span>
              </div>
            </div>
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

const styles = {
  container: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
  },
  messages: {
    maxWidth: '800px',
    margin: '0 auto',
  },
  // Welcome Screen
  welcome: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 24px',
  },
  welcomeContent: {
    textAlign: 'center',
    maxWidth: '500px',
    animation: 'slideUp 0.5s ease-out',
  },
  welcomeIcon: {
    fontSize: '64px',
    display: 'block',
    marginBottom: '16px',
  },
  welcomeTitle: {
    fontSize: '24px',
    fontWeight: 700,
    color: '#f1f5f9',
    marginBottom: '12px',
  },
  welcomeText: {
    fontSize: '14px',
    color: '#94a3b8',
    lineHeight: 1.6,
    marginBottom: '24px',
  },
  features: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
    marginBottom: '24px',
    flexWrap: 'wrap',
  },
  featureCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '12px',
    fontSize: '13px',
    color: '#cbd5e1',
  },
  tryText: {
    fontSize: '13px',
    color: '#64748b',
    marginBottom: '12px',
  },
  suggestions: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    alignItems: 'center',
  },
  suggestion: {
    display: 'inline-block',
    padding: '6px 16px',
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '20px',
    fontSize: '13px',
    color: '#818cf8',
    fontStyle: 'italic',
  },
  // Typing Indicator
  typingContainer: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: '8px',
    marginBottom: '16px',
    animation: 'fadeIn 0.3s ease-out',
  },
  typingAvatar: {
    width: '36px',
    height: '36px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '18px',
    background: '#1e293b',
    border: '1px solid #334155',
  },
  typingBubble: {
    padding: '12px 20px',
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '16px',
    borderBottomLeftRadius: '4px',
  },
  typingDots: {
    display: 'flex',
    gap: '4px',
  },
  dot: {
    fontSize: '12px',
    color: '#6366f1',
    animation: 'typing 1.4s infinite',
  },
};
