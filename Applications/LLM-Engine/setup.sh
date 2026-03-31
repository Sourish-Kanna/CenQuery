#!/bin/bash

# Configuration
REPO_URL="https://github.com/Sourish-Kanna/CenQuery.git"
BRANCH="stable" 

# 1. Setup/Update Project
echo "Cloning stable branch..."
git clone -b $BRANCH $REPO_URL
cd CenQuery

cd LLM-Engine

# 2. Cleanup existing containers (Ensures VRAM is freed)
docker stop vllm cenquery-engine 2>/dev/null || true
docker rm vllm cenquery-engine 2>/dev/null || true

# 3. Build and Run
docker build -t cenquery-api .

docker run -d \
  --gpus all \
  --restart always \
  --name cenquery-engine \
  -e PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True" \
  -p 8001:8000 \
  -v $(pwd)/model_cache:/app/model_cache \
  cenquery-api

echo -e "\n✅ CenQuery Engine deployment initiated on port 8001"
echo "Check progress with: docker logs -f cenquery-engine"

#!/bin/bash

# 1. Ensure SSH is allowed first to prevent lockout
echo "🔓 Allowing SSH..."
ufw allow ssh

# 2. Set default policies
echo "🛡️ Setting default policies (Deny Incoming, Allow Outgoing)..."
ufw default deny incoming
ufw default allow outgoing

# 3. Allow port 8001 for ANY IP address
echo "🚀 Opening port 8001 to the world..."
ufw allow 8001/tcp

# 4. Enable the firewall
echo "🔥 Enabling UFW..."
echo "y" | ufw enable

# 5. Show status
echo "📊 Current Firewall Status:"
ufw status numbered