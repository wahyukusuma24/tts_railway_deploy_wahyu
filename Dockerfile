# Gunakan base image yang ringan
FROM python:3.10-slim

# Set direktori kerja
WORKDIR /app

# Install dependensi sistem minimum
RUN apt-get update && apt-get install -y \
    libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

# Salin requirements dan install dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Salin semua source code, kecuali file besar
COPY . .

# Jalankan aplikasi dengan Uvicorn
CMD ["uvicorn", "tts_server:app", "--host", "0.0.0.0", "--port", "8000"]
