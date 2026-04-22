FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY api ./api
COPY collectors ./collectors
COPY storage ./storage
COPY tests ./tests

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose API port
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]