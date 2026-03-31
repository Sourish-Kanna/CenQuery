import pandas as pd
import json

# Load the results
results_file = "eval/evaluation_results_adapter.csv"
df = pd.read_csv(results_file)

print("--- 📊 CENQUERY BENCHMARK SUMMARY ---")
total = len(df)
em_count = df['em'].sum()
ex_count = df['ex'].sum()

print(f"Total Questions:     {total}")
print(f"Exact Match (EM):    {em_count} ({(em_count/total)*100:.2f}%)")
print(f"Execution Acc (EX):  {ex_count} ({(ex_count/total)*100:.2f}%)")

# 1. The "Semantic Wins" (Logic is right, syntax is different)
semantic_wins = df[(df['em'] == False) & (df['ex'] == True)]
print(f"Semantic Wins:       {len(semantic_wins)}")

# 2. Identify the "Hallucination" Rate (Gen failed or syntax error)
# Assuming 'gen_sql' contains "ERROR" or "FAILED"
gen_fails = df[df['gen_sql'].str.contains("ERROR|FAILED", case=False, na=False)]
print(f"Generation Failures: {len(gen_fails)}")

# 3. Export Semantic Wins for your Report Appendix
if len(semantic_wins) > 0:
    semantic_wins[['question', 'gt_sql', 'gen_sql']].to_csv("eval/semantic_wins_analysis.csv", index=False)
    print("🚀 Exported 'semantic_wins_analysis.csv' for project documentation.")

# 4. Top 5 Failures to analyze
failures = df[df['ex'] == False].head(5)
print("\n--- 🔍 SAMPLE FAILURES FOR DEBUGGING ---")
for i, row in failures.iterrows():
    print(f"Q: {row['question']}")
    print(f"Expected: {row['gt_sql']}")
    print(f"Got:      {row['gen_sql']}\n")