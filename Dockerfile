# Use minimal Python image
FROM python:3.10-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install PyTorch separately to optimize caching
RUN pip install --no-cache-dir torch==2.0.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Copy and install requirements
COPY requirements-base.txt requirements-heavy.txt ./
RUN pip install --no-cache-dir -r requirements-base.txt && \
    pip install --no-cache-dir -r requirements-heavy.txt

# Copy the application source code
COPY . .

# Cleanup build tools and pip cache to reduce size
RUN apt-get remove -y build-essential git && \
    apt-get autoremove -y && \
    rm -rf /root/.cache/pip

# Expose API port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
