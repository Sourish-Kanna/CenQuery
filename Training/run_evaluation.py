import json
import requests
import re
import pandas as pd
from tqdm import tqdm

# --- CONFIGURATION ---
EVAL_DATASET_PATH = "../Dataset/eval_data/old_eval_(Mixed).jsonl" 
API_BASE_URL = "http://localhost:8000" 
TEST_MODE = "adapter" # Options: "adapter" or "base"
RESULTS_FILE = f"evaluation_results_{TEST_MODE}.csv"
DETAILED_JSONL_FILE = f"detailed_logs_{TEST_MODE}.jsonl"
# ---------------------

def evaluate():
    print(f"🚀 Starting Evaluation Pipeline (Mode: {TEST_MODE.upper()})")
    
    # Clear the detailed log file to start fresh
    open(DETAILED_JSONL_FILE, 'w').close()
    
    # --- LOCAL DATASET LOADING ---
    try:
        with open(EVAL_DATASET_PATH, 'r', encoding='utf-8') as f:
            eval_data = [json.loads(line) for line in f][:5]
    except Exception as e:
        print(f"❌ Failed to load local dataset: {e}")
        return

    total = len(eval_data)
    print(f"📋 Found {total} questions for evaluation.")
    
    exact_matches = 0
    execution_matches = 0
    results_log = []
    
    if TEST_MODE == "adapter":
        generate_endpoint = f"{API_BASE_URL}/generate-select-sql"
    else:
        generate_endpoint = f"{API_BASE_URL}/generate/base"
        
    execute_endpoint = f"{API_BASE_URL}/execute/bare"

    for idx, item in enumerate(tqdm(eval_data, desc="Evaluating")):
        full_text = item.get('text', '')
        
        # 1. Extract the question 
        q_match = re.search(r'`([^`]+)`', full_text)
        if not q_match:
            print(f"\n⚠️ Skipping item {idx}: No question found in backticks.")
            continue
        question = q_match.group(1).strip()
        
        # 2. Extract Ground Truth SQL 
        if "### SQL" not in full_text:
            print(f"\n⚠️ Skipping item {idx}: No '### SQL' marker found.")
            continue
            
        ground_truth_sql = full_text.split("### SQL")[-1].strip().lower()
        if ground_truth_sql.endswith(';'):
            ground_truth_sql = ground_truth_sql[:-1].strip()

        # 3. Call Generation API
        generated_sql = "ERROR"
        llm_data = {}
        try:
            gen_response = requests.post(generate_endpoint, json={"question": question}, timeout=120)
            gen_response.raise_for_status()
            llm_data = gen_response.json()
            
            generated_sql = llm_data.get("sql_query", "").strip().lower()
            if generated_sql.endswith(';'):
                generated_sql = generated_sql[:-1].strip()
        except Exception as e:
            llm_data = {"error": str(e)}

        # 4. Check Exact Match (EM)
        is_em = (generated_sql == ground_truth_sql)
        if is_em:
            exact_matches += 1

        # 5. Check Execution Accuracy (EX)
        is_ex = False
        gt_result = None
        gen_result = None
        
        if generated_sql != "ERROR":
            try:
                # Execute Ground Truth
                gt_resp = requests.post(execute_endpoint, json={"sql_query": ground_truth_sql}, timeout=120)
                gt_result = gt_resp.json().get("result", [])
                
                # Execute Generated
                gen_resp = requests.post(execute_endpoint, json={"sql_query": generated_sql}, timeout=120)
                gen_result = gen_resp.json().get("result", [])
                
                # Compare Results
                if isinstance(gt_result, list) and isinstance(gen_result, list):
                    if gt_result == gen_result:
                        is_ex = True
                        execution_matches += 1
            except Exception as e:
                print(f"\n⚠️ Execution failed for: '{question}' -> {e}")

        # 6. Build and Append the Master JSONL Record
        detailed_record = {
            "id": f"q{idx}",
            "question": question,
            "ground_truth_sql": ground_truth_sql,
            "generated_sql": generated_sql,
            "exact_match": is_em,
            "execution_match": is_ex,
            "llm_api_response": llm_data,
            "ground_truth_db_result": gt_result,
            "generated_db_result": gen_result
        }
        
        with open(DETAILED_JSONL_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(detailed_record) + "\n")

        # 7. Master Summary Log (for standard CSV overview)
        results_log.append({
            "id": f"q{idx}",
            "question": question,
            "ground_truth_sql": ground_truth_sql,
            "generated_sql": generated_sql,
            "exact_match": is_em,
            "execution_match": is_ex,
            "gt_result_sample": str(gt_result)[:100] if gt_result else "ERROR",
            "gen_result_sample": str(gen_result)[:100] if gen_result else "ERROR"
        })

    # --- Metrics Calculation ---
    evaluated_count = len(results_log)
    em_accuracy = (exact_matches / evaluated_count) * 100 if evaluated_count > 0 else 0
    ex_accuracy = (execution_matches / evaluated_count) * 100 if evaluated_count > 0 else 0
    
    df = pd.DataFrame(results_log)
    df.to_csv(RESULTS_FILE, index=False)

    print("\n" + "="*50)
    print(f"🎯 EVALUATION COMPLETE: {TEST_MODE.upper()} MODEL")
    print(f"Total Questions Evaluated : {evaluated_count} out of {total}")
    print(f"Exact Match (EM) Accuracy : {em_accuracy:.2f}% ({exact_matches}/{evaluated_count})")
    print(f"Execution (EX) Accuracy   : {ex_accuracy:.2f}% ({execution_matches}/{evaluated_count})")
    print(f"Summary saved to          : {RESULTS_FILE}")
    print(f"Detailed JSONL saved to   : {DETAILED_JSONL_FILE}")
    print("="*50)

if __name__ == "__main__":
    evaluate()