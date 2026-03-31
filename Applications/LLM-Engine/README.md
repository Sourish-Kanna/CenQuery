# LLM-Engine Setup Guide

The LLM-Engine is a FastAPI-based service that provides SQL query generation using fine-tuned Large Language Models. It uses the Llama-3-SQLCoder model with a CenQuery adapter for generating SQL queries from natural language questions.

## Prerequisites

- Python 3.8 or higher
- CUDA 12.1 or higher (for GPU support)
- GPU with at least 16GB VRAM (8GB minimum with quantization)
- pip (Python package manager)
- Virtual environment (recommended)

## System Requirements

### Minimum GPU Requirements
- **With Quantization (4-bit)**: 8GB VRAM minimum
- **Recommended**: 16GB or more VRAM for optimal performance

### Disk Space
- ~20GB for model downloads (models are cached)

## Installation

### 1. Create Virtual Environment

```bash
# Navigate to LLM-Engine directory
cd Applications/LLM-Engine

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (API framework)
- PyTorch with CUDA support
- Transformers (Hugging Face)
- PEFT (Parameter-Efficient Fine-Tuning)
- BitsAndBytes (Quantization)

## Configuration

### Environment Variables

Create a `.env` file in the LLM-Engine folder with the following variables:

```env
# API Configuration
LLMENGINE_HOST=0.0.0.0
LLMENGINE_PORT=8001

# Model Configuration
BASE_MODEL=defog/llama-3-sqlcoder-8b
ADAPTER_MODEL=Sourish-Kanna/CenQuery

# GPU/CUDA Configuration
CUDA_VISIBLE_DEVICES=0

# HuggingFace Settings
HF_TOKEN=your_huggingface_token_here  # Optional, for private models
```

### HuggingFace Authentication

If using private models, authenticate with Hugging Face:

```bash
huggingface-cli login
```

## Running the Service

### Development Mode

```bash
cd Applications/LLM-Engine
python main.py
```

The service will be available at `http://localhost:8001`

### Production Mode with Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1
```

### Expected Output

```
🧹 Cleaning GPU Memory...
⏳ Loading Base Model: defog/llama-3-sqlcoder-8b...
⏳ Downloading Adapter: Sourish-Kanna/CenQuery...
🔥 Warming up engine...
INFO:     Uvicorn running on http://0.0.0.0:8001
```

## Model Information

### Base Model
- **Model**: defog/llama-3-sqlcoder-8b
- **Framework**: Llama-3-8B optimized for SQL generation
- **Language**: SQL, Python, Natural Language
- **License**: Community License

### CenQuery Adapter
- **Type**: LoRA Adapter
- **Size**: ~50MB
- **Training**: Fine-tuned on CenQuery dataset
- **Quantization**: 4-bit for memory efficiency

### Model Loading Process

1. Downloads and loads the base Llama-3-SQLCoder-8B model
2. Applies 4-bit quantization to reduce memory usage
3. Loads the CenQuery LoRA adapter weights
4. Sets model to evaluation mode
5. Warms up the engine with initial inference

## API Endpoints

### Health Check
- `GET /health` - Server health status
- `GET /models` - List loaded models

### SQL Generation
- `POST /generate` - Generate SQL from natural language question

Example request:

```bash
curl -X POST "http://localhost:8001/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the total count of patients?",
    "schema": "table_name(column_name type, ...)"
  }'
```

## File Structure

```
LLM-Engine/
├── main.py              # FastAPI application and LLM engine
├── requirements.txt     # Python dependencies
├── dockerfile           # Docker configuration
├── setup.sh            # Setup script (Linux/macOS)
├── run.txt             # Running instructions
└── Tunnel.ipynb        # Jupyter notebook for tunneling
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t cenquery-llm-engine:latest .
```

### Run Docker Container

```bash
# With GPU support
docker run --gpus all \
  -p 8001:8001 \
  -e PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True" \
  -v llm_cache:/app/model_cache \
  cenquery-llm-engine:latest

# Check logs
docker logs -f container_id
```

### Docker Volumes

Create a Docker volume for model caching to avoid re-downloading models:

```bash
docker volume create llm_cache
```

## Performance Tips

### GPU Optimization
- Use `CUDA_VISIBLE_DEVICES` to specify which GPU to use
- Monitor GPU memory with `nvidia-smi`
- Use 4-bit quantization for reduced memory footprint

### Inference Optimization
- Batch requests when possible
- Use output caching if same questions are repeated
- Adjust `max_tokens` for faster generation

## Troubleshooting

### GPU Not Detected

```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Out of Memory Error

- Ensure no other GPU processes are running
- Reduce `max_batch_size` if processing batches
- Check GPU with: `nvidia-smi`

### Model Download Fails

```bash
# Clear HuggingFace cache and retry
rm -rf ~/.cache/huggingface/hub
python main.py
```

### Slow Inference

- First inference is slow due to model warming up
- Subsequent inferences should be faster
- Check GPU utilization with `nvidia-smi`

## Testing Endpoints

Use the interactive API documentation:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Performance Benchmarks

Expected inference times (on GPU with quantization):
- Cold start (first query): 10-20 seconds
- Warm queries: 5-10 seconds per query
- Batch processing: More efficient than individual queries

## Advanced Configuration

### Custom Model Loading

Edit `main.py` to change:

```python
self.base_model_id = "your-model-id"
self.adapter_id = "your-adapter-id"
```

### Quantization Settings

Modify BitsAndBytesConfig in `main.py` for different precision levels:

```python
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,  # Can change to 8bit
    bnb_4bit_quant_type="nf4",  # fp4 for different performance
    bnb_4bit_compute_dtype=torch.float16,
)
```

## See Also

- [Backend Setup](../Backend/README.md) - API that calls this engine
- [Frontend Setup](../Frontend/README.md) - User interface
- [PyTorch Documentation](https://pytorch.org/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [PEFT Documentation](https://huggingface.co/docs/peft/)
