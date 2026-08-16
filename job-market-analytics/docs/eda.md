# Exploratory Data Analysis (EDA) Specification

This document details the exploratory data analysis (EDA) methodology, analytical dimensions, visualization guidelines, and reporting standards for the **Job Market Analytics & Skill Demand Analysis Platform**.

---

## 1. Scope & Objective

As an **MSc Computer Science (Data Analytics)** project, this EDA phase focuses strictly on descriptive, exploratory, and non-predictive statistical investigation of processed job market postings.

### Included Analyses:
- **Macro Overview**: Total posting count, company concentration, geographic locations, remote work ratio, date coverage.
- **Job Title & Role Distributions**: Frequency counts, percentage proportions, top N job titles.
- **Employer Posting Concentrations**: Top hiring organizations, posting variance across companies.
- **Geographic & Regional Trends**: Top hiring cities, state/province breakdowns, work modality distributions per city.
- **Work Modality (Remote vs. Hybrid vs. Onsite)**: Categorical proportions, remote availability across seniority levels.
- **Experience Requirement Analysis**: Seniority levels, minimum/maximum required experience in years.
- **Salary & Compensation Analysis**: Parametric (mean, std) and non-parametric (median, IQR, Q1, Q3) pay distributions.
- **Outlier Analysis**: Interquartile Range (IQR) and Z-Score outlier detection without destructive data removal.

### Explicitly Excluded (Per Project Constraints):
- Salary forecasting or predictive modeling
- Machine learning job title classification
- Job recommendation systems
- Skill-demand predictive forecasting

---

## 2. Analytical Submodules & CLI Runner

The EDA framework is built as a modular package within `analytics/eda/`:

```text
analytics/
├── eda/
│   ├── overview.py       # Macro dataset overview & completeness ratios
│   ├── jobs.py           # Job title & role frequency distributions
│   ├── company.py        # Employer posting concentrations
│   ├── location.py       # City, state, country breakdowns
│   ├── salary.py         # Salary statistics & outlier detection
│   ├── experience.py     # Seniority & experience year metrics
│   └── runner.py         # CLI entry point: python -m analytics.eda.runner
│
├── statistics/
│   ├── descriptive.py    # Numerical & categorical statistical functions
│   └── distributions.py  # IQR, Z-score, Pearson correlation matrices
│
└── visualization/
    ├── charts.py         # Matplotlib/Seaborn analytical plot generators
    └── save.py           # Aesthetic styling & 300 DPI image export
```

### CLI Execution Command:
```bash
python -m analytics.eda.runner
```

---

## 3. Output Directory Structure

Running the EDA pipeline generates machine-readable data files, high-resolution PNG charts, and an automated Markdown report under `analytics_outputs/`:

```text
analytics_outputs/
├── statistics/
│   ├── top_job_titles.csv
│   ├── salary_by_experience.csv
│   ├── salary_by_remote_type.csv
│   └── salary_by_city.csv
│
├── summaries/
│   └── eda_summary.json
│
├── charts/
│   ├── remote_work_distribution.png
│   ├── employment_type_distribution.png
│   ├── top_job_titles.png
│   ├── top_companies.png
│   ├── top_locations.png
│   ├── experience_distribution.png
│   ├── salary_histogram.png
│   ├── salary_box_experience.png
│   └── correlation_heatmap.png
│
└── reports/
    └── eda_report.md
```

---

## 4. Academic Rule-Based Insight Framework

To ensure statistical rigor and prevent overclaiming, analytical insights follow a 4-part structured framework:

1. **Observation**: What the metric or chart directly demonstrates.
2. **Supporting Evidence**: Exact calculated numbers and sample size.
3. **Interpretation**: Logical analytical takeaway grounded in empirical data.
4. **Limitation**: Boundaries of dataset scope (e.g., sample representation, self-selection bias).
