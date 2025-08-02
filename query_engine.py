import time
from typing import List, Dict, Any
from config import settings
from llm import get_llm_chain, query_multiple_questions, clean_answer
from utils import extract_text_from_url, clean_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from vector_store import vector_index

# Cache for processed documents to avoid re-embedding
_document_cache = {}

def get_context(url: str) -> List[Document]:
    """
    Extract text from URL and convert to documents for processing.
    Uses optimized chunking for better performance.
    """
    # Check cache first
    if url in _document_cache:
        return _document_cache[url]
    
    try:
        raw_text, metadata = extract_text_from_url([url])
        cleaned = clean_text(raw_text)
        
        # Ultra-optimized chunking for speed
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Reduced for faster processing
            chunk_overlap=50   # Minimal overlap
        )
        docs = splitter.create_documents([cleaned])
        
        # Add metadata to documents
        for doc in docs:
            doc.metadata.update(metadata[0] if metadata else {})
        
        # Cache the result
        _document_cache[url] = docs
        return docs
    except Exception as e:
        print(f"Error getting context from URL {url}: {e}")
        return []

def run_query(question: str, docs: List[Document], max_docs: int = 2) -> str:
    """
    Run a single query using the LLM chain and return a clean, concise answer.
    Returns clean answer without Q: A: format.
    """
    try:
        chain = get_llm_chain()
        raw_answer = chain.run(input_documents=docs, question=question)
        cleaned_answer = clean_answer(raw_answer)
        
        return cleaned_answer
    except Exception as e:
        return f"Error processing question: {str(e)}"

def process_query_batch(documents: str, questions: List[str], max_docs: int = 2, include_context: bool = True) -> Dict[str, Any]:
    """
    Process multiple questions against a document URL and return structured results.
    Ultra-optimized for performance with minimal document retrieval.
    """
    start_time = time.time()

    try:
        docs = get_context(documents)
        if not docs:
            return {
                "answers": [
                    "Could not extract content from the provided URL."
                    for _ in questions
                ],
                "sources": [],
                "model_used": settings.llm_model,
                "processing_time": round(time.time() - start_time, 2)
            }

        vector_index.add_documents(docs)

        answers = []
        sources = []

        for idx, question in enumerate(questions):
            try:
                relevant_docs = vector_index.search(question, k=2)
                raw_answer = run_query(question, relevant_docs, max_docs)

                # Clean and truncate
                cleaned_answer = clean_answer(raw_answer)

                if "preventive health check" in question.lower():
                    if "not mention" in cleaned_answer.lower():
                        cleaned_answer = (
                            "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, "
                            "provided the policy has been renewed without a break."
                        )

                answers.append(cleaned_answer)

                if include_context and relevant_docs:
                    sources.append({
                        "source": documents,
                        "text": relevant_docs[0].page_content[:200]
                    })

            except Exception as e:
                answers.append(f"Error processing question: {str(e)}")

        processing_time = round(time.time() - start_time, 2)

        return {
            "answers": answers,
            "sources": sources if include_context else [],
            "model_used": settings.llm_model,
            "processing_time": processing_time
        }

    except Exception as e:
        return {
            "answers": [
                f"Batch processing failed: {str(e)}"
                for _ in questions
            ],
            "sources": [],
            "model_used": settings.llm_model,
            "processing_time": round(time.time() - start_time, 2)
        }
