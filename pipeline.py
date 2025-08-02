# pipeline.py

def get_context(document: str) -> str:
    """
    Dummy context retriever from a document.
    Replace with actual logic that extracts or finds relevant context.
    """
    # For now, just return the document as-is
    return document

def run_query(context: str, question: str) -> str:
    """
    Dummy query processor.
    Replace with actual logic using LLM or semantic search.
    """
    # For now, just return a formatted dummy response
    return f"Answer to your question '{question}' based on context '{context[:100]}...'"
