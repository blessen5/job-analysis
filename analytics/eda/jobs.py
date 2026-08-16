"""
Job posting and title analysis module for Job Market Analytics.

Calculates distributions by job title, seniority, employment contract type,
work modality, and publication date breakdowns.
"""

from typing import Any, Dict
import pandas as pd


def analyze_job_distributions(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate job posting distributions across major categorical dimensions.
    """
    total = len(df)
    if total == 0:
        return {
            "by_employment_type": {},
            "by_remote_type": {},
            "by_seniority": {},
            "by_posted_year": {},
        }

    def _get_counts_pct(col_name: str) -> Dict[str, Dict[str, Any]]:
        if col_name not in df.columns:
            return {}
        counts = df[col_name].value_counts()
        res = {}
        for k, v in counts.items():
            res[str(k)] = {
                "count": int(v),
                "percentage": round(float(v) / total * 100.0, 2)
            }
        return res

    return {
        "by_employment_type": _get_counts_pct("employment_type"),
        "by_remote_type": _get_counts_pct("remote_type"),
        "by_seniority": _get_counts_pct("seniority_level"),
        "by_posted_year": _get_counts_pct("posted_year"),
    }


def analyze_job_titles(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Generate frequency distribution DataFrame for top N job titles.
    """
    if df.empty or "job_title" not in df.columns:
        return pd.DataFrame(columns=["job_title", "count", "percentage"])

    titles = df["job_title"].dropna().astype(str).str.strip()
    titles = titles[titles != "Unknown"]

    if titles.empty:
        return pd.DataFrame(columns=["job_title", "count", "percentage"])

    counts = titles.value_counts().head(top_n).reset_index()
    counts.columns = ["job_title", "count"]
    counts["percentage"] = (counts["count"] / len(df) * 100.0).round(2)

    return counts
