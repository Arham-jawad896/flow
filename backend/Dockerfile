FROM python:3.11-slim

# Optional system dependencies for scientific stack performance
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .

# Create runtime directories
RUN mkdir -p data logs database

# Environment
ENV HOST=0.0.0.0
ENV PORT=7860

EXPOSE 7860

# Start FastAPI with Uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]


