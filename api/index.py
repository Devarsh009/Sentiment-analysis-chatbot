"""
Vercel Serverless Entry Point
===============================
Wraps the FastAPI backend for Vercel's Python serverless runtime.

On Vercel:
- ML model (PyTorch) is NOT available (too large for serverless)
- Sentiment analysis uses keyword-based fallback
- Groq LLM handles response generation
- SQLite uses /tmp/ (ephemeral storage)
"""

import sys
import os

# ── Path setup: let Python find our backend & ml packages ──
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
sys.path.insert(0, os.path.join(ROOT, "ml"))

# ── Vercel-friendly environment defaults (must be set BEFORE importing app) ──
os.environ.setdefault("LOG_FILE", "/tmp/app.log")
os.environ.setdefault("CORS_ORIGINS", "*")
os.environ.setdefault("DEBUG", "False")

# ── Import the FastAPI application ──
from app.main import app  # noqa: E402, F401
