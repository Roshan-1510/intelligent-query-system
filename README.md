# 🧠 Intelligent Query–Retrieval System

A secure, high-performance FastAPI backend powered by **Claude 3 Haiku** (via OpenRouter API) for extracting precise answers from large, complex documents (PDF, DOCX, EML, and more).  
**Purpose-built for insurance, legal, HR, and compliance workflows.**

---

## 📚 Table of Contents

- [Features](#-features)
- [API Endpoints](#-api-endpoints)
- [Authentication](#-authentication)
- [Local Setup](#-local-setup)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Security & Deployment](#-security--deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## ✨ Features

| Feature                                    | Description                                   |
|-------------------------------------------|-----------------------------------------------|
| 🔍 Document Ingestion via URL             | Accepts PDF, DOCX, HTML, EML files            |
| 📚 LLM-powered Multi-Question Answering   | Uses Claude 3 Haiku for robust answers        |
| 🧠 Semantic Search (FAISS + MiniLM)       | Fast, smart retrieval from large corpora      |
| 🔐 Bearer Token API Authentication        | Secure endpoints for every request            |
| ⚡ Batch Query (HackRx Ready)             | Submit many questions across docs at once     |
| ⚙️ Health check & Observability           | `/health` endpoint for monitoring             |
| 🚀 Optimized for Webhook/Low-Latency      | Fast response for integration scenarios       |
| 🛡️ Schema & Input Validation              | Hardened against malformed requests           |

---

## 📦 API Endpoints

### 🩺 Health Check

Check server health.

```http
GET /health
```

---

### 📥 Document Ingestion

Add documents by URL. Optionally assign your own doc ID.

```http
POST /ingest
Content-Type: application/json

{
  "url": "https://example.com/document.pdf",
  "doc_id": "custom_doc_id_001"
}
```

---

### ❓ Single Query

Ask a question (or multiple) about your ingested documents.

```http
POST /query
Content-Type: application/json

{
  "questions": ["What is the premium grace period?"],
  "max_docs": 3
}
```

---

### 🧠 Batch Multi-Query (HackRx Endpoint)

Submit multiple questions in bulk; works across one or several documents.

```http
POST /hackrx/run
Content-Type: application/json

{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "Is maternity covered?",
    "What is the waiting period for cataract surgery?"
  ],
  "max_docs": 4,
  "include_context": true
}
```

**Sample Response:**

```json
{
  "answers": [
    "Yes, maternity expenses are covered with conditions...",
    "Waiting period for cataract is 2 years."
  ]
}
```

---

## 🔐 Authentication

All endpoints require a Bearer Token in the header:

```
Authorization: Bearer <YOUR_API_KEY>
```

_**Never expose your real API keys in shared/public code!**_

---

## ⚙️ Local Setup

### 1. 📁 Clone the Repository

```bash
git clone https://github.com/Roshan-1510/intelligent-query-system.git
cd intelligent-query-system
```

### 2. 🛠 Configure Environment Variables

Create a `.env` file in your project root:

```env
# API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
API_KEY=your_secure_api_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Logging
LOG_LEVEL=INFO

# Model Configuration
LLM_MODEL=anthropic/claude-3-haiku
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1000

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu
```

### 3. 📦 Install Requirements

```bash
pip install -r requirements.txt
```

### 4. ▶️ Run the Application

```bash
python run.py
```

_Server defaults to `http://localhost:8000`_

---

## 🧪 Testing

Run included system tests:

```bash
python test_system.py
```

---

## 🗂️ Project Structure

```
intelligent-query-system/
├── main.py              # FastAPI application and routes
├── run.py               # Entry point
├── config.py            # App settings and environment
├── auth.py              # Token-based security
├── models.py            # Pydantic schemas
├── llm.py               # OpenRouter LLM wrapper
├── query_engine.py      # Batch and single query logic
├── vector_store.py      # FAISS index operations
├── pipeline.py          # Document preprocessing, extraction
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
└── README.md            # You're here!
```

---

## 🌐 Security & Deployment

- ✅ Bearer Token authentication everywhere  
- ✅ Input and schema validation throughout the app  
- ✅ Exception handling for robust uptime  
- ✅ Designed for rate-limiting & logging  
- ✅ Compatible with [Render.com](https://render.com/) — just link the repo and expose port `8000`

---

## 🙌 Contributing

Pull requests are highly welcome!  
- Open an issue first to discuss your proposed changes.  
- Follow standard Pythonic linting and design guidelines.  
- See [`CONTRIBUTING.md`](CONTRIBUTING.md) if available.

---


## 👨‍💻 Author

**Roshan Vishwakarma**  
[GitHub: Roshan-1510](https://github.com/Roshan-1510)  
📧 roshanvishwakarma277@gmail.com

---

## 🏆 Acknowledgements

Inspired by the open source, LLM, and HackRx hackathon community. Thank you!
