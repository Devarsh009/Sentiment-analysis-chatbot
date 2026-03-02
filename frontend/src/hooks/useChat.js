/**
 * useChat Hook
 * ==============
 * Custom React hook that manages chat state and API interactions.
 * Handles message history, loading states, errors, and session management.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { sendChatMessage } from '../services/api';

/**
 * Generate a unique session ID.
 */
function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
}

/**
 * Custom hook for chat functionality.
 *
 * @returns {Object} Chat state and methods
 */
export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId] = useState(() => generateSessionId());
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  /**
   * Send a message to the chatbot.
   *
   * @param {string} text - The message text to send
   */
  const sendMessage = useCallback(
    async (text) => {
      if (!text.trim() || isLoading) return;

      // Add user message to history
      const userMessage = {
        id: Date.now(),
        text: text.trim(),
        sender: 'user',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        // Call the API
        const response = await sendChatMessage(text.trim(), sessionId);

        // Add bot response to history
        const botMessage = {
          id: Date.now() + 1,
          text: response.reply,
          sender: 'bot',
          sentiment: response.sentiment,
          confidence: response.confidence,
          timestamp: response.timestamp,
        };

        setMessages((prev) => [...prev, botMessage]);
      } catch (err) {
        setError(err.message);

        // Add error message
        const errorMessage = {
          id: Date.now() + 1,
          text: "Sorry, I'm having trouble responding right now. Please try again.",
          sender: 'bot',
          isError: true,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, sessionId]
  );

  /**
   * Clear all messages and start a new conversation.
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  /**
   * Dismiss the current error.
   */
  const dismissError = useCallback(() => {
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sessionId,
    sendMessage,
    clearMessages,
    dismissError,
    messagesEndRef,
  };
}
