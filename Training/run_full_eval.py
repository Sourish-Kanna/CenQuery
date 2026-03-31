import json
from time import sleep, time
import requests
import re
import pandas as pd
from tqdm import tqdm
import os

# --- CONFIGURATION ---
EVAL_DATASET_PATH = "old_eval_(Mixed).jsonl" 
API_BASE_URL = "http://localhost:8000" 

# File Output Paths
OUT = {
    "adapter_bare": {"csv": "eval/results_adapter_bare.csv", "jsonl": "eval/logs_adapter_bare.jsonl"},
    "adapter_heal": {"csv": "eval/results_adapter_healed.csv", "jsonl": "eval/logs_adapter_healed.jsonl"},
    "base":         {"csv": "eval/results_base_bare.csv",    "jsonl": "eval/logs_base_bare.jsonl"}
}

# Endpoints
ENDPOINTS = {
    "gen_adapter": f"{API_BASE_URL}/generate/adapter",
    "gen_base":    f"{API_BASE_URL}/generate/base",
    "exe_bare":    f"{API_BASE_URL}/execute/bare",
    "exe_heal":    f"{API_BASE_URL}/execute-sql"
}

def extract_ground_truth(text):
    match = re.search(r'### SQL\n(.+)', text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_question(text):
    match = re.search(r'`([^`]+)`', text)
    return match.group(1).strip() if match else ""

def evaluate():
    print(f"🚀 Starting Triple-Mode Evaluation (Adapter, Healed, Base)")
    if not os.path.exists(EVAL_DATASET_PATH): return print(f"❌ Dataset not found")

    os.makedirs("eval", exist_ok=True)
    with open(EVAL_DATASET_PATH, 'r', encoding='utf-8') as f:
        eval_data = [json.loads(line) for line in f]

    # Initialize Log Lists
    logs = {"adapter_bare": [], "adapter_heal": [], "base": []}
    
    # Initialize Statistics
    stats = {mode: {"em": 0, "ex": 0, "gen_lat": [], "exe_lat": []} for mode in logs.keys()}

    # Clear JSONL files
    for paths in OUT.values(): open(paths["jsonl"], 'w').close()

    for idx, item in enumerate(tqdm(eval_data, desc="Total Progress")):
        raw_text = item.get('text', "")
        gt_sql = extract_ground_truth(raw_text).lower().replace(';', '').strip()
        question = extract_question(raw_text)

        # --- PHASE 1: GROUND TRUTH RESULT ---
        # Get baseline data once per question
        try:
            gt_res = requests.post(ENDPOINTS["exe_bare"], json={"sql_query": gt_sql, "question": question}, timeout=60).json().get("result")
        except: gt_res = "GT_EXEC_ERROR"

        # --- PHASE 2: ADAPTER MODES (Bare & Healed) ---
        # 1. Generate via Adapter
        s_gen = time()
        try:
            resp = requests.post(ENDPOINTS["gen_adapter"], json={"question": question}, timeout=(5, 300)).json()
            sql_a = resp.get("sql_query", "").strip().lower().replace(';', '').strip()
            stats["adapter_bare"]["gen_lat"].append(time() - s_gen)
            stats["adapter_heal"]["gen_lat"].append(time() - s_gen)
        except: sql_a = "GEN_FAILED"

        # 2. Bare Execution
        s_exe = time()
        is_ex_bare = False
        try:
            res_bare = requests.post(ENDPOINTS["exe_bare"], json={"sql_query": sql_a, "question": question}, timeout=60).json().get("result")
            stats["adapter_bare"]["exe_lat"].append(time() - s_exe)
            if isinstance(gt_res, list) and res_bare == gt_res:
                is_ex_bare = True
                stats["adapter_bare"]["ex"] += 1
        except: res_bare = "EXE_ERROR"

        # 3. Healed Execution
        s_exe = time()
        is_ex_heal = False
        try:
            h_resp = requests.post(ENDPOINTS["exe_heal"], json={"sql_query": sql_a, "question": question}, timeout=60).json()
            res_heal = h_resp.get("result")
            stats["adapter_heal"]["exe_lat"].append(time() - s_exe)
            if isinstance(gt_res, list) and res_heal == gt_res:
                is_ex_heal = True
                stats["adapter_heal"]["ex"] += 1
        except: res_heal = "EXE_ERROR"

        # --- PHASE 3: BASE MODEL MODE ---
        # 1. Generate via Base
        s_gen = time()
        try:
            resp = requests.post(ENDPOINTS["gen_base"], json={"question": question}, timeout=(5, 300)).json()
            sql_b = resp.get("sql_query", "").strip().lower().replace(';', '').strip()
            stats["base"]["gen_lat"].append(time() - s_gen)
        except: sql_b = "GEN_FAILED"

        # 2. Base Execution
        s_exe = time()
        is_ex_base = False
        try:
            res_base = requests.post(ENDPOINTS["exe_bare"], json={"sql_query": sql_b, "question": question}, timeout=60).json().get("result")
            stats["base"]["exe_lat"].append(time() - s_exe)
            if isinstance(gt_res, list) and res_base == gt_res:
                is_ex_base = True
                stats["base"]["ex"] += 1
        except: res_base = "EXE_ERROR"

        # --- LOGGING ---
        em_a = (sql_a == gt_sql)
        em_b = (sql_b == gt_sql)
        if em_a: stats["adapter_bare"]["em"] += 1; stats["adapter_heal"]["em"] += 1
        if em_b: stats["base"]["em"] += 1

        # Build log entries
        log_data = {
            "adapter_bare": {"id": idx, "q": question, "gt": gt_sql, "gen": sql_a, "em": em_a, "ex": is_ex_bare, "res": res_bare},
            "adapter_heal": {"id": idx, "q": question, "gt": gt_sql, "gen": sql_a, "em": em_a, "ex": is_ex_heal, "res": res_heal},
            "base":         {"id": idx, "q": question, "gt": gt_sql, "gen": sql_b, "em": em_b, "ex": is_ex_base, "res": res_base}
        }

        for m in logs.keys():
            logs[m].append(log_data[m])
            with open(OUT[m]["jsonl"], 'a') as f: f.write(json.dumps(log_data[m]) + "\n")

    # --- SAVE & REPORT ---
    for m in logs.keys(): pd.DataFrame(logs[m]).to_csv(OUT[m]["csv"], index=False)

    print("\n" + "="*70)
    print(f"{'Metric':<20} | {'Base Model':<12} | {'Adapter Bare':<12} | {'Adapter Healed':<12}")
    print("-" * 70)
    for metric, key in [("Exact Match", "em"), ("Execution Acc", "ex")]:
        print(f"{metric:<20} | {(stats['base'][key]/len(eval_data))*100:>10.2f}% | {(stats['adapter_bare'][key]/len(eval_data))*100:>10.2f}% | {(stats['adapter_heal'][key]/len(eval_data))*100:>10.2f}%")
    
    print("-" * 70)
    print(f"{'Avg Gen Latency':<20} | {sum(stats['base']['gen_lat'])/len(eval_data):>10.2f}s | {sum(stats['adapter_bare']['gen_lat'])/len(eval_data):>10.2f}s | {sum(stats['adapter_heal']['gen_lat'])/len(eval_data):>10.2f}s")
    print(f"{'Avg Exe Latency':<20} | {sum(stats['base']['exe_lat'])/len(eval_data):>10.2f}s | {sum(stats['adapter_bare']['exe_lat'])/len(eval_data):>10.2f}s | {sum(stats['adapter_heal']['exe_lat'])/len(eval_data):>10.2f}s")
    print("="*70)

if __name__ == "__main__":
    evaluate()