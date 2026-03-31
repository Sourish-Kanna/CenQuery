import json
from time import sleep
import requests
import re
import pandas as pd
from tqdm import tqdm
import os

# --- CONFIGURATION ---
EVAL_DATASET_PATH = "old_eval_(Mixed).jsonl" 
API_BASE_URL = "http://localhost:8000" 
TEST_MODE = "adapter" 
RESULTS_FILE = f"eval/evaluation_results_{TEST_MODE}.csv"
DETAILED_JSONL_FILE = f"eval/detailed_logs_{TEST_MODE}.jsonl"

# Endpoint Mapping
GENERATE_ENDPOINT = f"{API_BASE_URL}/generate/{TEST_MODE}"
EXECUTE_ENDPOINT = f"{API_BASE_URL}/execute/bare"

def extract_ground_truth(text):
    match = re.search(r'### SQL\n(.+)', text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_question(text):
    match = re.search(r'`([^`]+)`', text)
    return match.group(1).strip() if match else ""

def evaluate():
    print(f"🚀 Starting Evaluation Pipeline (Mode: {TEST_MODE.upper()})")
    if not os.path.exists(EVAL_DATASET_PATH):
        print(f"❌ Error: Dataset not found at {EVAL_DATASET_PATH}")
        return

    os.makedirs("eval", exist_ok=True)

    with open(EVAL_DATASET_PATH, 'r', encoding='utf-8') as f:
        eval_data = [json.loads(line) for line in f]

    exact_matches = 0
    execution_matches = 0
    results_log = []
    eval_data = eval_data[:] # Set your desired limit
    
    # Clear logs
    open(DETAILED_JSONL_FILE, 'w').close()

    for idx, item in enumerate(tqdm(eval_data, desc="Evaluating")):
        raw_text = item.get('text', "")
        gt_sql = extract_ground_truth(raw_text).lower().replace(';', '').strip()
        question = extract_question(raw_text)

        # 1. Generate SQL
        generated_sql = "ERROR"
        gen_error = None
        try:
            gen_resp = requests.post(GENERATE_ENDPOINT, json={"question": question}, timeout=(5, 300))
            gen_resp.raise_for_status()
            generated_sql = gen_resp.json().get("sql_query", "").strip().lower().replace(';', '').strip()
        except Exception as e:
            gen_error = str(e)
            generated_sql = "GENERATION_FAILED"

        # 2. Exact Match
        is_em = (generated_sql == gt_sql)
        if is_em: exact_matches += 1

        # 3. Execution & Result Capture
        is_ex = False
        gt_res, gen_res = None, None
        exec_error = None

        try:
            # Get Ground Truth Result
            gt_payload = {"sql_query": gt_sql, "question": question}
            gt_data = requests.post(EXECUTE_ENDPOINT, json=gt_payload, timeout=(5, 300)).json()
            gt_res = gt_data.get("result")

            # Get Generated Result
            if generated_sql != "GENERATION_FAILED":
                gen_payload = {"sql_query": generated_sql, "question": question}
                gen_data = requests.post(EXECUTE_ENDPOINT, json=gen_payload, timeout=(5, 300)).json()
                gen_res = gen_data.get("result")
                
                # Check for execution status in response
                if gen_data.get("status") == "error":
                    exec_error = gen_res # Backend returns error string in result field on error
                
                # Logic Comparison
                if isinstance(gt_res, list) and isinstance(gen_res, list) and gt_res == gen_res:
                    is_ex = True
                    execution_matches += 1
        except Exception as e:
            exec_error = f"Request Exception: {str(e)}"

        # 4. Logging with Full Context
        log_entry = {
            "id": idx,
            "question": question,
            "gt_sql": gt_sql,
            "gen_sql": generated_sql,
            "em": is_em,
            "ex": is_ex,
            "gt_result": gt_res,        # Actual data returned by GT
            "gen_result": gen_res,      # Actual data returned by Model
            "errors": {
                "generation": gen_error,
                "execution": exec_error
            }
        }
        results_log.append(log_entry)
        
        with open(DETAILED_JSONL_FILE, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

        sleep(0.3)

    # Summary
    total = len(results_log)
    pd.DataFrame(results_log).to_csv(RESULTS_FILE, index=True)

    print("\n" + "="*50)
    print(f"📊 FINAL RESULTS: {TEST_MODE.upper()}")
    print(f"Exact Match: {(exact_matches/total)*100:.2f}%")
    print(f"Execution Accuracy: {(execution_matches/total)*100:.2f}%")
    print(f"Logs saved to: {DETAILED_JSONL_FILE}")
    print("="*50)

if __name__ == "__main__":
    evaluate()