"""
Dataset overview module for Job Market Analytics.

Calculates macro dataset metrics, posting counts, date ranges, completeness ratios,
and remote work proportions.
"""

from typing import Any, Dict
import pandas as pd


def get_dataset_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate dynamic macro dataset statistics.
    """
    total_postings = int(len(df))
    if total_postings == 0:
        return {
            "total_job_postings": 0,
            "unique_companies": 0,
            "unique_locations": 0,
            "unique_job_titles": 0,
            "unique_skills": 0,
            "date_range": {"min_date": "N/A", "max_date": "N/A"},
            "remote_job_percentage": 0.0,
            "salary_completeness_pct": 0.0,
            "experience_completeness_pct": 0.0,
        }

    # Unique counts
    unique_companies = int(df["company"].replace("Unknown", pd.NA).dropna().nunique()) if "company" in df.columns else 0
    unique_locations = int(df["location"].replace("Unknown", pd.NA).dropna().nunique()) if "location" in df.columns else 0
    unique_titles = int(df["job_title"].replace("Unknown", pd.NA).dropna().nunique()) if "job_title" in df.columns else 0

    # Skills count
    unique_skills = 0
    if "skills" in df.columns:
        all_skills = set()
        for sk_val in df["skills"].dropna():
            if isinstance(sk_val, list):
                all_skills.update([str(s).strip() for s in sk_val if str(s).strip()])
            elif isinstance(sk_val, str) and sk_val.strip():
                all_skills.update([s.strip() for s in sk_val.split(",") if s.strip()])
        unique_skills = len(all_skills)

    # Date range
    min_date, max_date = "N/A", "N/A"
    if "posted_date" in df.columns:
        valid_dates = pd.to_datetime(df["posted_date"], errors="coerce").dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().strftime("%Y-%m-%d")
            max_date = valid_dates.max().strftime("%Y-%m-%d")

    # Percentages
    remote_cnt = (df["remote_type"] == "Remote").sum() if "remote_type" in df.columns else 0
    remote_pct = round(remote_cnt / total_postings * 100.0, 2)

    has_sal = df["salary_min"].notna() if "salary_min" in df.columns else pd.Series([False] * total_postings)
    sal_pct = round(has_sal.sum() / total_postings * 100.0, 2)

    has_exp = (df["experience_level"] != "Unknown") if "experience_level" in df.columns else pd.Series([False] * total_postings)
    exp_pct = round(has_exp.sum() / total_postings * 100.0, 2)

    return {
        "total_job_postings": total_postings,
        "unique_companies": unique_companies,
        "unique_locations": unique_locations,
        "unique_job_titles": unique_titles,
        "unique_skills": unique_skills,
        "date_range": {"min_date": min_date, "max_date": max_date},
        "remote_job_percentage": remote_pct,
        "salary_completeness_pct": sal_pct,
        "experience_completeness_pct": exp_pct,
    }
