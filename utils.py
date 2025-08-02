"""
Utility functions for the Document Q&A System
"""
import hashlib
import logging
import time
import psutil
import re
import os
from pathlib import Path
from typing import Dict, Any, Optional
from functools import wraps
import requests
from bs4 import BeautifulSoup

# Set up logger
logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """Set up logging configuration"""
    
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{log_dir}/app.log"),
            logging.StreamHandler()
        ]
    )
    
    # Reduce noise from other libraries
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)

def get_cache_key(text: str) -> str:
    """Generate a cache key from text"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def get_file_hash(url: str) -> str:
    """Generate a hash for a URL/file for caching purposes"""
    return hashlib.sha256(url.encode('utf-8')).hexdigest()[:16]

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper

def get_system_info() -> Dict[str, Any]:
    """Get system information for monitoring"""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "available_memory_gb": round(psutil.virtual_memory().available / (1024**3), 2)
        }
    except Exception as e:
        logger.warning(f"Could not get system info: {e}")
        return {}

from typing import Dict, Any
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from io import BytesIO
import requests

def extract_text_from_url(urls: list[str], timeout: int = 30) -> tuple[str, list[Dict[str, Any]]]:
    """
    Extract and combine text content from multiple URLs.
    Returns: (combined_text_content, list_of_metadata)
    """
    combined_text = ""
    all_metadata = []

    for url in urls:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '').lower()

            # Case 1: PDF
            if 'application/pdf' in content_type:
                pdf_reader = PdfReader(BytesIO(response.content))
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                combined_text += text.strip() + "\n\n"
                all_metadata.append({"source": url, "type": "pdf"})

            # Case 2: HTML
            elif 'text/html' in content_type:
                soup = BeautifulSoup(response.content, 'html.parser')

                for script in soup(["script", "style"]):
                    script.decompose()

                text = soup.get_text()
                title = soup.title.string if soup.title else None

                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)

                combined_text += text.strip() + "\n\n"

                meta = {"source": url, "type": "html"}
                if title:
                    meta["title"] = title
                all_metadata.append(meta)

            else:
                raise ValueError(f"Unsupported content type: {content_type}")

        except Exception as e:
            raise RuntimeError(f"Error extracting text from URL {url}: {e}")

    return combined_text.strip(), all_metadata



def validate_file_type(filename: str, allowed_types: list) -> bool:
    """Validate if file type is allowed"""
    file_extension = Path(filename).suffix.lower()
    return file_extension in allowed_types

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"



import re
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt', quiet=True)

def clean_answer(answer: str, max_length: int = 1000) -> str:
    """
    Cleans and formats the answer for HackRx standards.

    Args:
        answer: Raw answer string from LLM.
        max_length: Max allowed length.

    Returns:
        Cleaned and concise answer (≤2 sentences, trimmed, formatted).
    """
    if not answer:
        return ""

    # Remove unwanted phrases
    answer = re.sub(
        r"(According to the document|Document \d+ states:|Based on the information provided,?)", 
        '', 
        answer, 
        flags=re.IGNORECASE
    )

    # Collapse whitespace
    answer = re.sub(r'\s+', ' ', answer).strip()

    # Fix markdown ellipses and strip trailing punctuations
    answer = re.sub(r'\.{3,}', '...', answer)
    answer = re.sub(r'^\W+|\W+$', '', answer)

    # Tokenize and keep first 2 meaningful sentences
    sentences = sent_tokenize(answer)
    answer = ' '.join(sentences[:2]).strip()

    # Final truncate check (preserves whole words)
    if len(answer) > max_length:
        answer = answer[:max_length].rsplit(' ', 1)[0] + "..."

    return answer


def clean_text(text: str) -> str:
    """Clean and normalize raw text extracted from documents or web pages"""
    if not text:
        return ""

    # Step 1: Remove null characters and normalize line breaks
    text = text.replace('\x00', '')
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Step 2: Remove common boilerplate like headers/footers (PDF page numbers, repeated titles)
    # Remove lines that look like page headers/footers or copyright info
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remove lines that are just numbers (page numbers)
        if re.fullmatch(r'\d{1,3}', line):
            continue
        # Remove common copyright/publisher lines
        if re.search(r'(page \d+|©|all rights reserved)', line, re.IGNORECASE):
            continue
        # Remove uppercase lines often used as headers
        if line.isupper() and len(line.split()) <= 6:
            continue
        cleaned_lines.append(line)

    # Step 3: Remove extra spacing and keep clean paragraphs
    text = '\n'.join(cleaned_lines)
    text = re.sub(r'\s{2,}', ' ', text)  # multiple spaces to one
    text = re.sub(r'\n{2,}', '\n\n', text)  # multiple newlines to paragraph breaks

    # Step 4: Optional truncation for overly long inputs (can help LLMs focus)
    max_length = 100_000  # 100k characters
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 60, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def is_allowed(self) -> bool:
        """Check if a call is allowed based on rate limits"""
        current_time = time.time()
        
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls 
                     if current_time - call_time < self.time_window]
        
        # Check if we're under the limit
        if len(self.calls) < self.max_calls:
            self.calls.append(current_time)
            return True
        
        return False
    
    def wait_time(self) -> float:
        """Get the time to wait before the next call is allowed"""
        if not self.calls:
            return 0
        
        oldest_call = min(self.calls)
        current_time = time.time()
        
        return max(0, self.time_window - (current_time - oldest_call))

# Global rate limiter instance
api_rate_limiter = RateLimiter(max_calls=50, time_window=60)  # 50 calls per minute