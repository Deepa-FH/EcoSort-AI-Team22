# EcoSort AI - CPU-only image that runs on any machine with Docker.
# Build :  docker build -t ecosort-ai .
# Run   :  docker run -p 5000:5000 -e LLM_API_KEY=YOUR_KEY ecosort-ai
#      or  docker run -p 5000:5000 ecosort-ai --api-key YOUR_KEY
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SORTLY_HOST=0.0.0.0 \
    SORTLY_PORT=5000 \
    SORTLY_NO_BROWSER=1 \
    SORTLY_ENABLE_TUNNEL=0 \
    SORTLY_DATA_DIR=/data \
    WASTE_MODEL_PATH=/app/models/best_model.pt

WORKDIR /app

# System libraries needed by OpenCV (used inside Ultralytics).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/*

# CPU-only PyTorch first (much smaller than the default CUDA build), then the rest.
COPY requirements.txt .
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r requirements.txt

# Application code, trained model (5 MB) and sample images. The API key is NOT baked in.
COPY . .
RUN mkdir -p /data

VOLUME /data
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=4)"

# Extra arguments after the image name (e.g. --api-key KEY) are passed to main.py.
ENTRYPOINT ["python", "main.py"]
