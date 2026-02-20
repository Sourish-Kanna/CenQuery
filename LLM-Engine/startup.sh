#!/bin/bash
# Setup Project
cd /root
git clone https://github.com/Sourish-Kanna/CenQuery.git
cd CenQuery/LLM-Engine

# Clear the default DigitalOcean vLLM container
docker stop vllm || true
docker rm vllm || true

# Build and Run CenQuery Engine on Port 8001
docker build -t cenquery-api .
docker run -d \
  --gpus all \
  --restart always \
  --name cenquery-engine \
  -p 8001:8000 \
  -v $(pwd)/model_cache:/app/model_cache \
  cenquery-api
