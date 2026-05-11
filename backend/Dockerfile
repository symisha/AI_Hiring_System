# 1. Use a stable Python base
FROM python:3.10-slim

# 2. Install system-level dependencies
# we need build-essential for gcc, and portaudio for PyAudio
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    python3-all-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Set working directory
WORKDIR /app

# 4. Copy and install dependencies
# We use the extra-index-url specifically for the +cpu torch version
COPY requirements_full.txt .
RUN pip install --no-cache-dir -r requirements_full1.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 5. Copy the rest of your backend code
COPY . .

# 6. Start the server
# Railway/Koyeb will provide the $PORT variable automatically
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT