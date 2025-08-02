import re
import requests
from config import settings
from typing import List, Dict, Any
from langchain.schema import Document  # Import Document

HEADERS = {
    "Authorization": f"Bearer {settings.openrouter_api_key}",
    "HTTP-Referer": "https://yourdomain.com",  # Replace if hosted
    "X-Title": "Document Query System"
}

def clean_answer(text: str) -> str:
    """
    Cleans up LLM output by removing boilerplate, normalizing text, and shortening lengthy responses.
    Returns clean, direct answers without any prefixes or document references.
    """
    if not text:
        return ""

    # Remove known noisy prefixes and document references
    noisy_starts = [
        "According to the document",
        "As per the policy",
        "Based on the information provided",
        "According to Document",
        "The document states",
        "It is mentioned in the document",
        "From the documents",
        "As per the available data",
        "Based on the document",
        "According to the information",
        "The document indicates",
        "As mentioned in the document",
        "From the provided information",
        "Based on the available information",
        "Document 1 states",
        "Document 2 states",
        "Document 3 states",
        "The policy states",
        "The information indicates",
        "The content shows",
        "The document mentions",
        "The text reveals",
        "The data suggests",
        "The information shows",
        "According to",
        "Based on",
        "As per",
        "The documents indicate",
        "The policy indicates",
        "The information shows",
        "The document shows",
        "The policy shows",
        "The documents show",
        "The information reveals",
        "The document reveals",
        "The policy reveals"
    ]
    
    # Remove document references like "Document 1", "Document 3", etc.
    text = re.sub(r'Document \d+', '', text)
    text = re.sub(r'\(source: [^)]+\)', '', text)
    text = re.sub(r'Document \d+ states', '', text)
    text = re.sub(r'Document \d+ indicates', '', text)
    
    # Remove all noisy prefixes
    for phrase in noisy_starts:
        text = re.sub(rf"^{re.escape(phrase)}[:,\- ]*", "", text, flags=re.IGNORECASE)
        text = re.sub(rf"{re.escape(phrase)}[:,\- ]*", "", text, flags=re.IGNORECASE)

    # Replace line breaks and bullet dashes
    text = text.replace('\n', ' ').replace('•', '-').replace('●', '-')

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove trailing punctuation/ellipses
    text = re.sub(r"[.]+$", "", text)
    text = re.sub(r"\.\.\.$", "", text)
    text = re.sub(r"\.\.\.", "", text)
    text = re.sub(r'\s+([.,!?;])', r'\1', text)
    text = re.sub(r'^(yes|no|however|indeed|furthermore|moreover)[, ]+', '', text, flags=re.IGNORECASE)
# Remove specific 2–3 word generic prefixes
    text = re.sub(r'^(The|This|That|Such) [A-Za-z]+ (policy|document)[\s\-:,]*', '', text, flags=re.IGNORECASE)

    # Extract up to 2 clean sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    if len(sentences) > 2:
        combined_length = sum(len(s) for s in sentences[:2])
        if combined_length < 100 and len(sentences) > 2:
            text = " ".join(sentences[:3])  # include 3rd if 2 are too short
        else:
            text = " ".join(sentences[:2])
    else:
        text = " ".join(sentences)

    # Final cleanup - remove any remaining prefixes
    text = re.sub(r'^[A-Z][a-z]+ [a-z]+ [a-z]+[:,\- ]*', '', text)
    text = re.sub(r'^[A-Z][a-z]+ [a-z]+[:,\- ]*', '', text)
    
    return text.strip()


def format_prompt(question: str, docs: List[Document]) -> str:
    """
    Optimized prompt formatting for Claude 3 to produce clean, concise answers.
    """
    if not docs:
        return f"""You are a helpful assistant. Answer the following question in 1-2 clear, concise sentences without any prefixes like "According to" or "Based on".

Question: {question}

Answer:"""

    context_chunks = "\n\n".join(
        f"Document {i+1}:\n{doc.page_content.strip()}"
        for i, doc in enumerate(docs)
    )

    prompt = f"""You are a helpful assistant. Answer the following question based on the provided documents.

IMPORTANT: 
- Provide a direct, concise answer in 1-2 clear sentences
- Do NOT use phrases like "According to", "Based on", "Document states", etc.
- Do NOT mention document numbers or sources
- Write in simple, professional English
- Focus on the key information only

Documents:
{context_chunks}

Question: {question}

Answer:"""
    return prompt



def query_openrouter(prompt: str) -> str:
    """
    Send a query to OpenRouter API using the configured model.
    Optimized for speed with reduced token limits.
    """
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Provide concise answers in 1-2 sentences."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,  # Lower temperature for faster, more consistent responses
        "max_tokens": 150,   # Reduced for faster responses
        "top_p": 0.9,        # Add top_p for better speed
        "frequency_penalty": 0.1,  # Reduce repetition
        "presence_penalty": 0.1    # Encourage conciseness
    }
    try:
        response = requests.post(
            f"{settings.openrouter_base_url}/chat/completions",
            headers=HEADERS,
            json=payload,
            timeout=15  # Reduced timeout for speed
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        print(f"WARNING: OpenRouter API request failed: {e}")
        return f"Based on the provided documents, I cannot provide a specific answer to your question. The API request failed with error: {e}. Please check your API key and try again later."
    except (KeyError, IndexError) as e:
        print(f"WARNING: OpenRouter API returned unexpected data: {e}")
        return "Based on the provided documents, I cannot provide a specific answer to your question due to an unexpected API response. Please try again later."


def get_llm_chain():
    """
    Returns a callable LLM chain using OpenRouter.
    """
    class LLMChain:
        def run(self, input_documents: List[Document], question: str) -> str:
            prompt = format_prompt(question, input_documents)
            return query_openrouter(prompt)

    return LLMChain()


def query_multiple_questions(docs: List[Document], questions: List[str]) -> List[Dict[str, Any]]:
    """
    Process multiple questions against the same set of documents.
    
    Args:
        docs: List of documents to use as context
        questions: List of questions to answer
        
    Returns:
        List of dictionaries containing question and answer pairs
    """
    results = []
    chain = get_llm_chain()
    
    for question in questions:
        try:
            answer = chain.run(input_documents=docs, question=question)
            results.append({
                "question": question,
                "answer": answer,
                "error": None
            })
        except Exception as e:
            results.append({
                "question": question,
                "answer": "",
                "error": str(e)
            })
    
    return results