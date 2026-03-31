# 💎 CenQuery: Specialized Text-to-SQL for Indian Census Data

**CenQuery** is a high-accuracy Natural Language to SQL (NL-to-SQL) system specifically architected for Indian Census datasets. By moving away from generic LLMs, this project utilizes a fine-tuned **Llama-3-SQLCoder-8b** model with **LoRA adapters** to ensure schema-safe query generation and 100% execution accuracy on domain-specific queries.

**[Project Demo Video](https://drive.google.com/file/d/16c4AwUkKUdbjDFtxAuA4cx7uH_hcqqO3/view?usp=drive_link)**

---

## 🏗️ System Architecture

To solve the "hallucination" and "privacy-performance paradox" found in baseline models, CenQuery employs a specialized production-ready pipeline:

1. **Base Model:** `defog/llama-3-sqlcoder-8b` (SOTA for SQL generation).
2. **Fine-Tuning:** LoRA (Low-Rank Adaptation) training on **650 hand-verified** Indian Census NL→SQL pairs.
3. **Evaluation:** Validated against an **unseen 350-question dataset** focusing on Execution Accuracy and Exact Match metrics.
4. **Deployment Stack:** - **Inference Engine:** Hosted on **DigitalOcean AI GPU Droplets** for low-latency, secure processing.
   - **Backend:** **FastAPI (Python)** deployed on **Render**, acting as the orchestration layer.
   - **Frontend:** **Next.js (TypeScript)** deployed on **Vercel**, providing an interactive administrative dashboard.

---

## 📂 Project Structure

The CenQuery repository is organized into distinct modules for data processing, model training, and application deployment.

```text
CenQuery-regorg/
├── Applications/             # Core Service Implementations
│   ├── Backend/              # FastAPI Server & SQL Engine logic
│   ├── Frontend/             # Next.js Web Dashboard
│   └── LLM-Engine/           # VLLM/Transformer Inference Scripts & Docker
├── Dataset/                  # Census-650 & Evaluation Gold Sets
│   ├── all dataset/          # Raw .sql and .txt source pairs
│   ├── data/                 # 12 Normalized Census CSV tables
│   ├── eval_data/            # Unseen test sets (.jsonl)
│   └── training_data/        # Fine-tuning ready records
├── Diagrams/                 # System, Sequence, and ER Diagrams 
│   ├── System arch new.png   # Current production architecture
│   └── ER Diagram.png        # Normalized Census Schema visual
├── Training/                 # Model Adaptation & Metrics
│   ├── lora_train_test.ipynb # LoRA/QLoRA training pipeline
│   ├── run_evaluation.py     # Automated metric calculation script
│   └── evaluation_results_adapter.csv # Final model performance logs
├── Pre-Process/              # Data Cleaning & Normalization Pipeline
│   ├── scripts/              # Individual table cleaning logic
│   └── unified_outputs/      # Final processed CSVs for DB ingestion
├── DB-Setup/                 # Database Ingestion & Security Scripts
└── README.md                 # Project Overview & Documentation
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

## 👥 Contributors

This project is a collaborative effort by the following team members at **SIES Graduate School of Technology**:

| Contributor | Core Responsibilities |
| :--- | :--- |
| **Sourish Kanna** | System Architecture, QLoRA Fine-tuning, Backend Orchestration |
| **G U Gopikha** | Healthcare & Social Dataset Curation, SQL Logic Verification |
| **Nandini Shende** | Demographic & Economic Data Engineering, IEEE Documentation |
| **Maharajan Konar** | Frontend Development (Next.js), UI/UX Design, Vercel Deployment |

**Guided by:** Prof. Suvarna Chaure

---

## ⚙️ Coding Conventions

* **Schema-Awareness:** All SQL generation is constrained by `database_schema.json` to eliminate column/table hallucinations.
* **Security:** Read-only database access with strict transaction timeouts to ensure data sovereignty.
* **Documentation:** All technical decisions and metrics are mirrored in the **Implementation Paper** and **Black Book**.
