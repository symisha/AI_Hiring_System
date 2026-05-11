FROM python:3.10-slim

# Install system dependencies (essential for pydub and PyAudio)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements from the Backend folder
COPY Backend/requirements_full.txt .
RUN pip install --no-cache-dir -r requirements_full.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy the entire Backend folder content into the Docker /app directory
COPY Backend/ .

# Run uvicorn (assuming main.py is in Backend/app/main.py)
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT