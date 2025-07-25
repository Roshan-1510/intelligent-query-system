# main.py
import os
import logging
import json # <-- ADD THIS IMPORT
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from typing import List
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from query_engine import IntelligentQueryEngine
from database import get_db, QueryLog

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
AUTH_TOKEN = "7609610f76f0b4b9e6b16db3e3fab7752a9fb25593df76ca443a60eca02020e9"
security = HTTPBearer()

class HackRxRequest(BaseModel):
    documents: HttpUrl
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]

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
    try:
        success = engine.process_document_from_url(str(request.documents))
        if not success:
            raise HTTPException(status_code=400, detail="Failed to process document. Check URL/format.")

        final_answers = []
        for question in request.questions:
            answer = engine.answer_question(question)
            final_answers.append(answer if isinstance(answer, str) else json.dumps(answer))
        
        # --- FIX: Convert dicts to JSON strings before saving ---
        log_entry = QueryLog(
            document_url=str(request.documents),
            questions=json.dumps({"questions": request.questions}),
            answers=json.dumps({"answers": final_answers})
        )
        db.add(log_entry); db.commit()
        logging.info("Successfully logged request to the database.")

        return HackRxResponse(answers=final_answers)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API is running."}