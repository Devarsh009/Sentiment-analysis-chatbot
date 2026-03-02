/**
 * SentimentBadge Component
 * ==========================
 * Displays the detected sentiment as a colored badge.
 * Shows sentiment label and confidence percentage.
 */

import React from 'react';

export default function SentimentBadge({ sentiment, confidence }) {
  const config = {
    positive: {
      color: '#22c55e',
      bg: 'rgba(34, 197, 94, 0.15)',
      border: 'rgba(34, 197, 94, 0.3)',
      icon: '😊',
      label: 'Positive',
    },
    negative: {
      color: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.15)',
      border: 'rgba(239, 68, 68, 0.3)',
      icon: '😔',
      label: 'Negative',
    },
    neutral: {
      color: '#f59e0b',
      bg: 'rgba(245, 158, 11, 0.15)',
      border: 'rgba(245, 158, 11, 0.3)',
      icon: '😐',
      label: 'Neutral',
    },
  };

  const cfg = config[sentiment] || config.neutral;
  const confidencePercent = Math.round((confidence || 0) * 100);

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '2px 8px',
        borderRadius: '12px',
        backgroundColor: cfg.bg,
        border: `1px solid ${cfg.border}`,
        fontSize: '11px',
        fontWeight: 500,
        color: cfg.color,
        marginTop: '4px',
      }}
    >
      <span>{cfg.icon}</span>
      <span>{cfg.label}</span>
      <span style={{ opacity: 0.7 }}>·</span>
      <span style={{ opacity: 0.8 }}>{confidencePercent}%</span>
    </div>
  );
}
