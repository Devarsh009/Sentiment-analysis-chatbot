/**
 * Sidebar — Clean left navigation with status + capabilities
 */

import React, { useState, useEffect } from 'react';
import { checkHealth } from '../services/api';

export default function Sidebar({ open, onNewChat, onClose }) {
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

  const statusConfig = {
    online:   { color: '#10a37f', label: 'Model Active',   glow: 'rgba(16, 163, 127, 0.4)' },
    degraded: { color: '#f59e0b', label: 'Fallback Mode',  glow: 'rgba(245, 158, 11, 0.4)' },
    offline:  { color: '#ef4444', label: 'Offline',        glow: 'rgba(239, 68, 68, 0.4)' },
    checking: { color: '#8e8ea0', label: 'Connecting...',   glow: 'rgba(142, 142, 160, 0.3)' },
  };

  const cfg = statusConfig[status];

  return (
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="sidebar-header">
        <button
          className="new-chat-btn"
          onClick={() => { onNewChat(); onClose(); }}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          New chat
        </button>
      </div>

      <nav className="sidebar-nav" />

      <div className="sidebar-footer">
        <button className="sidebar-footer-btn">
          <span
            className="status-dot"
            style={{
              background: cfg.color,
              boxShadow: `0 0 6px ${cfg.glow}`,
            }}
          />
          {cfg.label}
        </button>
      </div>
    </aside>
  );
}
