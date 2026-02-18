# %%
# 1. Install Dependencies
!pip install -q fastapi uvicorn pyngrok nest_asyncio torch transformers peft bitsandbytes accelerate huggingface_hub

# %%
# --- MEMORY FIX START ---
import os
# This helps with "fragmentation" errors
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
# --- MEMORY FIX END ---

# 2. Imports
import torch
import gc
import uvicorn
import nest_asyncio
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyngrok import ngrok
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from huggingface_hub import login


# %%
# 4. The Optimized LLM Engine (Merged Logic)
class LLMEngine:
    def __init__(self):
        # --- CONFIGURATION ---
        self.base_model_id = "defog/llama-3-sqlcoder-8b"
        self.adapter_id = "Sourish-Kanna/CenQuery"  # <--- YOUR NEW REPO
        # ---------------------

        # 1. Clean Memory (Crucial for Colab Free Tier)
        print("🧹 Cleaning GPU Memory...")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

        print(f"⏳ Loading Base Model: {self.base_model_id}...")

        # 2. 4-bit Config (NF4 - High Precision Quantization)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )

        # 3. Load Base Model
        self.base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_id,
            device_map="auto",
            quantization_config=bnb_config,
            # dtype=torch.float16, # Managed by bnb_config above
            trust_remote_code=True
        )

        # Disable cache to save VRAM (Good for inference, bad for long chat history)
        self.base_model.config.use_cache = False

        # 4. Load Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_id)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right" # Llama-3 standard for generation

        print(f"⏳ Downloading Adapter from HF: {self.adapter_id}...")
        self.model = PeftModel.from_pretrained(self.base_model, self.adapter_id, is_trainable=False)
        self.model.eval()

        # 5. Define Terminators (Crucial for Llama-3 to stop chatting)
        self.terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        print("✅ System Ready! CenQuery Brain is Online.")

    def generate(self, prompt: str):
        """
        Generates SQL and applies robust cleaning to remove hallucinations.
        """
        # --- MEMORY CLEANUP BEFORE GENERATION ---
        gc.collect()
        torch.cuda.empty_cache()
        # ----------------------------------------
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=300,
                num_return_sequences=1,
                eos_token_id=self.terminators, # Use explicit Llama-3 terminators
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=False # Deterministic
            )

        full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # --- Robust Cleaning Logic ---
        # 1. Remove the Input Prompt
        # (We check if prompt exists in output to avoid errors if context window shifts)
        if prompt in full_output:
            generated_text = full_output.replace(prompt, "").strip()
        else:
            generated_text = full_output # Fallback

        # 2. Handle "### SQL" Header (Style 2 Compliance)
        # If the model repeats the header, split on it.
        if "### SQL" in generated_text:
            generated_text = generated_text.split("### SQL")[-1].strip()

        # 3. Stop Hallucinations (Road trips, explanations, etc.)
        # Stop at "assistant" header or double newlines if no SQL found
        clean_sql = generated_text.split("assistant")[0].split("<|start_header_id|>")[0].strip()

        # If there are multiple queries, take the first one
        if ";" in clean_sql:
            clean_sql = clean_sql.split(";")[0] + ";"

        return clean_sql


# %%
# Initialize App & Engine
app = FastAPI(title="CenQuery LLM Service (Optimized)")
nest_asyncio.apply()
engine = LLMEngine()

# %%
# 5. API Endpoint
class QueryRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_sql(req: QueryRequest):
    try:
        print("Request Start")
        print(req)
        print(f"🔸 Prompt: [{req.prompt}]")
        sql = engine.generate(req.prompt)
        print(f"🔹 Generated: {sql}") # Log for debugging in Colab
        return {"sql": sql}
    except Exception as e:
        print(f"❌ Error: {e}") # Log for debugging in Colab
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "CenQuery LLM Service (Optimized) is Online!"}

# %%
# 6. Start Ngrok
# PASTE YOUR NGROK TOKEN BELOW (Get it from dashboard.ngrok.com)
# NGROK_AUTH_TOKEN = "YOUR_NGROK_TOKEN_HERE"
from google.colab import userdata
NGROK_AUTH_TOKEN = userdata.get('NGROK')
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

public_url = ngrok.connect(8000).public_url
print(f"🚀 Service A is Online at: {public_url}")



# %%
# 7. Run Server
# Apply the patch (Good practice, even if using await)
nest_asyncio.apply()

# Configure the server
config = uvicorn.Config(app, port=8000)
server = uvicorn.Server(config)

# Start the server in the existing loop
# This cell will stay "Busy" [*] - that is normal!
await server.serve()

# %%
from pyngrok import ngrok

# 1. Kill all running tunnels
ngrok.kill()

print("🛑 ngrok tunnels killed. You can now restart the server.")


