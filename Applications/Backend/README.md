# Backend API Setup Guide

The Backend is a FastAPI-based REST API server that handles database queries, SQL generation, and business logic for the CenQuery project.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Database (configured and running)
- Virtual environment (recommended)

## Installation

### 1. Create Virtual Environment

```bash
# Navigate to Backend directory
cd Applications/Backend

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

## Configuration

### Environment Variables

Create a `.env` file in the Backend folder with the following variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///./cenquery.db
# or for other databases:
# DATABASE_URL=postgresql://user:password@localhost:5432/cenquery

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# LLM Engine
LLM_ENGINE_URL=http://localhost:8001

# Optional: Add other configuration as needed
```

### Database Setup

If not already done, initialize the database:

```bash
# Run database setup
cd ../../DB-Setup
python "Setup DB.py"
```

## Running the Server

### Development Mode

```bash
cd Applications/Backend
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Main Endpoints

### Query Generation & Execution
- `POST /api/generate-sql` - Generate SQL from natural language question
- `POST /api/execute-sql` - Execute generated SQL query
- `POST /api/execute-bare` - Execute SQL with auto-healing

### Health Check
- `GET /health` - Server health status

## File Structure

```
Backend/
├── main.py                 # FastAPI application and endpoints
├── sql_engine.py          # Core SQL generation and execution logic
├── requirements.txt       # Python dependencies
├── requirements.in        # Source requirements file
├── database_schema.json   # Database schema definition
└── data/                  # Data files
```

## Development Notes

### Key Components

- **main.py**: Defines FastAPI app, routes, and Pydantic models
- **sql_engine.py**: Contains SQL generation, execution, and healing logic
- **database_schema.json**: Database structure definition used by the LLM engine

### Testing Endpoints

Use the interactive Swagger UI at `/docs` to test endpoints, or use curl/Postman:

```bash
# Example: Generate SQL
curl -X POST "http://localhost:8000/api/generate-sql" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the total count of patients?"}'
```

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:

```bash
python main.py --port 8080
```

### Database Connection Error
- Ensure database is initialized
- Check DATABASE_URL environment variable
- Verify database credentials and network connectivity

### LLM Engine Connection Error
- Ensure LLM-Engine is running on http://localhost:8001
- Check LLM_ENGINE_URL environment variable
- Verify network connectivity between services

## Performance Tips

- Use a production ASGI server (Uvicorn) for deployment
- Enable query caching for frequently asked questions
- Monitor API response times using the built-in logging

## See Also

- [LLM-Engine Setup](../LLM-Engine/README.md) - Required for SQL generation
- [Frontend Setup](../Frontend/README.md) - Consumes this API
- [Database Setup](../../DB-Setup/Setup%20DB.py) - Database initialization
