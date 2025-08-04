from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import time
import logging
import traceback
from fastapi.responses import JSONResponse
from config import settings  # Corrected import
from models import DocumentIngestRequest, IngestResponse, QueryRequest, QueryResponse, ErrorResponse, HealthResponse, MultiQueryRequest, MultiQueryResponse, QuestionAnswer  # Import models
# from vector_store import vector_index  # Import vector_index
from llm import query_multiple_questions  # Import get_llm_chain and query_multiple_questions
from utils import extract_text_from_url, clean_text, get_system_info  # Import utils functions
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Import text splitter
from langchain.schema import Document  # Import Document
from auth import verify_api_key  # Import authentication
from query_engine import process_query_batch  # Import batch function
from models import DocumentInfo  # Or wherever it's defined
from datetime import datetime

app = FastAPI()
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"message": "Hello from Google App Engine!"}

@app.get("/health", response_model=HealthResponse, responses={401: {"model": ErrorResponse}})
def health_check(request: Request, api_key: str = Depends(verify_api_key)):
    try:
        print("🔍 Health check called.")
        sys_info = get_system_info()
        print(f"✅ System info: {sys_info}")

        return HealthResponse(
            status="ok",
            timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            models_loaded={"llm": True, "embeddings": True},
            cache_status={},
            system_info=sys_info
        )
    except Exception as e:
        print("❌ Exception in /health:")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Health check failed: {str(e)}"}
        )

@app.post("/ingest", response_model=IngestResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}})
def ingest_document(request: DocumentIngestRequest, api_key: str = Depends(verify_api_key)):
    start = time.time()
    from vector_store import vector_index # Import vector_index here to avoid circular import issues
    try:
        raw_text, metadata = extract_text_from_url([request.url])
        cleaned = clean_text(raw_text)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
        docs = splitter.create_documents([cleaned])
        vector_index.add_documents(docs)
        return IngestResponse(
             status="success",
           message="Document ingested successfully",
          doc_info=DocumentInfo(  # ✅ Use the actual Pydantic model
          doc_id=request.doc_id,
          url=request.url,
          chunk_count=len(docs),
          ingested_at=datetime.utcnow(),
          metadata=metadata if isinstance(metadata, dict) else metadata[0]  # ✅ Ensure it's a dict
    ),
    processing_time=round(time.time() - start, 2)
)

    except Exception as e:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query", response_model=List[QueryResponse], responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}})
def query_docs(request: QueryRequest, api_key: str = Depends(verify_api_key)):
    start = time.time()
    from vector_store import vector_index
    from llm import get_llm_chain  # Import get_llm_chain here to avoid circular import issues

    try:
        chain = get_llm_chain()
        responses = []

        for question in request.questions:
            docs = vector_index.search(question, k=request.max_docs or 3)
            result = chain.run(input_documents=docs, question=question)
            responses.append(QueryResponse(
                question=question,
                answer=result,
                model_used=settings.llm_model,
                doc_ids_searched=[
                    doc.metadata.get("doc_id") for doc in docs if doc.metadata.get("doc_id") is not None
                ],
                sources=[{"text": d.page_content[:300]} for d in docs],
                context_used="\n---\n".join(d.page_content[:500] for d in docs),
                processing_time=round(time.time() - start, 2)
            ))

        return responses


    except Exception as e:
        logger.exception("Query failed")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/hackrx/run", response_class=JSONResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}})
def multi_query_docs(request: MultiQueryRequest, api_key: str = Depends(verify_api_key)):
    start = time.time()
    try:
        # Process queries with ultra-optimized settings for speed
        results = process_query_batch(
            request.documents, 
            request.questions, 
            request.max_docs or 2,  # Default to 2 for maximum speed
            request.include_context
        )

        # Convert to QuestionAnswer format for compatibility
        question_answers = [
            QuestionAnswer(
                question=request.questions[i],
                answer=results["answers"][i],
                error=None
            ) for i in range(len(request.questions))
        ]

        return {
            "answers": [qa.answer for qa in question_answers]
        }

    except Exception as e:
        logger.exception("Multi-query failed")
        raise HTTPException(status_code=400, detail=f"Failed to process document. Check URL/format. Error: {str(e)}")
