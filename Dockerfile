# Use Python 3.10 (stable and compatible with sentence-transformers & faiss)
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all project files
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI app (ensure main.py has `app` defined in global scope)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
