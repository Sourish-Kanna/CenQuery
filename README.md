# 💎 CenQuery: Specialized Text-to-SQL for Indian Census Data

**CenQuery** is a high-accuracy Natural Language to SQL (NL-to-SQL) system specifically architected for Indian Census datasets. By moving away from generic LLMs, this project utilizes a fine-tuned **Llama-3-SQLCoder-8b** model with **LoRA adapters** to ensure schema-safe query generation and 100% execution accuracy on domain-specific queries.

**[Project Demo Video](https://drive.google.com/file/d/16c4AwUkKUdbjDFtxAuA4cx7uH_hcqqO3/view?usp=drive_link)**

---

## 🏗️ System Architecture: The "Soft Reboot"

To solve the "hallucination" and "privacy-performance paradox" found in baseline models, CenQuery employs a specialized production-ready pipeline:

1. **Base Model:** `defog/llama-3-sqlcoder-8b` (SOTA for SQL generation).
2. **Fine-Tuning:** LoRA (Low-Rank Adaptation) training on **650 hand-verified** Indian Census NL→SQL pairs.
3. **Evaluation:** Validated against an **unseen 350-question dataset** focusing on Execution Accuracy and Exact Match metrics.
4. **Deployment Stack:** - **Inference Engine:** Hosted on **DigitalOcean AI GPU Droplets** for low-latency, secure processing.
   - **Backend:** **FastAPI (Python)** deployed on **Render**, acting as the orchestration layer.
   - **Frontend:** **Next.js (TypeScript)** deployed on **Vercel**, providing an interactive administrative dashboard.

---

## 📂 Project Structure

```text
CenQuery-main/
├── Backend/                # FastAPI Server & Business Logic (Deployed on Render)
│   ├── main.py             # API Routes (/api/query)
│   └── database_schema.json# Verified Master Schema for Prompt Construction
├── LLM-Engine/             # Inference logic (Deployed on DigitalOcean)
│   ├── main.py             # vLLM/Transformers Inference Server
│   └── dockerfile          # Containerization for GPU deployment
├── Dataset/                # The "Census-650" & Evaluation Sets
│   ├── training_data/      # train_final_(650).jsonl for LoRA training
│   ├── data/               # 12 Normalized CSV Tables (Religion, Crop, etc.)
│   └── eval_data/          # 350 Unseen questions for final validation
├── Frontend/               # Next.js Application (Deployed on Vercel)
│   ├── src/app/            # Query interface and result visualization
│   └── tailwind.config.ts  # UI Styling
├── Training/               # Fine-tuning & Evaluation Scripts
│   ├── lora_train_test.ipynb # QLoRA training workflow
│   └── run_evaluation.ipynb  # Metric calculation (Accuracy/Error Analysis)
├── Old-Research/           # Baseline Comparative Study
│   └── summary_metrics.csv # Historical results (GPT vs Llama baselines)
└── README.md
```

---

## 📊 Dataset & Schema

The model is trained to navigate **12 normalized tables** covering the depth of Indian Census data. This normalization prevents the "Complexity Limit" errors seen in generic models:

* **Demographics:** `population_stats`, `regions`, `age_groups`
* **Social:** `religion_stats`, `language_stats`, `religions`, `languages`
* **Economic:** `education_stats`, `occupation_stats`, `healthcare_stats`
* **Agriculture:** `crops`, `tru` (Total/Rural/Urban)

**Current Status:** ✅ Adapter training completed. ✅ Comparative paper completed. 🔄 Final Implementation Paper in progress.

---

## 🚀 Development & Validation Workflow

1. **Data Engineering:** Consolidated 650 questions into schema-aware `.jsonl` format with execution-validated SQL ground truths.
2. **Model Training:** Executed LoRA adaptation to bridge the 17% performance gap identified in the baseline research.
3. **Deployment:** Established a decoupled architecture using DigitalOcean (Inference), Render (Backend), and Vercel (Frontend).
4. **Evaluation:** Analyzing results from the 350-question unseen dataset to categorize remaining errors (Syntax, Join logic, or Aggregation).

---

## ⚙️ Coding Conventions

* **Schema-Awareness:** All SQL generation is constrained by `database_schema.json` to eliminate column/table hallucinations.
* **Security:** Read-only database access with strict transaction timeouts to ensure data sovereignty.
* **Documentation:** All technical decisions and metrics are mirrored in the **Implementation Paper** and **Black Book**.
