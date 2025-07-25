# main.py
import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from typing import List
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Import your custom modules
from query_engine import IntelligentQueryEngine
from database import get_db, QueryLog

# Load environment variables from .env file
load_dotenv()

# --- Configuration & Initialization ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
AUTH_TOKEN = "7609610f76f0b4b9e6b16db3e3fab7752a9fb25593df76ca443a60eca02020e9"
security = HTTPBearer()

class HackRxRequest(BaseModel):
    documents: HttpUrl
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]

app = FastAPI(
    title="Intelligent Query-Retrieval System",
    description="An LLM-powered system to process and query documents.",
    version="1.0.0"
)

# Dependency to verify the bearer token
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.scheme != "Bearer" or credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing authentication token")

# Instantiate the engine once when the app starts up to keep models in memory
query_engine = IntelligentQueryEngine()

@app.on_event("startup")
async def startup_event():
    if not query_engine.llm or not query_engine.embedding_model:
        logging.error("CRITICAL: Models failed to initialize. The API will not be functional.")

@app.post("/api/v1/hackrx/run", 
          response_model=HackRxResponse, 
          dependencies=[Depends(verify_token)])
async def run_submission(request: HackRxRequest, db: Session = Depends(get_db)):
    if not query_engine.llm:
        raise HTTPException(status_code=503, detail="Service Unavailable: LLM is not initialized.")

    success = query_engine.process_document_from_url(str(request.documents))
    if not success:
        raise HTTPException(status_code=400, detail="Failed to process the document. Check URL and file format.")

    final_answers = []
    for question in request.questions:
        answer = query_engine.answer_question(question)
        if isinstance(answer, dict) and "error" in answer:
            final_answers.append(f"Could not process question '{question}': {answer['error']}")
        else:
            final_answers.append(answer)
    
    log_entry = QueryLog(
        document_url=str(request.documents),
        questions={"questions": request.questions},
        answers={"answers": final_answers}
    )
    db.add(log_entry); db.commit()
    logging.info("Successfully logged request to the database.")

    return HackRxResponse(answers=final_answers)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API is running."}