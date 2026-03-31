import json
import requests
import re
import pandas as pd
from tqdm import tqdm
import os

# --- CONFIGURATION ---
# Based on your repo structure: Training/run_evaluation.py
EVAL_DATASET_PATH = "../Dataset/eval_data/eval_(Mixed).jsonl" 
API_BASE_URL = "http://localhost:8000" 
TEST_MODE = "adapter" # Options: "adapter" or "base"
RESULTS_FILE = f"evaluation_results_{TEST_MODE}.csv"
DETAILED_JSONL_FILE = f"detailed_logs_{TEST_MODE}.jsonl"

# 1. Generation Endpoint Mapping (Matches Backend/main.py tags)
if TEST_MODE == "adapter":
    GENERATE_ENDPOINT = f"{API_BASE_URL}/generate/adapter"
else:
    GENERATE_ENDPOINT = f"{API_BASE_URL}/generate/base"

# 2. Execution Endpoint Mapping (Matches @app.post("/execute/bare"))
EXECUTE_ENDPOINT = f"{API_BASE_URL}/execute/bare"
# ---------------------

def extract_question(item):
    """Extracts question from 'prompt' or 'text' fields in the JSONL."""
    content = item.get('prompt') or item.get('text') or ""
    match = re.search(r'`([^`]+)`', content)
    return match.group(1).strip() if match else content.split("\n")[0].strip()

def evaluate():
    print(f"🚀 Starting Evaluation Pipeline (Mode: {TEST_MODE.upper()})")
    print(f"📡 Using Benchmarking Endpoints:")
    print(f"   - Gen: {GENERATE_ENDPOINT}")
    print(f"   - Exe: {EXECUTE_ENDPOINT}")

    if not os.path.exists(EVAL_DATASET_PATH):
        print(f"❌ Error: Dataset not found at {EVAL_DATASET_PATH}")
        return

    with open(EVAL_DATASET_PATH, 'r', encoding='utf-8') as f:
        eval_data = [json.loads(line) for line in f]

    exact_matches = 0
    execution_matches = 0
    results_log = []

    # Clear logs
    open(DETAILED_JSONL_FILE, 'w').close()

    for idx, item in enumerate(tqdm(eval_data, desc="Evaluating")):
        # Get Ground Truth (completion field)
        gt_sql = (item.get('completion') or "").strip().lower()
        if gt_sql.endswith(';'): gt_sql = gt_sql[:-1].strip()

        question = extract_question(item)

        # Step 1: Generate SQL (adapter vs base)
        generated_sql = "ERROR"
        try:
            # Backend expects {"question": "..."} for GenerateSQLRequest
            gen_resp = requests.post(GENERATE_ENDPOINT, json={"question": question}, timeout=120)
            gen_resp.raise_for_status()
            generated_sql = gen_resp.json().get("sql_query", "").strip().lower()
            if generated_sql.endswith(';'): generated_sql = generated_sql[:-1].strip()
        except Exception as e:
            generated_sql = f"GEN_ERROR: {str(e)}"

        # Step 2: Check Exact Match (EM)
        is_em = (generated_sql == gt_sql)
        if is_em: exact_matches += 1

        # Step 3: Check Execution Accuracy (EX) using /execute/bare
        is_ex = False
        gt_res, gen_res = None, None

        if "ERROR" not in generated_sql:
            try:
                # Backend expects ExecuteSQLRequest: {"sql_query": "...", "question": "..."}
                gt_payload = {"sql_query": gt_sql, "question": question}
                gen_payload = {"sql_query": generated_sql, "question": question}

                gt_res = requests.post(EXECUTE_ENDPOINT, json=gt_payload, timeout=60).json().get("result")
                gen_res = requests.post(EXECUTE_ENDPOINT, json=gen_payload, timeout=60).json().get("result")

                if isinstance(gt_res, list) and isinstance(gen_res, list) and gt_res == gen_res:
                    is_ex = True
                    execution_matches += 1
            except Exception:
                pass

        # Step 4: Logging
        log_entry = {
            "id": idx,
            "question": question,
            "gt_sql": gt_sql,
            "gen_sql": generated_sql,
            "em": is_em,
            "ex": is_ex
        }
        results_log.append(log_entry)
        
        with open(DETAILED_JSONL_FILE, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    # --- Summary ---
    total = len(results_log)
    df = pd.DataFrame(results_log)
    df.to_csv(RESULTS_FILE, index=False)

    print("\n" + "="*50)
    print(f"📊 RESULTS: {TEST_MODE.upper()}")
    print(f"Exact Match Accuracy: {(exact_matches/total)*100:.2f}%")
    print(f"Execution Accuracy:   {(execution_matches/total)*100:.2f}%")
    print("="*50)

if __name__ == "__main__":
    evaluate()