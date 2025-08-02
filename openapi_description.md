# HackRx Document Q&A API

## Overview
FastAPI-based document question-answering system optimized for hackathon performance and accuracy.

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints require Bearer token authentication:
```
Authorization: Bearer 7609610f76f0b4b9e6b16db3e3fab7752a9fb25593df76ca443a60eca02020e9
```

## Endpoints

### POST /hackrx/run
Process multiple questions against a document URL.

**Request Body:**
```json
{
  "documents": "string (URL)",
  "questions": ["string"],
  "max_docs": 3,
  "include_context": true
}
```

**Response:**
```json
{
  "results": [
    {
      "question": "Q: <original_question>",
      "answer": "A: <cleaned_answer>",
      "error": null
    }
  ],
  "documents": "<url>",
  "model_used": "anthropic/claude-3-haiku",
  "processing_time": 12.34,
  "sources": [
    {
      "text": "<relevant snippet>",
      "source": "<url>"
    }
  ]
}
```

**Performance Guarantees:**
- Response time: < 30 seconds
- Answer length: 2-3 sentences max
- Document retrieval: Top 3 chunks only
- Source snippets: 300 characters max

**Supported Document Types:**
- PDF files
- DOCX files
- HTML pages
- Public email (.eml) files

**Error Handling:**
- 400: Invalid request format or document extraction failure
- 401: Invalid API key
- 500: Internal server error

## Example Usage

```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Authorization: Bearer 7609610f76f0b4b9e6b16db3e3fab7752a9fb25593df76ca443a60eca02020e9" \
  -H "Content-Type: application/json" \
  -d @test_query.json
```

## Technical Specifications

**Model:** Claude 3.5 Haiku via OpenRouter API
**Vector Store:** FAISS with HuggingFace embeddings
**Chunking:** 800 characters with 100 overlap
**Processing:** Independent question processing for explainability
**Caching:** Vector embeddings cached to avoid reprocessing 