/**
 * API Service
 * =============
 * Handles all HTTP requests to the backend API.
 * Provides clean methods for chat, prediction, and analytics.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling.
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || errorData.error || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
      throw new Error('Unable to connect to the server. Please ensure the backend is running.');
    }
    throw error;
  }
}

/**
 * Send a chat message and get a sentiment-aware response.
 *
 * @param {string} message - User's message text
 * @param {string|null} sessionId - Optional session ID for conversation tracking
 * @returns {Promise<Object>} - { reply, sentiment, confidence, session_id, timestamp }
 */
export async function sendChatMessage(message, sessionId = null) {
  const body = { message };
  if (sessionId) body.session_id = sessionId;

  return apiRequest('/api/chat', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * Get sentiment prediction for a text message.
 *
 * @param {string} message - Text to analyze
 * @returns {Promise<Object>} - { sentiment, confidence, scores }
 */
export async function predictSentiment(message) {
  return apiRequest('/api/predict', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}

/**
 * Get analytics data for the admin dashboard.
 *
 * @returns {Promise<Object>} - Analytics data
 */
export async function getAnalytics() {
  return apiRequest('/api/admin/analytics');
}

/**
 * Get model information.
 *
 * @returns {Promise<Object>} - Model info
 */
export async function getModelInfo() {
  return apiRequest('/api/admin/model-info');
}

/**
 * Check API health status.
 *
 * @returns {Promise<Object>} - { status, model_loaded, version }
 */
export async function checkHealth() {
  return apiRequest('/health');
}
