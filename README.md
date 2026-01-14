# 📘 CenQuery: Specialized Text-to-SQL for Indian Census Data

**CenQuery** is a high-accuracy Natural Language to SQL (NL-to-SQL) system specifically architected for Indian Census datasets. By moving away from generic LLMs, this project utilizes a fine-tuned **Llama-3-SQLCoder-8b** model with **QLoRA adapters** to ensure schema-safe query generation and 100% execution accuracy.

---

## 🏗️ System Architecture: The "Soft Reboot"

To solve the "hallucination" problem found in baseline models, CenQuery employs a specialized pipeline:

1. **Base Model:** `defog/llama-3-sqlcoder-8b` (SOTA for SQL generation).
2. **Fine-Tuning:** 4-bit QLoRA (NF4) training on **650+ hand-verified** Indian Census question-SQL pairs.
3. **Deployment:** * **Training:** Google Colab (A100/L4).

* **Inference:** Hugging Face Inference Endpoints (Microservice).
* **Backend:** FastAPI (Python) serving as the bridge.
* **Frontend:** Next.js (TypeScript) for the interactive dashboard.

---

## 📂 Project Structure

```text
CenQuery-main/
├── Backend/                # FastAPI Server & Model Clients
│   ├── main.py             # API Routes (/api/query)
│   ├── model_client.py     # Hugging Face Endpoint integration
│   └── setup_database.py   # Supabase/PostgreSQL connection logic
├── Dataset/                # The "Golden" Dataset (650 Questions)
│   ├── training_data/      # Merged .jsonl files for LoRA training
│   ├── data/               # 12 Normalized CSV Tables (Religion, Crop, etc.)
│   └── database_schema.json# Verified Master Schema
├── Frontend/               # Next.js Application
│   ├── src/app/            # Query interface and result visualization
│   └── public/             # Static assets
├── Training/               # Fine-tuning scripts
│   └── train_lora.py       # QLoRA training script for Colab
├── Research/               # Academic Documentation
│   └── Comparative_Analysis.pdf # The Jan 12 Research Paper
└── README.md

```

---

## 📊 Dataset & Schema

The model is trained on **12 normalized tables** covering the depth of Indian Census data:

* **Demographics:** `population_stats`, `regions`
* **Social:** `religion_stats`, `language_stats`
* **Economic:** `education_stats`, `occupation_stats`, `healthcare_stats`
* **Agriculture:** `crop_stats`

**Current Status:** ✅ 650 Verified training pairs complete.

---

## 👥 Team & Responsibilities

* **Sourish (Lead):** Model Architecture, QLoRA Fine-tuning, and Backend Integration.
* **Nandhini & Gopikha:** Data Engineering, SQL Verification, and IEEE Documentation.
* **Maharajan:** Frontend Development (Next.js) and UI/UX Deployment.

---

## 🚀 Development Workflow

1. **Data Engineering:** Consolidate 650 questions into a schema-aware `.jsonl` format.
2. **Model Training:** Execute QLoRA training on Colab and push adapters to Hugging Face.
3. **Integration:** Connect FastAPI to the HF inference microservice.
4. **Evaluation:** Conduct Comparative Analysis (GPT-3.5 vs. CenQuery) for the research paper.
5. **Review:** Demonstrate end-to-end "Natural Language → SQL → Census Result" on Jan 17.

---

## ⚙️ Coding Conventions

* **Model-First:** All SQL must be generated based on the `database_schema.json` to prevent column hallucinations.
* **Clean Code:** Use OOP in the backend; TypeScript for type-safety in the frontend.
* **Documentation:** All project updates must be mirrored in the IEEE Status Report.
