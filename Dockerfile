# Use lightweight Python 3.10 base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install torch separately to avoid memory overflow
RUN pip install --no-cache-dir torch==2.0.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Copy requirement files
COPY requirements.txt .
# COPY requirements-heavy.txt .

# Install Python dependencies in chunks
RUN pip install --no-cache-dir --upgrade pip==23.3.1
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir -r requirements-heavy.txt

# Copy application code
COPY . .

# Do NOT expose a fixed port; Sevalla sets $PORT
# EXPOSE 8000  <-- ❌ Remove this

# Start FastAPI using dynamic $PORT from Sevalla
CMD ["python", "run.py"]
