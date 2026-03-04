#!/bin/bash

# Configuration
REPO_URL="https://github.com/Sourish-Kanna/CenQuery.git"
BRANCH="stable" 

# 1. Setup/Update Project
cd /root
if [ -d "CenQuery" ]; then
    echo "Updating existing repository..."
    cd CenQuery && git fetch origin && git checkout $BRANCH && git pull origin $BRANCH
else
    echo "Cloning stable branch..."
    git clone -b $BRANCH $REPO_URL
    cd CenQuery
fi

cd LLM-Engine

# 2. Cleanup existing containers
docker stop vllm cenquery-engine 2>/dev/null || true
docker rm vllm cenquery-engine 2>/dev/null || true

# 3. Build and Run
docker build -t cenquery-api .
docker run -d \
  --gpus all \
  --restart always \
  --name cenquery-engine \
  -p 8001:8000 \
  -v $(pwd)/model_cache:/app/model_cache \
  cenquery-api

echo -e "\n✅ CenQuery Engine deployment initiated on port 8001"
echo "Check progress with: docker logs -f cenquery-engine"