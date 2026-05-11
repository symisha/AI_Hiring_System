FROM python:3.10-slim

# 1. Install system dependencies 
# Added ffmpeg for the audio conversion bridge and build-essential for PyAudio/pydub
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Fix the typo: Reference the actual file copied
# Your latest commit changed the COPY source but left the pip filename as '...full1.txt'
COPY requirements_full.txt .

# 3. Install from the correct file
RUN pip install --no-cache-dir -r requirements_full.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 4. Copy the rest of the backend code
COPY . .

# 5. Start the server (pointing to your app entry in main.py)
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT