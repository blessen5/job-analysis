# Job Market Analytics & Skill Demand Analysis

A comprehensive data analytics platform built to analyze real job-market postings, identifying in-demand technical skills, salary distributions, role relationships, remote work trends, and geographic patterns.

> **Project Note**: This project focuses strictly on descriptive, exploratory, and statistical analysis of job market data. It does **not** perform forecasting, predictive modeling, or machine learning predictions.

---

## Overview & Description

Understanding trends in the technical job market requires rigorous data analysis. This project ingests, normalizes, processes, and visualizes job posting data to provide data-driven insights into:

* **Skill Demand**: Identifying top technical and soft skills across job domains.
* **Skill Co-occurrence**: Discovering skill clusters and technology combinations frequently requested together.
* **Job Roles**: Categorizing job titles into standard analytical roles.
* **Salary Patterns**: Examining compensation distributions across roles, experience levels, and locations.
* **Geographic & Location Trends**: Analyzing regional concentration of job postings.
* **Experience Requirements**: Evaluating requested seniority and experience thresholds.
* **Remote vs. Onsite Trends**: Comparing remote, hybrid, and onsite job availability.

---

## Objectives

1. **Standardize & Normalize Data**: Build robust ingestion pipelines to cleanse and map heterogeneous raw job postings into a unified analytical schema.
2. **Exploratory Data Analysis (EDA)**: Uncover foundational distributions, missing data patterns, and key categorical metrics.
3. **Statistical Analysis**: Apply rigorous statistical methods (correlation analysis, parametric/non-parametric tests) to evaluate relationships between salary, experience, and remote work.
4. **Skill Extraction & Network Mapping**: Extract structured skill terms from unstructured text using NLP and map co-occurrence networks.
5. **Interactive Visualization**: Expose insights through a modern REST API (FastAPI) and interactive dashboard (React & TypeScript).

---

## Planned Technology Stack

* **Language**: Python 3.11+
* **Data Processing & Analytics**: Pandas, NumPy, SciPy
* **Visualization**: Matplotlib, Seaborn, Plotly
* **Natural Language Processing**: spaCy
* **Database**: PostgreSQL, SQLAlchemy
* **API Framework**: FastAPI, Uvicorn
* **Frontend Dashboard**: React, TypeScript, Vite
* **Testing & Quality**: pytest, HTTPX
* **Containerization & CI/CD**: Docker, Docker Compose, GitHub Actions

---

## Project Status

```text
Phase 1 — Repository Foundation: Complete
Phase 2 — Dataset & Data Pipeline: Complete
Phase 3 — Data Cleaning & Quality Analysis: Complete
Phase 4 — Exploratory Data Analysis & Descriptive Statistics: Complete (Current)
```

---

## Planned Project Roadmap

* **Phase 1** — Repository Foundation *(Completed)*
* **Phase 2** — Dataset & Data Pipeline *(Completed)*
* **Phase 3** — Data Cleaning & Quality Analysis *(Completed)*
* **Phase 4** — Exploratory Data Analysis & Descriptive Statistics *(Completed)*
* **Phase 5** — Statistical Analysis
* **Phase 6** — Skill Extraction & Skill Demand
* **Phase 7** — Skill Co-occurrence Analysis
* **Phase 8** — Job Role & Location Analytics
* **Phase 9** — Salary Analytics
* **Phase 10** — Backend API
* **Phase 11** — Interactive Dashboard
* **Phase 12** — Testing & Docker
* **Phase 13** — Documentation & Final Release

---

## Quick Start

### Backend Prerequisites
* Python 3.11+
* PostgreSQL (or Docker)

### Installation
```bash
# Clone the repository
git clone https://github.com/user/job-market-analytics.git
cd job-market-analytics

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Run health check server
uvicorn backend.app.main:app --reload
```

### Data Cleaning & Quality Pipeline
```bash
# Run raw dataset ingestion, column normalization, data cleaning, and quality report generation
python -m analytics.cleaning.pipeline
```

### Exploratory Data Analysis & Statistics Pipeline
```bash
# Run EDA, descriptive statistics, outlier analysis, visualization chart generation, and automated report
python -m analytics.eda.runner
```

### Running Tests
```bash
pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](file:///c:/Users/bless/OneDrive/Desktop/job%20analysis/job-market-analytics/LICENSE) file for details.
