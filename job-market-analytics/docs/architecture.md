# System Architecture

This document describes the high-level system architecture and component interactions for the **Job Market Analytics** platform.

---

## Architectural Diagram

```text
                ┌─────────────────┐
                │   Job Dataset   │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │ Data Processing │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │ Analytics Layer │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │   PostgreSQL    │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │    FastAPI      │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │ React Dashboard │
                └─────────────────┘
```

---

## System Components

### 1. Job Dataset
* Raw input job posting data stored in `data/raw/` in CSV or JSON formats.

### 2. Data Processing Layer (`analytics/cleaning`)
* Performs validation, text sanitization, normalization, and canonical schema mapping.

### 3. Analytics Layer (`analytics/`)
* Executes EDA, descriptive statistics, NLP skill extraction, co-occurrence matrix generation, and salary breakdown calculations.

### 4. Database Layer (`PostgreSQL` & `backend/app/database.py`)
* Relational database storing processed job postings, extracted skills, skill co-occurrences, and pre-computed analytical metrics.

### 5. Backend REST API Layer (`FastAPI`)
* High-performance Python REST API exposing analytical query endpoints, health checks, and data payloads.

### 6. Frontend Dashboard Layer (`React` + `TypeScript`)
* Interactive client web application providing data visualizations, dynamic filters, and analytical dashboards.
