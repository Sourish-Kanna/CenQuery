# 📘 CenSQL – Text-to-SQL for Indian Census Data

This project implements a **Text-to-SQL system** for querying **Indian Census Data** using **LLaMA-3-SQLCoder + LoRA** with a **FastAPI backend**, **Supabase PostgreSQL database**, and **Next.js frontend**.

## 🚀 Workflow

1. **Data** → Collect, clean, save to Supabase.
2. **Backend** → FastAPI pipeline (rule-based + model).
3. **Frontend** → Next.js app calling backend API.
4. **Integration** → End-to-end demo (NL → SQL → Census DB → Result).
5. **Evaluation** → Log metrics (Exact Match, Execution Accuracy, Latency).
