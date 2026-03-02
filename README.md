# 🤖 AI-Powered Sentiment-Aware Website Chatbot

A full-stack AI chatbot that detects user sentiment in real-time and adapts its responses accordingly. Built with **FastAPI**, **React**, and **HuggingFace Transformers (DistilBERT)**.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow?logo=huggingface)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [ML Training](#-ml-training)
- [API Documentation](#-api-documentation)
- [Docker Deployment](#-docker-deployment)
- [Testing](#-testing)
- [Future Improvements](#-future-improvements)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Sentiment Analysis** | Real-time detection of positive, negative, and neutral sentiment |
| **Adaptive Responses** | Chatbot tone changes based on detected sentiment |
| **DistilBERT Model** | Fine-tuned transformer model for high accuracy |
| **Custom Training** | Train on your own CSV dataset |
| **Continuous Learning** | Collect user data and retrain periodically |
| **Analytics Dashboard** | View sentiment distribution and usage stats |
| **Rate Limiting** | Built-in API rate limiter for security |
| **Modern UI** | Beautiful dark-themed React chat interface |
| **Docker Ready** | One-command deployment with Docker Compose |

### Chatbot Behavior
- 😊 **Positive messages** → Enthusiastic, encouraging responses
- 😔 **Negative messages** → Empathetic, supportive responses
- 😐 **Neutral messages** → Informative, helpful responses

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                            │
│              React + Vite (Port 5173)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐    │
│  │  Header   │ │ChatWindow│ │  Admin Dashboard     │    │
│  └──────────┘ └──────────┘ └──────────────────────┘    │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Chat Input                           │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP REST API
┌────────────────────────▼────────────────────────────────┐
│                      BACKEND                             │
│              FastAPI + Uvicorn (Port 8000)                │
│  ┌──────────┐ ┌──────────┐ ┌────────────────────┐      │
│  │  Routes   │ │ Services │ │   Middleware        │      │
│  │ /predict  │ │Sentiment │ │  Rate Limiter       │      │
│  │ /chat     │ │ Chatbot  │ │  Security Headers   │      │
│  │ /admin    │ │ Database │ │  CORS               │      │
│  └──────────┘ └────┬─────┘ └────────────────────┘      │
└─────────────────────┼───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    ML PIPELINE                           │
│  ┌────────────┐ ┌──────────┐ ┌──────────────────────┐  │
│  │  DistilBERT │ │ Tokenizer│ │  Inference Pipeline  │  │
│  │  Fine-tuned │ │          │ │                      │  │
│  └────────────┘ └──────────┘ └──────────────────────┘  │
│  ┌────────────┐ ┌──────────┐ ┌──────────────────────┐  │
│  │  Training   │ │Evaluation│ │  Retraining Script   │  │
│  └────────────┘ └──────────┘ └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   DATABASE                               │
│              SQLite (chatbot.db)                          │
│  ┌────────────┐ ┌──────────┐ ┌──────────────────────┐  │
│  │  Messages   │ │ Sessions │ │  Analytics           │  │
│  └────────────┘ └──────────┘ └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation & serialization
- **SQLite** - Lightweight database

### Machine Learning
- **HuggingFace Transformers** - Transformer models
- **DistilBERT** - Efficient BERT variant
- **PyTorch** - Deep learning framework
- **HuggingFace Datasets** - Dataset loading
- **scikit-learn** - Evaluation metrics

### Frontend
- **React 18** - UI library
- **Vite** - Fast build tool
- **CSS-in-JS** - Inline styles for components

### DevOps
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy for frontend

---

## 📂 Project Structure

```
Sentiment-analysis-chatbot/
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # App entry point
│   │   ├── config.py             # Settings (env vars)
│   │   ├── models.py             # Pydantic schemas
│   │   ├── routes/
│   │   │   ├── predict.py        # POST /api/predict
│   │   │   ├── chat.py           # POST /api/chat
│   │   │   └── admin.py          # Admin endpoints
│   │   ├── services/
│   │   │   ├── sentiment.py      # ML inference wrapper
│   │   │   ├── chatbot.py        # Response generation
│   │   │   └── database.py       # SQLite operations
│   │   ├── middleware/
│   │   │   ├── rate_limiter.py   # Rate limiting
│   │   │   └── security.py       # Security headers
│   │   └── utils/
│   │       └── logger.py         # Logging system
│   ├── tests/                    # Unit tests
│   │   ├── test_predict.py
│   │   ├── test_chat.py
│   │   └── test_sentiment.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── ml/                           # Machine Learning
│   ├── config.py                 # ML configuration
│   ├── preprocess.py             # Dataset preprocessing
│   ├── train.py                  # Training script
│   ├── evaluate.py               # Evaluation script
│   ├── inference.py              # Inference pipeline
│   ├── retrain.py                # Continuous learning
│   └── push_to_hub.py           # Push to HF Hub
├── frontend/                     # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── ChatInput.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── SentimentBadge.jsx
│   │   │   └── AdminDashboard.jsx
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   ├── hooks/
│   │   │   └── useChat.js        # Chat state hook
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/Devarsh009/Sentiment-analysis-chatbot.git
cd Sentiment-analysis-chatbot
```

### 2. Set Up Backend
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. (Optional) Train the Model
```bash
# Train on SST-2 dataset
cd ml
python train.py

# Or use a custom dataset
python preprocess.py --create-sample    # Create sample CSV
python train.py --custom data/sample_dataset.csv

# Evaluate the model
python evaluate.py
```

> **Note:** The chatbot works without training using a keyword-based fallback.
> Training gives much better accuracy with the DistilBERT model.

### 4. Start the Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: **http://localhost:8000**  
Interactive docs at: **http://localhost:8000/docs**

### 5. Set Up Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## 🧠 ML Training

### How the Training Pipeline Works

1. **Dataset Loading**: Uses HuggingFace `datasets` library to load SST-2 (or custom CSV)
2. **Tokenization**: Converts text to tokens using `AutoTokenizer` (DistilBERT tokenizer)
3. **Fine-tuning**: Uses HuggingFace `Trainer` API with AdamW optimizer
4. **Evaluation**: Computes accuracy, precision, recall, F1 score
5. **Saving**: Saves model + tokenizer to `ml/trained_model/`

### Training Commands

```bash
# Default training (SST-2 dataset, 3 epochs)
python ml/train.py

# Custom hyperparameters
python ml/train.py --epochs 5 --lr 3e-5 --batch-size 32

# Custom dataset
python ml/train.py --custom path/to/your/data.csv

# Evaluate after training
python ml/evaluate.py

# Push to HuggingFace Hub (optional)
python ml/push_to_hub.py --model-id your-username/model-name
```

### Custom Dataset Format
Create a CSV file with `text` and `label` columns:
```csv
text,label
"I love this product!",positive
"Terrible experience.",negative
"It was okay.",neutral
```

### Continuous Learning (Retraining)
The system collects user messages in SQLite. Retrain periodically:
```bash
python ml/retrain.py --epochs 2 --lr 1e-5
```

---

## 📡 API Documentation

### `POST /api/predict`
Analyze sentiment of a text message.

**Request:**
```json
{ "message": "I love this product!" }
```

**Response:**
```json
{
  "sentiment": "positive",
  "confidence": 0.97,
  "scores": {
    "negative": 0.01,
    "neutral": 0.02,
    "positive": 0.97
  }
}
```

### `POST /api/chat`
Send a message to the sentiment-aware chatbot.

**Request:**
```json
{
  "message": "I'm having a terrible day.",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "reply": "I'm sorry to hear that... 💙",
  "sentiment": "negative",
  "confidence": 0.92,
  "session_id": "generated-session-id",
  "timestamp": "2026-03-02T10:30:00"
}
```

### `GET /api/admin/analytics`
Get usage analytics.

### `GET /health`
Health check endpoint.

Full interactive docs available at **http://localhost:8000/docs**

---

## 🐳 Docker Deployment

### Build and Run Everything
```bash
docker-compose up --build
```

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:80
- **API Docs**: http://localhost:8000/docs

### Stop Services
```bash
docker-compose down
```

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_predict.py -v

# Run with coverage
pytest tests/ -v --cov=app
```

---

## 🔮 Future Improvements

1. **Multi-class Emotion Detection** - Extend beyond 3 sentiments to detect joy, anger, fear, surprise, etc.
2. **WebSocket Support** - Real-time streaming responses
3. **User Authentication** - Login system with JWT tokens
4. **PostgreSQL** - Replace SQLite for production scale
5. **Redis Caching** - Cache frequent predictions
6. **Kubernetes Deployment** - K8s manifests for cloud deployment
7. **CI/CD Pipeline** - GitHub Actions for automated testing & deployment
8. **Model A/B Testing** - Compare different model versions
9. **Multi-language Support** - Sentiment analysis in multiple languages
10. **Voice Input** - Speech-to-text integration
11. **Export Analytics** - CSV/PDF export of analytics data
12. **Conversation Memory** - Context-aware multi-turn conversations with LLM

---

## 📄 License

This project is for educational purposes. Feel free to use and modify it.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Built with ❤️ by Devarsh**
