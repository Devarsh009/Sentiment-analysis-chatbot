"""
Database Service
=================
SQLite database for storing user messages, sentiments, and analytics.
Supports continuous learning by collecting training data from user interactions.
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseService:
    """
    Database service for the chatbot application.
    
    Stores:
    - User messages with detected sentiments
    - Session information
    - Analytics data
    
    Uses SQLite for simplicity. Can be swapped for PostgreSQL in production.
    """
    
    _instance = None
    _connection = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for database connection."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        if DatabaseService._connection is not None:
            return
        
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__)))),
                "chatbot.db"
            )
        
        self.db_path = db_path
    
    def initialize(self):
        """Create database tables if they don't exist."""
        try:
            DatabaseService._connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False  # Allow multi-thread access
            )
            DatabaseService._connection.row_factory = sqlite3.Row
            
            cursor = DatabaseService._connection.cursor()
            
            # Messages table - stores all user interactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    message TEXT NOT NULL,
                    sentiment TEXT,
                    confidence REAL,
                    bot_response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sessions table - tracks conversation sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0
                )
            """)
            
            # Analytics table - aggregated metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    total_messages INTEGER DEFAULT 0,
                    positive_count INTEGER DEFAULT 0,
                    negative_count INTEGER DEFAULT 0,
                    neutral_count INTEGER DEFAULT 0,
                    avg_confidence REAL DEFAULT 0.0
                )
            """)
            
            DatabaseService._connection.commit()
            logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def save_message(
        self,
        message: str,
        sentiment: str,
        confidence: float,
        bot_response: str,
        session_id: str = None,
    ) -> int:
        """
        Save a user message and its analysis to the database.
        
        Args:
            message: User's original message
            sentiment: Detected sentiment
            confidence: Prediction confidence
            bot_response: The chatbot's response
            session_id: Optional session identifier
        
        Returns:
            The ID of the inserted row
        """
        try:
            conn = DatabaseService._connection
            if conn is None:
                logger.warning("Database not connected, skipping save")
                return -1
            
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO messages (session_id, message, sentiment, confidence, bot_response)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, message, sentiment, confidence, bot_response))
            
            # Update session if exists
            if session_id:
                cursor.execute("""
                    INSERT INTO sessions (id, message_count) VALUES (?, 1)
                    ON CONFLICT(id) DO UPDATE SET
                        last_active = CURRENT_TIMESTAMP,
                        message_count = message_count + 1
                """, (session_id,))
            
            conn.commit()
            
            row_id = cursor.lastrowid
            logger.debug(f"Message saved (id={row_id})")
            return row_id
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return -1
    
    def get_analytics(self) -> Dict:
        """
        Get analytics data for the admin dashboard.
        
        Returns:
            Dictionary with usage statistics
        """
        try:
            conn = DatabaseService._connection
            if conn is None:
                return self._empty_analytics()
            
            cursor = conn.cursor()
            
            # Total messages
            cursor.execute("SELECT COUNT(*) FROM messages")
            total = cursor.fetchone()[0]
            
            # Sentiment distribution
            cursor.execute("""
                SELECT sentiment, COUNT(*) as count 
                FROM messages 
                WHERE sentiment IS NOT NULL
                GROUP BY sentiment
            """)
            distribution = {row["sentiment"]: row["count"] for row in cursor.fetchall()}
            
            # Average confidence
            cursor.execute("SELECT AVG(confidence) FROM messages WHERE confidence > 0")
            avg_conf = cursor.fetchone()[0] or 0.0
            
            # Recent messages (last 20)
            cursor.execute("""
                SELECT message, sentiment, confidence, timestamp
                FROM messages
                ORDER BY timestamp DESC
                LIMIT 20
            """)
            recent = [dict(row) for row in cursor.fetchall()]
            
            # Messages per day (last 7 days)
            cursor.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM messages
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """)
            daily = {row["date"]: row["count"] for row in cursor.fetchall()}
            
            return {
                "total_messages": total,
                "sentiment_distribution": distribution,
                "average_confidence": round(avg_conf, 4),
                "recent_messages": recent,
                "daily_counts": daily,
            }
            
        except Exception as e:
            logger.error(f"Analytics query failed: {e}")
            return self._empty_analytics()
    
    def get_session_sentiments(self, session_id: str, limit: int = 10) -> List[str]:
        """
        Get recent sentiments for a session (for context-aware responses).
        
        Args:
            session_id: The session identifier
            limit: Max number of sentiments to return
        
        Returns:
            List of recent sentiment labels
        """
        try:
            conn = DatabaseService._connection
            if conn is None:
                return []
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sentiment FROM messages
                WHERE session_id = ? AND sentiment IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            return [row["sentiment"] for row in cursor.fetchall()][::-1]
            
        except Exception as e:
            logger.error(f"Session sentiment query failed: {e}")
            return []
    
    def _empty_analytics(self) -> Dict:
        """Return empty analytics structure."""
        return {
            "total_messages": 0,
            "sentiment_distribution": {},
            "average_confidence": 0.0,
            "recent_messages": [],
            "daily_counts": {},
        }
    
    def close(self):
        """Close the database connection."""
        if DatabaseService._connection:
            DatabaseService._connection.close()
            DatabaseService._connection = None
            logger.info("Database connection closed")
