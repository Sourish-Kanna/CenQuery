from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from constants import GenerateSQLRequest, GenerateSQLResponse, ExecuteSQLRequest, ExecuteSQLResponse

# Import our core logic module
from sql_engine import generate_sql, execute_and_heal, execute_bare

# --- Swagger UI Metadata ---
tags_metadata = [
    {
        "name": "Production (Adapter & Healing)",
        "description": "Endpoints used by the frontend application. Uses the 650-question CenQuery adapter and includes auto-healing SQL execution.",
    },
    {
        "name": "Benchmarking",
        "description": "Endpoints used for the 350-question unseen evaluation dataset. Bypasses error healing to measure raw Llama-3-SQLCoder-8B performance.",
    },
]

# --- App Initialization ---
app = FastAPI(
    title="CenQuery API (Dual-Mode Engine)", 
    version="5.3.0",
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==========================================
# ℹ️ SYSTEM ROUTE
# ==========================================
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "CenQuery Service B (Dual-Mode Engine) is Online"}

# ==========================================
# 🚀 PRODUCTION ENDPOINTS
# ==========================================

@app.post("/generate-select-sql", response_model=GenerateSQLResponse, tags=["Production (Adapter & Healing)"])
async def generate_sql_adapter(request: GenerateSQLRequest):
    """Generates SQL using the fine-tuned CenQuery adapter."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Empty question.")
    
    print(f"Received question: {request.question}")
    try:
        response_data = generate_sql(request.question, use_adapter=True)
        return GenerateSQLResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-sql", response_model=ExecuteSQLResponse, tags=["Production (Adapter & Healing)"])
async def execute_sql_robust(request: ExecuteSQLRequest):
    """Executes SQL against the Indian Census database with active error patching and retry loops."""

    print(f"Received question: {request.question}")
    try:
        execution_data = execute_and_heal(request.sql_query, request.question)
        return ExecuteSQLResponse(**execution_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 📊 BENCHMARKING ENDPOINTS
# ==========================================

@app.post("/generate/base", response_model=GenerateSQLResponse, tags=["Benchmarking"])
async def generate_sql_base(request: GenerateSQLRequest):
    """Generates SQL using the raw Llama-3-SQLCoder-8B model (bypasses adapter)."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Empty question.")
    
    print(f"Received question: {request.question}")
    try:
        response_data = generate_sql(request.question, use_adapter=False)
        return GenerateSQLResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/generate/adapter", response_model=GenerateSQLResponse, tags=["Benchmarking"])
async def generate_sql_benchmark_adapter(request: GenerateSQLRequest):
    """Generates SQL using the fine-tuned CenQuery adapter."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Empty question.")
    
    print(f"Received question: {request.question}")
    try:
        response_data = generate_sql(request.question, use_adapter=True)
        return GenerateSQLResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute/bare", response_model=ExecuteSQLResponse, tags=["Benchmarking"])
async def execute_sql_bare(request: ExecuteSQLRequest):
    """Raw execution without any safety checks, regex patching, or healing (for Exact Match / Execution Accuracy metrics)."""

    print(f"Received question: {request.question}")
    try:
        execution_data = execute_bare(request.sql_query, request.question)
        return ExecuteSQLResponse(**execution_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
