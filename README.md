# LLM-Powered Intelligent Query–Retrieval System

This project is an intelligent system that processes large documents (PDF, DOCX, EML) and answers natural language questions based on their content. It's designed for scenarios in insurance, legal, HR, and compliance.

---

## Technology Stack

- **Backend:** FastAPI
- **LLM & Embeddings:** Google Gemini & Google Generative AI Embeddings
- **Vector Store:** FAISS (for in-memory semantic search)
- **Database:** PostgreSQL (hosted on Neon)
- **Deployment:** Render

---

## API Documentation

### Endpoint: `POST /api/v1/hackrx/run`

This endpoint processes a document from a URL and answers a list of questions based on its content.

- **URL:** `https://your-app-name.onrender.com/api/v1/hackrx/run` 
  *(Replace with your actual Render URL)*

- **Method:** `POST`

- **Authentication:**
  - **Type:** Bearer Token
  - **Token:** `7609610f76f0b4b9e6b16db3e3fab7752a9fb25593df76ca443a60eca02020e9`

- **Request Body:**
  ```json
  {
      "documents": "https://<URL_to_your_document.pdf>",
      "questions": [
          "First question?",
          "Second question?"
      ]
  }
