# Start from a minimal Python base image
FROM python:3.10-slim

# Prevents Python from writing .pyc files and enables direct output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install only torch separately to optimize cache & size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.0.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Copy and install remaining requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose port
EXPOSE 8000

# Final cleanup to reduce image size
RUN apt-get remove -y build-essential git && \
    apt-get autoremove -y && \
    rm -rf /root/.cache/pip

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
