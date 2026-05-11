# 1. Use a Python base image
FROM python:3.10-slim

# 2. Set the directory inside the container
WORKDIR /app

# 3. Copy your requirements and install them
COPY requirements_full.txt .
RUN pip install --no-cache-dir -r requirements_full.txt --extra-index-url https://download.pytorch.org/whl/cpu
# 4. Copy the rest of your code
COPY . .

# 5. Start the app (Railway provides the PORT)
CMD uvicorn main:app --host 0.0.0.0 --port $PORT