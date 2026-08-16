# Analytical Methodology

This document details the analytical workflow, research methodology, and processing pipeline for the **Job Market Analytics & Skill Demand Analysis** project.

> **Scope Note**: The project performs descriptive and exploratory job-market analytics. It does **not** perform prediction or forecasting.

---

## Analytical Workflow Diagram

```text
Raw Job Data
     ↓
Column Normalization & Mapping
     ↓
Data Cleaning & HTML Sanitization
     ↓
Salary & Experience Parsing
     ↓
Validation & Logical Rules Check
     ↓
Data Quality Scoring & Reports (data/quality/)
     ↓
Exploratory Data Analysis
     ↓
Descriptive Statistics
     ↓
Skill Extraction & Taxonomy Mapping
     ↓
Skill Co-occurrence & Stack Analysis
     ↓
Role, Salary & Geographic Analysis
     ↓
Interactive Dashboard & Insights
```

---

## Workflow Phase Descriptions

### 1. Raw Data Ingestion & Validation
* Load heterogeneous raw job posting data from `data/raw/`.
* Dynamically detect column variations (`jobDescription`, `salaryRange`, `workMode`, `experienceLevel`, `keySkills`) and map to standard schema.

### 2. Data Cleaning & Quality Analysis (Phase 3 Completed)
* **Seniority & Title Normalization**: Separate clean job titles from standard seniority levels (`Intern`, `Entry Level`, `Junior`, `Mid Level`, `Senior`, `Lead`, `Manager`, `Director`, `Executive`, `Unknown`).
* **Experience Parsing**: Extract numeric `experience_min_years`, `experience_max_years`, and standardized `experience_level`.
* **Salary Parsing**: Extract `salary_min`, `salary_max`, `salary_currency`, `salary_period`, and derived `salary_midpoint` while preserving original compensation strings.
* **Location & Work Mode**: Extract `city`, `state`, `country` and categorize work modality (`Remote`, `Hybrid`, `Onsite`, `Unknown`).
* **Text Sanitization**: HTML tag stripping, entity unescaping, and whitespace normalization to produce `description_clean`.
* **Logical Rule Validation**: Flag records with invalid salary ranges (`salary_min > salary_max`), invalid experience ranges, or invalid date formats.
* **Transparent Data Quality Scoring**: Compute weighted Data Quality Score (Completeness, Validity, Uniqueness, Consistency) and export quality reports/charts to `data/quality/`.

### 3. Exploratory Data Analysis & Descriptive Statistics (Phase 4 Completed)
* **Macro Overview**: Dynamic calculation of posting counts, company concentration, location coverage, date ranges, and remote work percentages.
* **Parametric & Non-Parametric Metrics**: Compute mean, std, variance alongside robust median, Q1, Q3, and IQR metrics.
* **Outlier Detection**: Apply Interquartile Range (IQR) and Z-Score outlier algorithms without destructive record removal.
* **Visual Analytics & Reporting**: Generate publication-ready PNG charts and automated Markdown reports with structured rule-based insights (`Observation`, `Supporting Evidence`, `Interpretation`, `Limitation`).

### 5. Skill Extraction & Term Normalization
* Use Natural Language Processing (spaCy) and pattern matching to extract technical skills, libraries, databases, and frameworks from job descriptions.

### 6. Skill Demand & Co-occurrence Analysis
* Measure skill prevalence and ranking across job domains.
* Construct skill co-occurrence matrices to identify technology stacks commonly requested together.

### 7. Role, Salary & Geographic Analytics
* Aggregate compensation patterns across standardized job categories, experience levels, and geographic regions.

### 8. Visualization & Insights Synthesis
* Generate static and interactive charts (bar charts, box plots, co-occurrence heatmaps, network graphs).
* Synthesize empirical findings into dataset-derived market insights.
