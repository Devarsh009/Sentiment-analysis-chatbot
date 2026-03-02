/**
 * AdminDashboard Component
 * ==========================
 * Basic analytics dashboard showing:
 * - Total messages processed
 * - Sentiment distribution
 * - Average confidence
 * - Recent messages
 */

import React, { useState, useEffect } from 'react';
import { getAnalytics } from '../services/api';

export default function AdminDashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 15000); // Refresh every 15s
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
      <div style={styles.container}>
        <p style={styles.loading}>Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <p style={styles.error}>Failed to load analytics: {error}</p>
        <button onClick={fetchAnalytics} style={styles.retryBtn}>
          Retry
        </button>
      </div>
    );
  }

  const dist = analytics?.sentiment_distribution || {};
  const total = analytics?.total_messages || 0;
  const avgConf = analytics?.average_confidence || 0;

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>📊 Analytics Dashboard</h2>

      {/* Stats Cards */}
      <div style={styles.statsGrid}>
        <div style={styles.statCard}>
          <span style={styles.statValue}>{total}</span>
          <span style={styles.statLabel}>Total Messages</span>
        </div>
        <div style={{ ...styles.statCard, borderColor: '#22c55e33' }}>
          <span style={{ ...styles.statValue, color: '#22c55e' }}>
            {dist.positive || 0}
          </span>
          <span style={styles.statLabel}>Positive</span>
        </div>
        <div style={{ ...styles.statCard, borderColor: '#ef444433' }}>
          <span style={{ ...styles.statValue, color: '#ef4444' }}>
            {dist.negative || 0}
          </span>
          <span style={styles.statLabel}>Negative</span>
        </div>
        <div style={{ ...styles.statCard, borderColor: '#f59e0b33' }}>
          <span style={{ ...styles.statValue, color: '#f59e0b' }}>
            {dist.neutral || 0}
          </span>
          <span style={styles.statLabel}>Neutral</span>
        </div>
      </div>

      {/* Confidence Meter */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Average Confidence</h3>
        <div style={styles.progressBar}>
          <div
            style={{
              ...styles.progressFill,
              width: `${avgConf * 100}%`,
            }}
          />
        </div>
        <span style={styles.confValue}>{(avgConf * 100).toFixed(1)}%</span>
      </div>

      {/* Sentiment Distribution Bar */}
      {total > 0 && (
        <div style={styles.section}>
          <h3 style={styles.sectionTitle}>Sentiment Distribution</h3>
          <div style={styles.distBar}>
            {(dist.positive || 0) > 0 && (
              <div
                style={{
                  ...styles.distSegment,
                  width: `${((dist.positive || 0) / total) * 100}%`,
                  background: '#22c55e',
                }}
                title={`Positive: ${dist.positive}`}
              />
            )}
            {(dist.neutral || 0) > 0 && (
              <div
                style={{
                  ...styles.distSegment,
                  width: `${((dist.neutral || 0) / total) * 100}%`,
                  background: '#f59e0b',
                }}
                title={`Neutral: ${dist.neutral}`}
              />
            )}
            {(dist.negative || 0) > 0 && (
              <div
                style={{
                  ...styles.distSegment,
                  width: `${((dist.negative || 0) / total) * 100}%`,
                  background: '#ef4444',
                }}
                title={`Negative: ${dist.negative}`}
              />
            )}
          </div>
        </div>
      )}

      {/* Recent Messages */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Recent Messages</h3>
        {(analytics?.recent_messages || []).length === 0 ? (
          <p style={styles.empty}>No messages yet. Start chatting!</p>
        ) : (
          <div style={styles.messageList}>
            {analytics.recent_messages.slice(0, 10).map((msg, idx) => (
              <div key={idx} style={styles.messageItem}>
                <p style={styles.messageText}>
                  {msg.message?.substring(0, 60)}
                  {msg.message?.length > 60 ? '...' : ''}
                </p>
                <div style={styles.messageMeta}>
                  <span
                    style={{
                      ...styles.sentimentTag,
                      color:
                        msg.sentiment === 'positive'
                          ? '#22c55e'
                          : msg.sentiment === 'negative'
                          ? '#ef4444'
                          : '#f59e0b',
                    }}
                  >
                    {msg.sentiment}
                  </span>
                  <span style={styles.messageConf}>
                    {((msg.confidence || 0) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    width: '320px',
    background: '#1e293b',
    borderLeft: '1px solid #334155',
    padding: '20px',
    overflowY: 'auto',
    flexShrink: 0,
  },
  title: {
    fontSize: '16px',
    fontWeight: 700,
    color: '#f1f5f9',
    marginBottom: '20px',
  },
  loading: { color: '#94a3b8', textAlign: 'center', padding: '40px 0' },
  error: { color: '#ef4444', textAlign: 'center', fontSize: '13px' },
  retryBtn: {
    display: 'block',
    margin: '12px auto',
    padding: '6px 16px',
    background: '#334155',
    border: '1px solid #475569',
    borderRadius: '6px',
    color: '#f1f5f9',
    cursor: 'pointer',
    fontSize: '13px',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '10px',
    marginBottom: '20px',
  },
  statCard: {
    padding: '12px',
    background: '#0f172a',
    border: '1px solid #334155',
    borderRadius: '10px',
    textAlign: 'center',
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  statValue: { fontSize: '22px', fontWeight: 700, color: '#f1f5f9' },
  statLabel: { fontSize: '11px', color: '#64748b', textTransform: 'uppercase' },
  section: { marginBottom: '20px' },
  sectionTitle: {
    fontSize: '13px',
    fontWeight: 600,
    color: '#94a3b8',
    marginBottom: '8px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  progressBar: {
    width: '100%',
    height: '8px',
    background: '#0f172a',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #6366f1, #818cf8)',
    borderRadius: '4px',
    transition: 'width 0.5s ease',
  },
  confValue: {
    fontSize: '12px',
    color: '#94a3b8',
    display: 'block',
    marginTop: '4px',
  },
  distBar: {
    width: '100%',
    height: '20px',
    borderRadius: '10px',
    overflow: 'hidden',
    display: 'flex',
    background: '#0f172a',
  },
  distSegment: {
    height: '100%',
    transition: 'width 0.5s ease',
    minWidth: '4px',
  },
  messageList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  messageItem: {
    padding: '8px 10px',
    background: '#0f172a',
    borderRadius: '8px',
    border: '1px solid #334155',
  },
  messageText: {
    fontSize: '12px',
    color: '#cbd5e1',
    margin: 0,
    lineHeight: 1.4,
  },
  messageMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '4px',
  },
  sentimentTag: {
    fontSize: '11px',
    fontWeight: 600,
    textTransform: 'capitalize',
  },
  messageConf: { fontSize: '11px', color: '#64748b' },
  empty: { fontSize: '13px', color: '#475569', textAlign: 'center' },
};
