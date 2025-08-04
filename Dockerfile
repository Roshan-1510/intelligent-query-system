# Use minimal base image
FROM python:3.10-slim

# Avoid Python cache & enable stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install essential packages with no cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Pre-copy only requirements for layer caching
COPY requirements.txt .

# Install torch CPU (optimized)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.0.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
