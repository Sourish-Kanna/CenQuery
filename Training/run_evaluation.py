import json
import time
from annotated_types import T
import requests
import re
import pandas as pd
from tqdm import tqdm

# --- CONFIGURATION ---
EVAL_DATASET_PATH = "Dataset/eval_data/eval_(Mixed).jsonl" # Path to your 350-question dataset
API_BASE_URL = "http://localhost:8000" # Change to your Droplet IP if running remotely
TEST_MODE = "adapter" # Options: "adapter" or "base"
RESULTS_FILE = f"evaluation_results_{TEST_MODE}.csv"
# ---------------------

def extract_question(prompt_text):
    """
    Extracts the raw natural language question from the training/eval prompt block.
    Assumes the question is wrapped in backticks like: `What is the population...`
    """
    match = re.search(r'`([^`]+)`', prompt_text)
    if match:
        return match.group(1).strip()
    return prompt_text.split("\n")[0].strip() # Fallback

def evaluate():
    print(f"🚀 Starting Evaluation Pipeline (Mode: {TEST_MODE.upper()})")
    
    with open(EVAL_DATASET_PATH, 'r', encoding='utf-8') as f:
        eval_data = [json.loads(line) for line in f]

    total = len(eval_data)
    print(f"📋 Found {total} questions for evaluation.")
    
    exact_matches = 0
    execution_matches = 0
    results_log = []
    
    generate_endpoint = f"{API_BASE_URL}/generate/{TEST_MODE}" # e.g., /generate/adapter/ or /generate/base/
    execute_endpoint = f"{API_BASE_URL}/execute/bare"

    # Loop through the dataset with a progress bar
    for item in tqdm(eval_data, desc="Evaluating"):
        raw_prompt = item.get('prompt', '') 
        ground_truth_sql = item.get('completion', '').strip().lower()
        if ground_truth_sql.endswith(';'):
            ground_truth_sql = ground_truth_sql[:-1].strip() # Normalize GT
            
        # 1. Extract the raw question to send to the new API
        question = extract_question(raw_prompt)
        
        # 2. Call Generation API
        try:
            gen_response = requests.post(generate_endpoint, json={"question": question}, timeout=60)
            gen_response.raise_for_status()
            generated_sql = gen_response.json().get("sql_query", "").strip().lower()
            if generated_sql.endswith(';'):
                generated_sql = generated_sql[:-1].strip() # Normalize Gen
        except Exception as e:
            print(f"\n⚠️ Generation failed for: {question} -> {e}")
            generated_sql = "ERROR"

        # 3. Check Exact Match (EM)
        is_em = (generated_sql == ground_truth_sql)
        if is_em:
            exact_matches += 1

        # 4. Check Execution Accuracy (EX)
        is_ex = False
        gt_result = None
        gen_result = None
        
        # Only test execution if we generated something valid
        if generated_sql != "ERROR":
            try:
                # Execute Ground Truth
                gt_resp = requests.post(execute_endpoint, json={"sql_query": ground_truth_sql}, timeout=30)
                gt_result = gt_resp.json().get("result", [])
                
                # Execute Generated
                gen_resp = requests.post(execute_endpoint, json={"sql_query": generated_sql}, timeout=30)
                gen_result = gen_resp.json().get("result", [])
                
                # Compare Results (Ignore ordering differences if they contain the same data)
                if isinstance(gt_result, list) and isinstance(gen_result, list):
                    # Convert list of dicts to string for easy comparison, or do deep comparison
                    if gt_result == gen_result:
                        is_ex = True
                        execution_matches += 1
            except Exception as e:
                pass # Execution failed (syntax error, timeout, etc.)

        # 5. Log for Paper/Analysis
        results_log.append({
            "question": question,
            "ground_truth_sql": ground_truth_sql,
            "generated_sql": generated_sql,
            "exact_match": is_em,
            "execution_match": is_ex,
            "gt_result_sample": str(gt_result)[:100] if gt_result else "ERROR",
            "gen_result_sample": str(gen_result)[:100] if gen_result else "ERROR"
        })

    # --- Metrics Calculation ---
    em_accuracy = (exact_matches / total) * 100
    ex_accuracy = (execution_matches / total) * 100
    
    # Save to CSV for Paper 2 charts
    df = pd.DataFrame(results_log)
    df.to_csv(RESULTS_FILE, index=False)

    print("\n" + "="*50)
    print(f"🎯 EVALUATION COMPLETE: {TEST_MODE.upper()} MODEL")
    print(f"Total Questions Evaluated : {total}")
    print(f"Exact Match (EM) Accuracy : {em_accuracy:.2f}% ({exact_matches}/{total})")
    print(f"Execution (EX) Accuracy   : {ex_accuracy:.2f}% ({execution_matches}/{total})")
    print(f"Detailed logs saved to    : {RESULTS_FILE}")
    print("="*50)

if __name__ == "__main__":
    # Ensure your FastAPI server is running before executing this script!
    evaluate()