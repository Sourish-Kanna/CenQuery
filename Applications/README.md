# Applications

This folder contains the core application components of the CenQuery project, including the backend API, frontend interface, and LLM (Large Language Model) engine for query generation and processing.

## Folder Structure

- **Backend** - FastAPI-based REST API server for handling database queries and business logic
- **Frontend** - Next.js React application for the user interface
- **LLM-Engine** - Python-based service for generating and processing SQL queries using transformer models

## Quick Start Guide

Each sub-folder contains its own README with detailed setup instructions. Follow these general steps:

1. **Backend Setup**: Navigate to [Backend](./Backend/README.md) for API server setup
2. **Frontend Setup**: Navigate to [Frontend](./Frontend/README.md) for UI application setup
3. **LLM-Engine Setup**: Navigate to [LLM-Engine](./LLM-Engine/README.md) for model service setup

## Prerequisites

- Python 3.8+ (for Backend and LLM-Engine)
- Node.js 18+ and npm (for Frontend)
- Database connection details
- GPU support recommended for LLM-Engine

## Development Workflow

``` text
Frontend (React/Next.js) → Backend (FastAPI) → LLM-Engine (Transformers)
         ↓                            ↓                    ↓
    Port 3000                    Port 8000             Port 8001
```

The Frontend communicates with the Backend API, which in turn can call the LLM-Engine for query generation.

## Running All Services

1. Start the Backend: `cd Backend && python main.py`
2. Start the LLM-Engine: `cd LLM-Engine && python main.py`
3. Start the Frontend: `cd Frontend && npm run dev`

Each service can also be run independently based on requirements.

## Additional Documentation

- See parent [README.md](../README.md) for overall project documentation
- See [Database Setup](../DB-Setup/Setup%20DB.py) for database configuration
- See [Diagrams](../Diagrams/) for system architecture and data flow diagrams
