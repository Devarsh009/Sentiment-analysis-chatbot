/**
 * Header Component
 * ==================
 * Top navigation bar with app title, status indicator, and controls.
 */

import React, { useState, useEffect } from 'react';
import { checkHealth } from '../services/api';

export default function Header({ onClearChat, onToggleDashboard, showDashboard }) {
  const [status, setStatus] = useState('checking');

  useEffect(() => {
    const check = async () => {
      try {
        const health = await checkHealth();
        setStatus(health.model_loaded ? 'online' : 'degraded');
      } catch {
        setStatus('offline');
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  const statusColors = {
    online: '#22c55e',
    degraded: '#f59e0b',
    offline: '#ef4444',
    checking: '#94a3b8',
  };

  const statusLabels = {
    online: 'Model Active',
    degraded: 'Fallback Mode',
    offline: 'Offline',
    checking: 'Checking...',
  };

  return (
    <header style={styles.header}>
      <div style={styles.left}>
        <div style={styles.logo}>
          <span style={styles.logoIcon}>🤖</span>
          <div>
            <h1 style={styles.title}>Sentiment Chatbot</h1>
            <p style={styles.subtitle}>AI-Powered Sentiment Analysis</p>
          </div>
        </div>
      </div>

      <div style={styles.right}>
        <div style={styles.status}>
          <span
            style={{
              ...styles.statusDot,
              backgroundColor: statusColors[status],
              boxShadow: `0 0 8px ${statusColors[status]}`,
            }}
          />
          <span style={styles.statusText}>{statusLabels[status]}</span>
        </div>

        <button
          onClick={onToggleDashboard}
          style={{
            ...styles.button,
            ...(showDashboard ? styles.buttonActive : {}),
          }}
          title="Toggle Analytics Dashboard"
        >
          📊
        </button>

        <button onClick={onClearChat} style={styles.button} title="New Chat">
          🗑️
        </button>
      </div>
    </header>
  );
}

const styles = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 24px',
    background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
    borderBottom: '1px solid #334155',
    position: 'sticky',
    top: 0,
    zIndex: 100,
    backdropFilter: 'blur(10px)',
  },
  left: { display: 'flex', alignItems: 'center', gap: '12px' },
  logo: { display: 'flex', alignItems: 'center', gap: '12px' },
  logoIcon: { fontSize: '32px' },
  title: {
    fontSize: '18px',
    fontWeight: 700,
    color: '#f1f5f9',
    margin: 0,
    lineHeight: 1.2,
  },
  subtitle: {
    fontSize: '12px',
    color: '#94a3b8',
    margin: 0,
    lineHeight: 1.2,
  },
  right: { display: 'flex', alignItems: 'center', gap: '12px' },
  status: { display: 'flex', alignItems: 'center', gap: '6px', marginRight: '8px' },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    transition: 'all 0.3s ease',
  },
  statusText: { fontSize: '12px', color: '#94a3b8' },
  button: {
    background: '#334155',
    border: '1px solid #475569',
    borderRadius: '8px',
    padding: '8px 12px',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    color: '#f1f5f9',
  },
  buttonActive: {
    background: '#4f46e5',
    borderColor: '#6366f1',
  },
};
