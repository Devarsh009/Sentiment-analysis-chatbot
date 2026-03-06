/**
 * AdminDashboard — Clean analytics panel with emotion-aware displays
 */

import React, { useState, useEffect } from 'react';
import { getAnalytics } from '../services/api';

const SENTIMENT_COLORS = {
  positive: '#10a37f',
  neutral: '#f59e0b',
  negative: '#ef4444',
};

export default function AdminDashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchAnalytics = async () => {
    try {
      const data = await getAnalytics();
      setAnalytics(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={s.container}>
        <p style={s.muted}>Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={s.container}>
        <p style={{ color: '#ef4444', fontSize: 13, textAlign: 'center' }}>
          Failed to load analytics
        </p>
        <button onClick={fetchAnalytics} style={s.retryBtn}>Retry</button>
      </div>
    );
  }

  const dist = analytics?.sentiment_distribution || {};
  const total = analytics?.total_messages || 0;
  const avg = analytics?.average_confidence || 0;

  return (
    <div style={s.container}>
      <h3 style={s.title}>Analytics</h3>

      {/* Stat cards */}
      <div style={s.grid}>
        <StatCard label="Total" value={total} icon="💬" />
        <StatCard label="Positive" value={dist.positive || 0} color="#10a37f" icon="😊" />
        <StatCard label="Negative" value={dist.negative || 0} color="#ef4444" icon="😢" />
        <StatCard label="Neutral" value={dist.neutral || 0} color="#f59e0b" icon="💭" />
      </div>

      {/* Confidence */}
      <Section title="Avg Confidence">
        <div style={s.barBg}>
          <div style={{
            ...s.barFill,
            width: `${avg * 100}%`,
            background: avg > 0.7 ? '#10a37f' : avg > 0.4 ? '#f59e0b' : '#ef4444',
          }} />
        </div>
        <span style={s.small}>{(avg * 100).toFixed(1)}%</span>
      </Section>

      {/* Distribution */}
      {total > 0 && (
        <Section title="Distribution">
          <div style={s.distBar}>
            {['positive', 'neutral', 'negative'].map((key) => {
              const count = dist[key] || 0;
              if (!count) return null;
              return (
                <div
                  key={key}
                  style={{
                    height: '100%',
                    width: `${(count / total) * 100}%`,
                    background: SENTIMENT_COLORS[key],
                    minWidth: 4,
                    transition: 'width 0.4s ease',
                  }}
                  title={`${key}: ${count}`}
                />
              );
            })}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
            {['positive', 'neutral', 'negative'].map((key) => (
              <span key={key} style={{ fontSize: 10, color: SENTIMENT_COLORS[key], textTransform: 'capitalize' }}>
                {key} {dist[key] || 0}
              </span>
            ))}
          </div>
        </Section>
      )}

      {/* Recent */}
      <Section title="Recent Messages">
        {(analytics?.recent_messages || []).length === 0 ? (
          <p style={s.muted}>No messages yet</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {analytics.recent_messages.slice(0, 8).map((msg, i) => (
              <div key={i} style={s.msgItem}>
                <p style={s.msgText}>
                  {msg.message?.substring(0, 55)}
                  {msg.message?.length > 55 ? '...' : ''}
                </p>
                <div style={s.msgMeta}>
                  <span style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: SENTIMENT_COLORS[msg.sentiment] || '#8e8ea0',
                    textTransform: 'capitalize',
                  }}>
                    {msg.sentiment}
                  </span>
                  <span style={{ fontSize: 11, color: 'var(--color-text-muted)', fontVariantNumeric: 'tabular-nums' }}>
                    {((msg.confidence || 0) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Section>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <h4 style={{
        fontSize: 11,
        fontWeight: 600,
        color: 'var(--color-text-muted)',
        textTransform: 'uppercase',
        letterSpacing: 0.5,
        marginBottom: 8,
      }}>
        {title}
      </h4>
      {children}
    </div>
  );
}

function StatCard({ label, value, color, icon }) {
  return (
    <div style={{
      padding: 12,
      background: 'var(--color-bg-main)',
      borderRadius: 12,
      border: '1px solid var(--color-border)',
      textAlign: 'center',
      transition: 'border-color 0.2s',
    }}>
      {icon && <span style={{ fontSize: 16, display: 'block', marginBottom: 4 }}>{icon}</span>}
      <div style={{
        fontSize: 22,
        fontWeight: 700,
        color: color || 'var(--color-text)',
        fontVariantNumeric: 'tabular-nums',
      }}>
        {value}
      </div>
      <div style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: 2 }}>
        {label}
      </div>
    </div>
  );
}

const s = {
  container: {
    padding: 20,
    background: 'var(--color-bg-sidebar)',
    height: '100%',
    overflowY: 'auto',
  },
  title: {
    fontSize: 15,
    fontWeight: 600,
    color: 'var(--color-text)',
    marginBottom: 18,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 8,
    marginBottom: 18,
  },
  barBg: {
    width: '100%',
    height: 6,
    background: 'var(--color-bg-main)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 3,
    transition: 'width 0.4s ease',
  },
  small: {
    fontSize: 12,
    color: 'var(--color-text-muted)',
    display: 'block',
    marginTop: 4,
    fontVariantNumeric: 'tabular-nums',
  },
  distBar: {
    width: '100%',
    height: 16,
    borderRadius: 8,
    overflow: 'hidden',
    display: 'flex',
    background: 'var(--color-bg-main)',
  },
  msgItem: {
    padding: '8px 10px',
    background: 'var(--color-bg-main)',
    borderRadius: 8,
    border: '1px solid var(--color-border)',
    transition: 'border-color 0.15s',
  },
  msgText: {
    fontSize: 12,
    color: 'var(--color-text-secondary)',
    margin: 0,
    lineHeight: 1.4,
  },
  msgMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: 4,
  },
  muted: {
    fontSize: 13,
    color: 'var(--color-text-muted)',
    textAlign: 'center',
    padding: '30px 0',
  },
  retryBtn: {
    display: 'block',
    margin: '10px auto',
    padding: '6px 16px',
    background: 'var(--color-bg-input)',
    border: '1px solid var(--color-border)',
    borderRadius: 8,
    color: 'var(--color-text)',
    cursor: 'pointer',
    fontSize: 13,
    fontFamily: 'inherit',
    transition: 'all 0.15s',
  },
};
