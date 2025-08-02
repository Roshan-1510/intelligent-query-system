"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


class DocumentIngestRequest(BaseModel):
    """Request model for document ingestion"""
    url: str = Field(..., description="URL of the document to ingest")
    doc_id: str = Field(..., description="Unique identifier for the document")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

    @validator('url')
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v.strip()

    @validator('doc_id')
    def validate_doc_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Document ID cannot be empty')
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Document ID can only contain letters, numbers, underscores, and hyphens')
        return v.strip()


class QueryRequest(BaseModel):
    """Request model for querying documents with multiple questions"""
    questions: List[str] = Field(..., min_items=1, description="List of questions to ask the system")  # <-- changed from `question: str`
    doc_ids: Optional[List[str]] = Field(default=None, description="List of document IDs to search within")
    max_docs: Optional[int] = Field(default=4, ge=1, le=10, description="Maximum number of documents to retrieve")
    include_context: Optional[bool] = Field(default=True, description="Include context in the response")

    @validator('questions')
    def validate_questions(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one question is required')
        for question in v:
            if not question or not question.strip():
                raise ValueError('Questions cannot be empty')
            if len(question.strip()) < 3:
                raise ValueError('Questions must be at least 3 characters long')
        return [q.strip() for q in v]


class MultiQueryRequest(BaseModel):
    """Request model for querying documents with multiple questions"""
    documents: str = Field(..., description="URL of the document to query")
    questions: List[str] = Field(..., min_items=1, description="List of questions to ask the system")
    max_docs: Optional[int] = Field(default=4, ge=1, le=10, description="Maximum number of documents to retrieve")
    include_context: Optional[bool] = Field(default=True, description="Include context in the response")

    @validator('documents')
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v.strip()

    @validator('questions')
    def validate_questions(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one question is required')
        for question in v:
            if not question or not question.strip():
                raise ValueError('Questions cannot be empty')
            if len(question.strip()) < 3:
                raise ValueError('Questions must be at least 3 characters long')
        return [q.strip() for q in v]


class DocumentInfo(BaseModel):
    """Information about an ingested document"""
    doc_id: str
    url: str
    title: Optional[str] = None
    chunk_count: int
    ingested_at: datetime
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    metadata: Dict[str, Any] = {}


class QueryResponse(BaseModel):
    """Response model for queries"""
    question: str
    answer: str
    confidence: Optional[float] = None
    sources: List[Dict[str, Any]] = []
    context_used: Optional[str] = None
    processing_time: float
    model_used: str
    doc_ids_searched: List[str] = []


class QuestionAnswer(BaseModel):
    """Model for a single question-answer pair"""
    question: str
    answer: str
    error: Optional[str] = None


class MultiQueryResponse(BaseModel):
    """Response model for multiple queries"""
    results: List[QuestionAnswer]
    documents: str
    model_used: str
    processing_time: float
    sources: Optional[List[Dict[str, Any]]] = None


class IngestResponse(BaseModel):
    """Response model for document ingestion"""
    status: str
    message: str
    doc_info: DocumentInfo
    processing_time: float
    cached: bool = False


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    models_loaded: Dict[str, bool] = {}
    cache_status: Dict[str, Any] = {}
    system_info: Dict[str, Any] = {}


class StatusResponse(BaseModel):
    """System status response"""
    vectorstore_status: str
    total_documents: int
    total_chunks: int
    available_doc_ids: List[str]
    cache_size: int
    memory_usage: Optional[Dict[str, Any]] = None
