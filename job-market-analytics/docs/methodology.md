# Analytical Methodology

This document details the analytical workflow, research methodology, and processing pipeline for the **Job Market Analytics & Skill Demand Analysis** project.

> **Scope Note**: The project performs descriptive and exploratory job-market analytics. It does **not** perform prediction or forecasting.

---

## Analytical Workflow Diagram

```text
Raw Job Data
     ↓
Data Validation
     ↓
Data Cleaning
     ↓
Data Normalization
     ↓
Exploratory Data Analysis
     ↓
Descriptive Statistics
     ↓
Skill Extraction
     ↓
Skill Demand Analysis
     ↓
Skill Co-occurrence Analysis
     ↓
Job Role Analysis
     ↓
Salary Analysis
     ↓
Location Analysis
     ↓
Visualization
     ↓
Insights
```

---

## Workflow Phase Descriptions

### 1. Raw Data Ingestion & Validation
* Load heterogeneous raw job posting data from structured and semi-structured files (CSV, JSON).
* Validate missing fields, structural schema integrity, and data types.

### 2. Data Cleaning & Normalization
* Standardize job titles, employment types, experience levels, and remote modality tags.
* Parse raw compensation ranges and convert hourly rates into standard annual currency figures.
* Clean raw job description text by removing HTML markup, unescaping characters, and stripping noise.

### 3. Exploratory Data Analysis (EDA)
* Compute baseline univariate metrics and continuous distributions.
* Inspect data completeness and missingness patterns across key dimensions.
* Tabulate categorical frequencies for hiring companies, roles, and regions.

### 4. Descriptive & Inferential Statistics
* Calculate measures of central tendency (mean, median) and dispersion (IQR, standard deviation).
* Apply statistical hypothesis testing to evaluate compensation differences across remote modalities and experience thresholds.

### 5. Skill Extraction & Term Normalization
* Use Natural Language Processing (spaCy) and pattern matching to extract technical skills, libraries, databases, and frameworks from job descriptions.
* Map raw extracted entities to a canonical skill taxonomy (e.g., `"PySpark"` -> `"Spark"`).

### 6. Skill Demand & Co-occurrence Analysis
* Measure skill prevalence and ranking across job domains.
* Construct skill co-occurrence matrices and adjacency graphs to identify technology stacks commonly requested together.

### 7. Role, Salary & Geographic Analytics
* Aggregate compensation patterns across standardized job categories, experience levels, and geographic regions.
* Evaluate remote vs. onsite job distribution and salary parity.

### 8. Visualization & Insights Synthesis
* Generate informative static and interactive visual charts (bar charts, box plots, co-occurrence heatmaps, network graphs).
* Synthesize empirical findings into actionable market summaries.
