FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU-only PyTorch first (much smaller), then the rest
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir torch==2.2.1 torchvision==0.17.1 \
        --extra-index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r backend/requirements.txt

COPY backend backend
COPY ml ml

RUN useradd -m -u 1000 user && chown -R user /app
USER user

ENV BACKEND_HOST=0.0.0.0 \
    BACKEND_PORT=7860 \
    BACKEND_RELOAD=false \
    ENVIRONMENT=production

WORKDIR /app/backend
EXPOSE 7860
CMD ["python", "app.py"]
