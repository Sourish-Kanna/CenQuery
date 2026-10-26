# 💎 CenQuery: Text-to-SQL for Indian Census Data

**CenQuery** is a domain-specific Natural Language to SQL (NL-to-SQL) system designed for Indian Census data. It uses a fine-tuned **Llama-3-SQLCoder-8B** model with **LoRA adapters** to generate SQL queries grounded in a structured census database.

The project covers the complete workflow, from dataset preparation and model fine-tuning to evaluation and a web-based application for querying census data using natural language.

## 🔗 Project Links

| Resource | Link |
| --- | --- |
| **GitHub Repository** | [Sourish-Kanna/CenQuery](https://github.com/Sourish-Kanna/CenQuery) |
| **IEEE Research Paper** | [CenQuery: A Domain-Specific Text-to-SQL Dataset and Baseline Analysis for Indian Census Data](https://ieeexplore.ieee.org/document/11706071) |
| **Hugging Face Model** | [Sourish-Kanna/CenQuery](https://huggingface.co/Sourish-Kanna/CenQuery) |
| **Hugging Face Dataset** | [CenQuery Dataset](https://huggingface.co/datasets/Sourish-Kanna/CenQuery) |
| **Project Demo** | [Watch the Demo Video](https://drive.google.com/file/d/16c4AwUkKUdbjDFtxAuA4cx7uH_hcqqO3/view?usp=drive_link) |

---

## 🏗️ System Architecture

CenQuery combines a domain-specific dataset, an adapted language model, a backend SQL execution layer, and a web frontend.

### Main Components

1. **Base Model:** `defog/llama-3-sqlcoder-8b`, used as the foundation for SQL generation.
2. **Fine-Tuning:** LoRA adaptation using 650 curated Indian Census natural-language-to-SQL training examples.
3. **Evaluation:** An evaluation workflow using a separate set of 350 questions, with supporting scripts, results, and logs maintained in the repository.
4. **LLM Engine:** Hosts the model inference functionality.
5. **Backend:** A Python/FastAPI service that coordinates requests and SQL processing.
6. **Frontend:** A Next.js and TypeScript web application for interacting with the system.

### Application Documentation

- [Applications Overview](Applications/README.md)
- [Backend Documentation](Applications/Backend/README.md)
- [Frontend Documentation](Applications/Frontend/README.md)
- [LLM Engine Documentation](Applications/LLM-Engine/README.md)

---

## 📂 Repository Structure

The following structure reflects the current `main` branch, with selected files and subdirectories shown for readability.

```text
CenQuery/
├── Applications/
│   ├── Backend/
│   │   ├── data/
│   │   ├── database_schema.json
│   │   ├── main.py
│   │   ├── sql_engine.py
│   │   ├── constants.py
│   │   ├── requirements.in
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   ├── Frontend/
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── about/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── login/
│   │   │   │   ├── query/
│   │   │   │   └── schema/
│   │   │   ├── components/
│   │   │   │   ├── auth/
│   │   │   │   ├── layout/
│   │   │   │   ├── query/
│   │   │   │   ├── theme/
│   │   │   │   └── ui/
│   │   │   └── lib/
│   │   ├── package.json
│   │   ├── env.example
│   │   └── README.md
│   │
│   └── LLM-Engine/
│       ├── main.py
│       ├── dockerfile
│       ├── requirements.txt
│       └── README.md
│
├── DB-Setup/
│   └── unified_outputs/
│
├── Dataset/
│   ├── all dataset/
│   ├── data/
│   ├── eval_data/
│   ├── logs/
│   └── training_data/
│
├── Diagrams/
│
├── Old-Research/
│   ├── datasets_normalized/
│   └── results/
│
├── Paper/
│
├── Pre-Process/
│   ├── input/
│   ├── scripts/
│   ├── unified_outputs/
│   ├── upload_unified_data.py
│   └── verify_data.py
│
├── Training/
│   ├── eval/
│   ├── lora_train_test.ipynb
│   ├── run_evaluation.py
│   ├── run_full_eval.py
│   ├── run_analyse.py
│   └── database_schema.json
│
├── Trial/
│   ├── training_data/
│   └── training_data_final/
│
├── env.example
├── pyproject.toml
├── requirements-dev.in
├── requirements-dev.txt
├── Refernce links.html
├── drive link.html
└── README.md
```

*This is a selected overview rather than an exhaustive listing of every file. For the complete structure, see the [repository on GitHub](https://github.com/Sourish-Kanna/CenQuery).*

---

## 📊 Dataset and Database Schema

CenQuery focuses on Indian Census data organized into normalized tables. The schema includes demographic, social, economic, and agricultural information.

The principal tables documented for the project include:

| Category | Tables |
| --- | --- |
| Demographics | `population_stats`, `regions`, `age_groups` |
| Religion | `religion_stats`, `religions` |
| Language | `language_stats`, `languages`, `language_stats` |
| Education and Employment | `education_stats`, `occupation_stats` |
| Healthcare | `healthcare_stats` |
| Agriculture and Geography | `crops`, `tru` |

The schema definition is available in [`Applications/Backend/database_schema.json`](Applications/Backend/database_schema.json), with related copies used by the training and frontend components.

The repository also contains dataset preparation, normalized CSV outputs, training records, evaluation datasets, and experiment logs.

---

## 🔄 Development and Evaluation Workflow

The project is organized into the following stages:

1. **Dataset Preparation** — Collect and organize natural-language questions and their corresponding SQL queries.
2. **Preprocessing** — Clean and normalize census data, with scripts and processed outputs maintained under `Pre-Process/`.
3. **Database Setup** — Prepare the data and supporting files used by the database.
4. **Model Fine-Tuning** — Adapt the base SQL-generation model using LoRA training.
5. **Evaluation** — Run evaluation scripts and analyze generated SQL using the project's evaluation datasets and results.
6. **Application Integration** — Connect the frontend, backend, and LLM engine to provide an interface for natural-language queries.
7. **Research and Documentation** — Document the methodology and findings in the project's research publication.

---

## 🚀 Running the Application

CenQuery has separate application components, each with its own documentation.

Before running the project, review:

- [Backend setup and usage](Applications/Backend/README.md)
- [Frontend setup and usage](Applications/Frontend/README.md)
- [LLM Engine setup and usage](Applications/LLM-Engine/README.md)

Configuration examples are provided in the root `env.example` and `Applications/Frontend/env.example` files. Follow the relevant component documentation for required environment variables, dependencies, and service configuration.

**Security note:** Use environment variables for credentials and other secrets. Do not commit real database passwords, API keys, or deployment credentials.

---

## 📄 Research Publication

CenQuery's research focuses on a domain-specific Text-to-SQL dataset and baseline analysis for Indian Census data.

**Published paper:** *CenQuery: A Domain-Specific Text-to-SQL Dataset and Baseline Analysis for Indian Census Data*

**Authors:** Sourish Kanna, Maharajan Konar, Nandini Shende, G U Gopikha, and Suvarna Chaure.

Read the paper on [IEEE Xplore](https://ieeexplore.ieee.org/document/11706071).

---

## 👥 Contributors

This project was developed collaboratively by students at **SIES Graduate School of Technology**.

| Contributor | Contributions |
| --- | --- |
| **Sourish Kanna** | System architecture, model fine-tuning, and backend orchestration |
| **G U Gopikha** | Healthcare and social dataset curation, SQL logic verification |
| **Nandini Shende** | Demographic and economic data engineering, research documentation |
| **Maharajan Konar** | Frontend development and UI/UX design |

**Project Guide:** Prof. Suvarna Chaure

---

## ⚙️ Design Considerations

- **Schema Awareness:** The database schema is maintained in a shared JSON definition for use by application components.
- **Domain Specialization:** The model is adapted for Indian Census questions rather than relying exclusively on generic SQL-generation behavior.
- **Component Separation:** The frontend, backend, and LLM engine are maintained as distinct application components.
- **Evaluation Artifacts:** Training and evaluation scripts, results, and logs are retained in the repository to support research and analysis.

---

## 📚 Additional Resources

- [GitHub Repository](https://github.com/Sourish-Kanna/CenQuery)
- [IEEE Research Paper](https://ieeexplore.ieee.org/document/11706071)
- [Hugging Face Model](https://huggingface.co/Sourish-Kanna/CenQuery)
- [Hugging Face Dataset](https://huggingface.co/datasets/Sourish-Kanna/CenQuery)
- [Project Demo Video](https://drive.google.com/file/d/16c4AwUkKUdbjDFtxAuA4cx7uH_hcqqO3/view?usp=drive_link)
