# main.py
import os
import logging
import json
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from query_engine import IntelligentQueryEngine
from database import get_db, QueryLog

load_dotenv()

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
AUTH_TOKEN = "7609610f76f0b4b9e6b16db3e3fab7752a9fb25593df76ca443a60eca02020e9"
security = HTTPBearer()

# --- UPDATED: Pydantic Models for a more systematic response ---
class QueryResult(BaseModel):
    question: str
    answer: str

class HackRxRequest(BaseModel):
    documents: HttpUrl
    questions: List[str]

class HackRxResponse(BaseModel):
    results: List[QueryResult]

# --- FastAPI Application ---
app = FastAPI(title="Intelligent Query-Retrieval System", version="1.0.0")

query_engine: IntelligentQueryEngine = None

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.scheme != "Bearer" or credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing authentication token")

def get_query_engine():
    global query_engine
    if query_engine is None:
        logging.info("First request received. Initializing the IntelligentQueryEngine...")
        query_engine = IntelligentQueryEngine()
        if not query_engine.llm:
            raise HTTPException(status_code=503, detail="Service Unavailable: Models could not be initialized.")
    return query_engine

@app.post("/api/v1/hackrx/run", response_model=HackRxResponse, dependencies=[Depends(verify_token)])
async def run_submission(
    request: HackRxRequest, 
    db: Session = Depends(get_db),
    engine: IntelligentQueryEngine = Depends(get_query_engine)
):
    success = engine.process_document_from_url(str(request.documents))
    if not success:
        raise HTTPException(status_code=400, detail="Failed to process document. Check URL/format.")

    final_results = []
    for question in request.questions:
        answer = engine.answer_question(question)
        if isinstance(answer, dict) and "error" in answer:
            # If there's an error, still return it in the structured format
            final_results.append(QueryResult(question=question, answer=f"Error: {answer['error']}"))
        else:
            final_results.append(QueryResult(question=question, answer=answer))
    
    # Log the structured results to the database
    log_entry = QueryLog(
        document_url=str(request.documents),
        questions=json.dumps({"questions": request.questions}),
        # Convert Pydantic models to dicts for JSON serialization
        answers=json.dumps({"results": [res.dict() for res in final_results]})
    )
    db.add(log_entry); db.commit()
    logging.info("Successfully logged request to the database.")

    return HackRxResponse(results=final_results)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API is running."}