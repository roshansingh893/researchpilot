FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# FastAPI: 8000
# Gradio: 7860
# EXPOSE 8000 7860

# Deployment CMD will be configured in a later phase.
