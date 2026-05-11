FROM python:3.10-slim

# Install ffmpeg (REQUIRED for the audio bridge) and build tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements from the current folder (backend/)
COPY requirements_full.txt .

# Install using the +cpu index for smaller image size
RUN pip install --no-cache-dir -r requirements_full.txt --extra-index-url https://download.pytorch.org/whl/cpu

COPY . .

# Point to the correct entry point
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT