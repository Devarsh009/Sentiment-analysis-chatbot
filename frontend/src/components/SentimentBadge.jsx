/**
 * SentimentBadge — Emotion-aware pill badge with icon + label
 * Shows granular emotion (angry, happy, curious, etc.) with color coding
 */

import React from 'react';

const EMOTION_CONFIG = {
  angry:        { icon: '😠', label: 'Angry',        color: 'var(--emotion-angry)' },
  frustrated:   { icon: '😤', label: 'Frustrated',   color: 'var(--emotion-frustrated)' },
  sad:          { icon: '😢', label: 'Sad',           color: 'var(--emotion-sad)' },
  worried:      { icon: '😟', label: 'Worried',       color: 'var(--emotion-worried)' },
  disappointed: { icon: '😞', label: 'Disappointed',  color: 'var(--emotion-disappointed)' },
  excited:      { icon: '🤩', label: 'Excited',       color: 'var(--emotion-excited)' },
  grateful:     { icon: '🙏', label: 'Grateful',      color: 'var(--emotion-grateful)' },
  happy:        { icon: '😊', label: 'Happy',         color: 'var(--emotion-happy)' },
  proud:        { icon: '💪', label: 'Proud',         color: 'var(--emotion-proud)' },
  curious:      { icon: '🤔', label: 'Curious',       color: 'var(--emotion-curious)' },
  confused:     { icon: '😕', label: 'Confused',      color: 'var(--emotion-confused)' },
  thoughtful:   { icon: '💭', label: 'Thoughtful',    color: 'var(--emotion-thoughtful)' },
  normal:       { icon: '💬', label: 'Neutral',       color: 'var(--emotion-normal)' },
};

export default function SentimentBadge({ sentiment, confidence, emotion }) {
  const key = emotion || sentiment || 'normal';
  const cfg = EMOTION_CONFIG[key] || EMOTION_CONFIG.normal;
  const pct = Math.round((confidence || 0) * 100);

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 5,
      padding: '3px 10px 3px 6px',
      borderRadius: 20,
      background: `color-mix(in srgb, ${cfg.color} 12%, transparent)`,
      fontSize: 12,
      fontWeight: 500,
      color: cfg.color,
      letterSpacing: '0.01em',
      transition: 'all 0.2s ease',
      animation: 'scaleIn 0.2s ease-out',
    }}>
      <span style={{ fontSize: 13, lineHeight: 1 }}>{cfg.icon}</span>
      {cfg.label} · {pct}%
    </span>
  );
}
