# Job Data Storage & Standardization

This directory holds the raw and processed job market datasets used by the analytics pipeline.

## Directory Structure
```text
data/
├── raw/        # Ingested raw datasets (CSV, JSON, Parquet)
└── processed/  # Standardized, cleaned, and normalized datasets
```

---

## Standard Analytical Target Schema

All ingested job postings will be transformed and mapped into the standard schema documented below:

| Field Name | Expected Type | Description |
| :--- | :--- | :--- |
| `job_id` | String / UUID | Unique primary identifier for the job posting |
| `job_title` | String | Original job title as advertised |
| `company` | String | Hiring organization name |
| `location` | String | City, state, or regional location text |
| `country` | String | ISO country code or standardized country name |
| `remote_type` | Enum / String | Work model classification (`Remote`, `Hybrid`, `Onsite`) |
| `salary_min` | Float | Minimum reported annual salary |
| `salary_max` | Float | Maximum reported annual salary |
| `salary_currency` | String | ISO 4217 currency code (e.g., `USD`, `EUR`, `GBP`) |
| `experience` | Enum / String | Seniority classification (`Entry`, `Mid`, `Senior`, `Lead`, `Executive`) |
| `employment_type` | Enum / String | Contract type (`Full-time`, `Part-time`, `Contract`, `Internship`) |
| `description` | Text | Full unstructured job description body text |
| `posted_date` | Date / ISO8601 | Job posting date timestamp |
| `skills` | List[String] | Parsed or explicit array of required technical skills |

---

## Data Normalization Layer Note

Raw datasets collected from different job boards or APIs typically feature non-uniform column names, varying salary representations (hourly vs. annual), diverse date formats, and disparate remote work tags. 

A **normalization layer** (to be implemented in Phase 2 & Phase 3) will handle schema mapping, data type casting, missing value handling, and value standardization without mutating raw source files stored in `data/raw/`.
