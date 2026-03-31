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

if TEST_MODE == "adapter":
    GENERATE_ENDPOINT = f"{API_BASE_URL}/generate/adapter"
else:
    GENERATE_ENDPOINT = f"{API_BASE_URL}/generate/base"

EXECUTE_ENDPOINT = f"{API_BASE_URL}/execute/bare"

def extract_ground_truth(text):
    """Extracts SQL following the '### SQL' marker."""
    match = re.search(r'### SQL\n(.+)', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def extract_question(text):
    """Extracts the question between backticks in the Task section."""
    match = re.search(r'`([^`]+)`', text)
    return match.group(1).strip() if match else ""

def evaluate():
    print(f"🚀 Starting Evaluation Pipeline (Mode: {TEST_MODE.upper()})")
    
    if not os.path.exists(EVAL_DATASET_PATH):
        print(f"❌ Error: Dataset not found at {EVAL_DATASET_PATH}")
        return

    # Ensure log directory exists
    os.makedirs("eval", exist_ok=True)

    with open(EVAL_DATASET_PATH, 'r', encoding='utf-8') as f:
        eval_data = [json.loads(line) for line in f]

    exact_matches = 0
    execution_matches = 0
    results_log = []
    eval_data = eval_data[:10]  # Limit to first 10 for quick testing
    
    # Reset logs
    open(DETAILED_JSONL_FILE, 'w').close()

    for idx, item in enumerate(tqdm(eval_data, desc="Evaluating")):
        raw_text = item.get('text', "")
        
        # --- FIXED EXTRACTION ---
        gt_sql = extract_ground_truth(raw_text).lower()
        if gt_sql.endswith(';'): gt_sql = gt_sql[:-1].strip()
        
        question = extract_question(raw_text)
        # ------------------------

        # Step 1: Generate SQL
        generated_sql = "ERROR"
        try:
            gen_resp = requests.post(GENERATE_ENDPOINT, json={"question": question}, timeout=120)
            gen_resp.raise_for_status()
            generated_sql = gen_resp.json().get("sql_query", "").strip().lower()
            if generated_sql.endswith(';'): generated_sql = generated_sql[:-1].strip()
        except Exception as e:
            generated_sql = f"GEN_ERROR: {str(e)}"

        # Step 2: Exact Match
        is_em = (generated_sql == gt_sql)
        if is_em: exact_matches += 1

        # Step 3: Execution Accuracy
        is_ex = False
        if "ERROR" not in generated_sql:
            try:
                gt_payload = {"sql_query": gt_sql, "question": question}
                gen_payload = {"sql_query": generated_sql, "question": question}

                gt_res = requests.post(EXECUTE_ENDPOINT, json=gt_payload, timeout=60).json().get("result")
                gen_res = requests.post(EXECUTE_ENDPOINT, json=gen_payload, timeout=60).json().get("result")

                if isinstance(gt_res, list) and isinstance(gen_res, list) and gt_res == gen_res:
                    is_ex = True
                    execution_matches += 1
            except Exception:
                pass

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
    sleep(0.5)

if __name__ == "__main__":
    evaluate()