"""
Company posting analysis module for Job Market Analytics.
"""

from typing import Any, Dict
import pandas as pd


def analyze_companies(df: pd.DataFrame, top_n: int = 15) -> Dict[str, Any]:
    """
    Calculate employer concentrations and top company posting statistics.
    """
    if df.empty or "company" not in df.columns:
        return {
            "total_unique_companies": 0,
            "top_companies": [],
            "mean_postings_per_company": 0.0,
            "median_postings_per_company": 0.0,
        }

    companies = df["company"].dropna().astype(str).str.strip()
    valid_companies = companies[~companies.isin(["", "nan", "None", "Unknown"])]

    if valid_companies.empty:
        return {
            "total_unique_companies": 0,
            "top_companies": [],
            "mean_postings_per_company": 0.0,
            "median_postings_per_company": 0.0,
        }

    counts = valid_companies.value_counts()
    unique_cnt = len(counts)

    top_df = counts.head(top_n).reset_index()
    top_df.columns = ["company", "count"]
    top_df["percentage"] = (top_df["count"] / len(df) * 100.0).round(2)

    return {
        "total_unique_companies": unique_cnt,
        "top_companies": top_df.to_dict(orient="records"),
        "mean_postings_per_company": round(float(counts.mean()), 2),
        "median_postings_per_company": round(float(counts.median()), 2),
    }
