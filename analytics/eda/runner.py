"""
CLI Execution Entry Point for Exploratory Data Analysis & Descriptive Statistics.

Executes full Phase 4 analytical pipeline:
- Loads clean job postings dataset from data/processed/
- Performs macro overview calculations, job title/company/location/remote/experience breakdowns
- Computes numerical/categorical descriptive statistics, IQR/Z-score outlier detection, and correlations
- Exports machine-readable CSV/JSON statistics to analytics_outputs/statistics/ and summaries/
- Generates high-resolution PNG charts in analytics_outputs/charts/
- Generates academic EDA report with rule-based insights in analytics_outputs/reports/eda_report.md

Executable via: `python -m analytics.eda.runner`
"""

import json
import logging
import sys
from pathlib import Path
import pandas as pd

from analytics.eda.overview import get_dataset_overview
from analytics.eda.jobs import analyze_job_distributions, analyze_job_titles
from analytics.eda.company import analyze_companies
from analytics.eda.location import analyze_locations
from analytics.eda.salary import analyze_salaries
from analytics.eda.experience import analyze_experience
from analytics.statistics.descriptive import calculate_numerical_stats, calculate_categorical_stats
from analytics.visualization.charts import generate_all_eda_charts

logger = logging.getLogger(__name__)


def locate_processed_dataset(processed_dir: Path, raw_dir: Path) -> Path:
    """
    Locate processed clean dataset or run cleaning pipeline if raw dataset exists.
    """
    clean_csv = processed_dir / "clean_job_postings.csv"
    if clean_csv.exists():
        return clean_csv

    # Check any csv in processed_dir
    proc_csvs = list(processed_dir.glob("*.csv"))
    if proc_csvs:
        return proc_csvs[0]

    # Check if raw dataset exists to trigger cleaning
    raw_csvs = list(raw_dir.glob("*.csv")) if raw_dir.exists() else []
    if raw_csvs:
        print("[+] Processed dataset not found. Running Phase 3 Data Cleaning pipeline...")
        from analytics.cleaning.run_pipeline import run_pipeline
        res = run_pipeline()
        if res == 0 and clean_csv.exists():
            return clean_csv

    return None


def generate_structured_insights(
    overview: dict,
    jobs_summary: dict,
    top_titles_df: pd.DataFrame,
    salary_summary: dict,
    remote_summary: dict
) -> list:
    """
    Rule-based analytical insight generator adhering to Observation, Evidence, Interpretation, Limitation format.
    """
    insights = []
    total = overview.get("total_job_postings", 0)
    if total == 0:
        return insights

    # Insight 1: Most Common Job Title
    if not top_titles_df.empty:
        top_title = top_titles_df.iloc[0]["job_title"]
        top_title_count = top_titles_df.iloc[0]["count"]
        top_title_pct = top_titles_df.iloc[0]["percentage"]
        insights.append({
            "topic": "Dominant Job Position",
            "finding": f"The job title '{top_title}' represents the single largest title category in the dataset.",
            "evidence": f"{top_title_count} out of {total} job postings ({top_title_pct}%) belong to this role.",
            "interpretation": f"High posting concentration in '{top_title}' reflects strong operational hiring demand for this functional specialization.",
            "limitation": "Reflects the specific dataset distribution and should not be assumed as universal market demand across all industries."
        })

    # Insight 2: Work Modality (Remote Ratio)
    remote_pct = overview.get("remote_job_percentage", 0.0)
    insights.append({
        "topic": "Work Modality Prevalence",
        "finding": f"Remote work opportunities represent {remote_pct}% of total analyzed job postings.",
        "evidence": f"Calculated dynamically from {total} posting records.",
        "interpretation": "Provides empirical baseline on post-pandemic remote/hybrid adoption in this market segment.",
        "limitation": "Work modality tags depend on employer posting transparency; unspecified modalities default to Onsite/Unknown."
    })

    # Insight 3: Salary Information Transparency
    sal_pct = overview.get("salary_completeness_pct", 0.0)
    sal_stats = salary_summary.get("overall_statistics", {})
    med_sal = sal_stats.get("median")
    insights.append({
        "topic": "Compensation Transparency & Median Pay",
        "finding": f"Salary information is disclosed in {sal_pct}% of job postings, with a median midpoint of {med_sal} INR/annual equivalent.",
        "evidence": f"{salary_summary.get('total_salary_records', 0)} out of {total} postings provide parseable salary bounds.",
        "interpretation": "Employers disclosing compensation ranges allow baseline median pay benchmarking across experience levels.",
        "limitation": "Optional salary disclosures may suffer from self-selection bias where higher or lower paying roles omit salary details."
    })

    return insights


def generate_markdown_report(
    overview: dict,
    job_dist: dict,
    top_titles_df: pd.DataFrame,
    company_summary: dict,
    location_summary: dict,
    salary_summary: dict,
    experience_summary: dict,
    insights: list,
    output_path: Path
):
    """
    Generate automated markdown report for MSc project portfolio.
    """
    lines = []
    lines.append("# Exploratory Data Analysis & Descriptive Statistics Report")
    lines.append("")
    lines.append("> **Project**: Job Market Analytics & Skill Demand Analysis Platform")
    lines.append("> **Scope**: Descriptive & Exploratory Data Analysis (Non-predictive)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 1: Dataset Overview
    lines.append("## 1. Dataset Overview")
    lines.append("")
    lines.append(f"- **Total Job Postings**: `{overview.get('total_job_postings', 0):,}`")
    lines.append(f"- **Unique Hiring Companies**: `{overview.get('unique_companies', 0):,}`")
    lines.append(f"- **Unique Geographic Locations**: `{overview.get('unique_locations', 0):,}`")
    lines.append(f"- **Unique Job Titles**: `{overview.get('unique_job_titles', 0):,}`")
    lines.append(f"- **Unique Extracted Skills**: `{overview.get('unique_skills', 0):,}`")
    d_range = overview.get("date_range", {})
    lines.append(f"- **Posting Date Range**: `{d_range.get('min_date')} to {d_range.get('max_date')}`")
    lines.append(f"- **Remote Work Ratio**: `{overview.get('remote_job_percentage', 0.0)}%`")
    lines.append(f"- **Salary Disclosure Rate**: `{overview.get('salary_completeness_pct', 0.0)}%`")
    lines.append(f"- **Experience Disclosure Rate**: `{overview.get('experience_completeness_pct', 0.0)}%`")
    lines.append("")

    # Section 2: Top Job Titles
    lines.append("## 2. Top Advertised Job Titles")
    lines.append("")
    if not top_titles_df.empty:
        lines.append("| Rank | Job Title | Count | Percentage |")
        lines.append("|---|---|---|---|")
        for idx, r in top_titles_df.head(10).iterrows():
            lines.append(f"| {idx + 1} | {r['job_title']} | {r['count']} | {r['percentage']}% |")
    else:
        lines.append("*No title data available.*")
    lines.append("")

    # Section 3: Salary Descriptive Statistics
    lines.append("## 3. Salary & Compensation Analysis")
    lines.append("")
    sal_stats = salary_summary.get("overall_statistics", {})
    lines.append("### Overall Salary Metrics")
    lines.append(f"- **Valid Salary Records**: `{salary_summary.get('total_salary_records', 0):,}`")
    lines.append(f"- **Mean Salary**: `{sal_stats.get('mean')}`")
    lines.append(f"- **Median Salary**: `{sal_stats.get('median')}`")
    lines.append(f"- **Standard Deviation**: `{sal_stats.get('std')}`")
    lines.append(f"- **Min / Max**: `{sal_stats.get('min')} / {sal_stats.get('max')}`")
    lines.append(f"- **IQR (Q1 to Q3)**: `{sal_stats.get('q1')} to {sal_stats.get('q3')} (IQR={sal_stats.get('iqr')})`")
    lines.append("")

    # Outliers
    iqr_out = salary_summary.get("outlier_analysis_iqr", {})
    lines.append("### Salary Outlier Analysis (IQR Method)")
    lines.append(f"- **Lower Bound**: `{iqr_out.get('lower_bound')}` | **Upper Bound**: `{iqr_out.get('upper_bound')}`")
    lines.append(f"- **Outlier Count**: `{iqr_out.get('outlier_count')} ({iqr_out.get('outlier_percentage')}%)`")
    lines.append("")

    # Section 4: Experience Level Breakdown
    lines.append("## 4. Experience Level Breakdown")
    lines.append("")
    exp_levels = experience_summary.get("level_distribution", {})
    if exp_levels:
        lines.append("| Experience Level | Count | Percentage |")
        lines.append("|---|---|---|")
        for k, v in exp_levels.items():
            lines.append(f"| {k} | {v['count']} | {v['percentage']}% |")
    lines.append("")

    # Section 5: Academic Rule-Based Insights
    lines.append("## 5. Dataset-Derived Insights")
    lines.append("")
    for ins in insights:
        lines.append(f"### {ins['topic']}")
        lines.append(f"- **Observation**: {ins['finding']}")
        lines.append(f"- **Supporting Evidence**: {ins['evidence']}")
        lines.append(f"- **Interpretation**: {ins['interpretation']}")
        lines.append(f"- **Limitation**: {ins['limitation']}")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run_eda_pipeline():
    """Execute complete Phase 4 EDA and descriptive statistics pipeline."""
    project_root = Path(__file__).resolve().parents[2]
    processed_dir = project_root / "data" / "processed"
    raw_dir = project_root / "data" / "raw"
    outputs_dir = project_root / "analytics_outputs"

    stats_dir = outputs_dir / "statistics"
    summaries_dir = outputs_dir / "summaries"
    charts_dir = outputs_dir / "charts"
    reports_dir = outputs_dir / "reports"

    for d in (stats_dir, summaries_dir, charts_dir, reports_dir):
        d.mkdir(parents=True, exist_ok=True)

    dataset_path = locate_processed_dataset(processed_dir, raw_dir)

    if dataset_path is None or not dataset_path.exists():
        print("\n" + "=" * 70)
        print(" [!] PROCESSED DATASET NOT FOUND")
        print("=" * 70)
        print(" No clean processed dataset was found in:")
        print(f"   {processed_dir}")
        print("\n Per project rules, synthetic/fake data is NOT generated.")
        print("\n Please download the raw dataset to data/raw/ and run Phase 3 cleaning first:")
        print("   python -m analytics.cleaning.pipeline")
        print("=" * 70 + "\n")
        return 1

    print(f"\n[+] Loading processed dataset from: {dataset_path.name}")
    df = pd.read_csv(dataset_path)
    print(f"[+] Loaded {len(df)} records with {len(df.columns)} columns.")

    print("\n[+] Executing Dataset Overview & Macro Analytics...")
    overview = get_dataset_overview(df)

    print("[+] Analyzing Job Distributions & Titles...")
    job_dist = analyze_job_distributions(df)
    top_titles_df = analyze_job_titles(df, top_n=20)

    print("[+] Analyzing Employer Postings...")
    company_summary = analyze_companies(df, top_n=15)

    print("[+] Analyzing Geographic Distributions...")
    location_summary = analyze_locations(df, top_n=15)

    print("[+] Analyzing Salary Distributions & Outliers...")
    salary_summary = analyze_salaries(df)

    print("[+] Analyzing Experience Requirements...")
    experience_summary = analyze_experience(df)

    print("\n[+] Generating Machine-Readable Exports to analytics_outputs/...")

    # Export Top Titles CSV
    top_titles_df.to_csv(stats_dir / "top_job_titles.csv", index=False)

    # Export Salary Breakdown CSVs
    if isinstance(salary_summary.get("by_experience"), pd.DataFrame):
        salary_summary["by_experience"].to_csv(stats_dir / "salary_by_experience.csv", index=False)

    if isinstance(salary_summary.get("by_remote_type"), pd.DataFrame):
        salary_summary["by_remote_type"].to_csv(stats_dir / "salary_by_remote_type.csv", index=False)

    if isinstance(salary_summary.get("by_city"), pd.DataFrame):
        salary_summary["by_city"].to_csv(stats_dir / "salary_by_city.csv", index=False)

    # Export Macro EDA JSON Summary
    eda_summary_json = {
        "dataset_overview": overview,
        "job_distributions": job_dist,
        "company_summary": company_summary,
        "location_summary": location_summary,
        "salary_summary": {
            "total_salary_records": salary_summary.get("total_salary_records", 0),
            "target_column_used": salary_summary.get("target_column_used"),
            "overall_statistics": salary_summary.get("overall_statistics"),
            "outlier_analysis_iqr": salary_summary.get("outlier_analysis_iqr"),
            "outlier_analysis_zscore": salary_summary.get("outlier_analysis_zscore"),
        },
        "experience_summary": experience_summary,
    }
    with open(summaries_dir / "eda_summary.json", "w", encoding="utf-8") as f:
        json.dump(eda_summary_json, f, indent=2)

    print("[+] Generating Visualizations in analytics_outputs/charts/...")
    charts = generate_all_eda_charts(df, charts_dir)
    for c in charts:
        print(f"    - Chart saved: {c.name}")

    print("[+] Generating Rule-Based Insights & Academic Markdown Report...")
    insights = generate_structured_insights(overview, job_dist, top_titles_df, salary_summary, job_dist.get("by_remote_type", {}))
    report_path = reports_dir / "eda_report.md"
    generate_markdown_report(overview, job_dist, top_titles_df, company_summary, location_summary, salary_summary, experience_summary, insights, report_path)
    print(f"[+] Automated EDA report generated at: {report_path}")

    print("\n" + "=" * 70)
    print(" Phase 4 — EDA & Descriptive Statistics Pipeline Execution Complete")
    print("=" * 70)
    print(f" Total Postings Analyzed: {overview.get('total_job_postings'):,}")
    print(f" Remote Work Percentage:  {overview.get('remote_job_percentage')}%")
    print(f" Median Salary Midpoint:  {salary_summary.get('overall_statistics', {}).get('median')}")
    print(f" Report Saved To:         analytics_outputs/reports/eda_report.md")
    print("=" * 70 + "\n")

    return 0


def main():
    """Module entry point: python -m analytics.eda.runner"""
    sys.exit(run_eda_pipeline())


if __name__ == "__main__":
    main()
