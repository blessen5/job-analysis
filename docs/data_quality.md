# Data Quality Methodology & Score Specification

This document details the transparent data quality evaluation methodology, validation rules, quality score formula, and report output specifications for the **Job Market Analytics & Skill Demand Analysis Platform**.

---

## 1. Overview & Objectives

In job market data analytics, raw job postings collected from web scraping or public repositories exhibit significant heterogeneity, missing values, inconsistent formats, HTML markup, and duplicate entries. To ensure analytical integrity, every dataset ingested undergoes standardized preprocessing and rigorous data quality assessment.

Key Objectives:
- **Reproducibility**: Standardized command-line execution (`python -m analytics.cleaning.pipeline`).
- **Transparency**: Fully documented quality metrics without black-box scoring or arbitrary adjustments.
- **Traceability**: All output metrics are calculated dynamically from the underlying dataset.
- **Non-Destructive Processing**: The raw dataset in `data/raw/` remains untouched. Processed datasets are stored in `data/processed/`, and quality reports in `data/quality/`.

---

## 2. Standardized Analytical Schema

Raw job posting columns are mapped into canonical analytical fields:

| Field Name | Description | Target Data Type | Allowed / Standardized Values |
|---|---|---|---|
| `job_id` | Unique posting identifier | String / UUID | Auto-generated if missing |
| `job_title` | Cleaned job position title | String | HTML stripped, normalized formatting |
| `seniority_level` | Seniority classification | Enum String | `Intern`, `Entry Level`, `Junior`, `Mid Level`, `Senior`, `Lead`, `Manager`, `Director`, `Executive`, `Unknown` |
| `company` | Hiring organization | String | `Unknown` if missing |
| `location` | Raw location string | String | Cleaned city, state, country |
| `city` | Extracted city name | String | `Unknown` if unparseable |
| `state` | Extracted state/province | String | `Unknown` if unparseable |
| `country` | Extracted country | String | Default `India` for target market |
| `remote_type` | Work modality | Enum String | `Remote`, `Hybrid`, `Onsite`, `Unknown` |
| `salary_min` | Lower annual salary bound | Float | Numeric annual equivalent |
| `salary_max` | Upper annual salary bound | Float | Numeric annual equivalent |
| `salary_currency` | Currency ISO code | String | `INR`, `USD`, `EUR`, `GBP` |
| `salary_period` | Compensation pay period | Enum String | `Annual`, `Monthly`, `Hourly`, `Unknown` |
| `salary_midpoint` | Derived salary midpoint | Float | `(salary_min + salary_max) / 2.0` |
| `experience_min_years` | Minimum experience in years | Float | Numeric years |
| `experience_max_years` | Maximum experience in years | Float | Numeric years |
| `experience_level` | Experience category | Enum String | `Entry Level`, `Junior`, `Mid Level`, `Senior`, `Lead`, `Unknown` |
| `employment_type` | Contract terms | Enum String | `Full-time`, `Part-time`, `Contract`, `Internship`, `Temporary`, `Unknown` |
| `description` | Raw body text | Text | Preserved original text |
| `description_clean` | Cleaned body text | Text | HTML stripped, entity unescaped |
| `posted_date` | Publication date | ISO Date | `YYYY-MM-DD` |
| `posted_year` | Publication year | Integer | `YYYY` |
| `posted_month` | Publication month | Integer | `1-12` |
| `posted_day` | Day of month | Integer | `1-31` |
| `skills` | Skill array / string | List / String | Deduplicated skill keywords |
| `validation_flags` | Data validation warnings | String | `VALID` or comma-separated warnings |

---

## 3. Data Validation & Logical Rules

The pipeline validates logical consistency across all records rather than silently dropping records with edge cases:

1. **Salary Logical Rule**:
   - $\text{salary\_min} \le \text{salary\_max}$ and $\text{salary\_min} > 0$.
   - Flagged as `INVALID_SALARY_RANGE` if $\text{salary\_min} > \text{salary\_max}$.

2. **Experience Logical Rule**:
   - $\text{experience\_min\_years} \le \text{experience\_max\_years}$ and $\text{experience\_min\_years} \ge 0$.
   - Flagged as `INVALID_EXPERIENCE_RANGE` if $\text{experience\_min} > \text{experience\_max}$.

3. **Date Format Validation**:
   - Validated against ISO dates (`YYYY-MM-DD`). Flagged as `INVALID_DATE_FORMAT` if unparseable.

4. **Missing Required Fields**:
   - Records with empty or missing `job_title` are dropped as invalid posting records.

---

## 4. Transparent Data Quality Score Formula

The **Data Quality Score** ($S_{\text{overall}}$) is a weighted score bounded between $0$ and $100$, evaluated across four distinct dimensions:

$$S_{\text{overall}} = 0.35 \cdot S_{\text{completeness}} + 0.25 \cdot S_{\text{validity}} + 0.20 \cdot S_{\text{uniqueness}} + 0.20 \cdot S_{\text{consistency}}$$

### Dimension Definitions & Calculations

1. **Completeness Score ($S_{\text{completeness}}$)** — Weight: **35%**:
   Measures the average non-null percentage across key analytical columns (`job_title`, `company`, `location`, `salary_min`, `experience_level`, `description_clean`, `skills_formatted`).
   $$S_{\text{completeness}} = \frac{1}{K} \sum_{k=1}^{K} \left( 100 - \frac{\text{Missing Count}_k}{N} \times 100 \right)$$

2. **Validity Score ($S_{\text{validity}}$)** — Weight: **25%**:
   Measures the percentage of records passing all logical rules (`validation_flags == "VALID"`).
   $$S_{\text{validity}} = \frac{N_{\text{valid}}}{N} \times 100$$

3. **Uniqueness Score ($S_{\text{uniqueness}}$)** — Weight: **20%**:
   Evaluates dataset deduplication quality (100% minus the proportion of exact and likely duplicate postings).
   $$S_{\text{uniqueness}} = \max\left(0, 100 - \frac{N_{\text{exact\_duplicates}} + N_{\text{likely\_duplicates}}}{N_{\text{initial}}} \times 100\right)$$

4. **Consistency Score ($S_{\text{consistency}}$)** — Weight: **20%**:
   Measures the proportion of records successfully mapped to standard non-`Unknown` categorical values across `seniority_level`, `remote_type`, `employment_type`, and `experience_level`.
   $$S_{\text{consistency}} = \frac{1}{C} \sum_{c=1}^{C} \left( \frac{N_{\text{mapped\_known}, c}}{N} \times 100 \right)$$

---

## 5. Output Directory & Artifact Structure

Running the pipeline exports artifacts to `data/quality/`:

```text
data/
├── raw/
│   └── original raw CSV dataset
├── processed/
│   └── clean_job_postings.csv
└── quality/
    ├── data_quality_report.json
    ├── data_quality_report.csv
    ├── cleaning_summary.json
    ├── missing_values.png
    └── quality_score.png
```
