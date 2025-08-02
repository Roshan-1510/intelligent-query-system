# BajajHack - Document Q&A System

A FastAPI-based document question-answering system with secure API endpoints and vector search capabilities.

## Features

- 🔐 **Secure API Authentication** - Bearer token authentication
- 📄 **Document Processing** - Support for PDF, HTML, and text documents
- 🤖 **AI-Powered Q&A** - Uses OpenRouter API with Claude 3 Haiku
- 🔍 **Vector Search** - FAISS-based semantic search
- ⚡ **Batch Processing** - Process multiple questions at once
- 📊 **Health Monitoring** - System status and performance metrics

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the project root with the following variables:

```env
# API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
API_KEY=7609610f76f0b4b9e6b16db3e3fab7752a9fb25593df76ca443a60eca02020e9

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

### 3. Get API Keys

1. **OpenRouter API Key** (Free): Visit [https://openrouter.ai](https://openrouter.ai) to get a free API key
2. **Application API Key**: The default key is provided, but you can generate a new one for security

### 4. Run the Application

```bash
python run.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Authentication

All endpoints require Bearer token authentication. Include the API key in the Authorization header:

```
Authorization: Bearer 7609610f76f0b4b9e6b16db3e3fab7752a9fb25593df76ca443a60eca02020e9
```

### Available Endpoints

#### Health Check
```http
GET /health
```

#### Document Ingestion
```http
POST /ingest
Content-Type: application/json

{
  "url": "https://example.com/document.pdf",
  "doc_id": "unique_document_id"
}
```

#### Single Query
```http
POST /query
Content-Type: application/json

{
  "questions": ["What is the main topic?", "Who is the author?"],
  "max_docs": 4
}
```

#### Multi-Query (HackRx)
```http
POST /hackrx/run
Content-Type: application/json

{
  "documents": "https://example.com/document.pdf",
  "questions": ["What is the main topic?", "Who is the author?"],
  "max_docs": 4,
  "include_context": true
}
```

## Security Features

- ✅ **API Key Authentication** - Secure Bearer token validation
- ✅ **Input Validation** - Comprehensive request validation
- ✅ **Error Handling** - Graceful error responses
- ✅ **Rate Limiting** - Built-in rate limiting for API calls
- ✅ **Logging** - Comprehensive logging for monitoring

## Project Structure

```
BajajHack/
├── main.py              # FastAPI application and endpoints
├── config.py            # Configuration and settings
├── models.py            # Pydantic data models
├── auth.py              # Authentication middleware
├── llm.py               # LLM integration with OpenRouter
├── vector_store.py      # FAISS vector store
├── query_engine.py      # Query processing logic
├── utils.py             # Utility functions
├── pipeline.py          # Document processing pipeline
├── run.py               # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **Missing API Key**: Ensure `OPENROUTER_API_KEY` is set in your `.env` file
2. **Authentication Errors**: Check that the Bearer token is correctly formatted
3. **Document Processing**: Ensure URLs are accessible and contain supported content types
4. **Memory Issues**: For large documents, consider reducing `chunk_size` in config

### Logs

Check the `logs/` directory for detailed application logs.

## Development

### Running Tests

```bash
python test_system.py
```

### Adding New Features

1. Update models in `models.py`
2. Add endpoints in `main.py`
3. Implement business logic in appropriate modules
4. Update documentation

## License

This project is for educational and development purposes.

## Support

For issues and questions, check the logs in the `logs/` directory and ensure all environment variables are properly configured. 