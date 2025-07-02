FROM python:3.10-slim

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app files
COPY ./app /app

# Expose port for Railway
ENV PORT 8000
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "tts_server:app", "--host", "0.0.0.0", "--port", "8000"]
