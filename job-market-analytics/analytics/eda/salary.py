"""
Salary and compensation analytics module for Job Market Analytics.
"""

from typing import Any, Dict
import pandas as pd

from analytics.statistics.descriptive import calculate_numerical_stats, calculate_grouped_stats
from analytics.statistics.distributions import detect_outliers_iqr, detect_outliers_zscore


def analyze_salaries(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate comprehensive salary analytics, descriptive metrics, outlier summaries,
    and grouped salary statistics across role, experience, location, and work modality.
    """
    if df.empty or "salary_min" not in df.columns:
        return {
            "total_salary_records": 0,
            "overall_statistics": calculate_numerical_stats(pd.Series(dtype=float)),
            "outlier_analysis_iqr": detect_outliers_iqr(pd.Series(dtype=float)),
            "outlier_analysis_zscore": detect_outliers_zscore(pd.Series(dtype=float)),
            "by_experience": pd.DataFrame(),
            "by_remote_type": pd.DataFrame(),
            "by_seniority": pd.DataFrame(),
            "by_city": pd.DataFrame(),
        }

    # Focus on salary_midpoint or salary_min for continuous representation
    target_col = "salary_midpoint" if "salary_midpoint" in df.columns and df["salary_midpoint"].notna().any() else "salary_min"
    sal_series = pd.to_numeric(df[target_col], errors="coerce").dropna()

    overall_stats = calculate_numerical_stats(sal_series)
    iqr_outliers = detect_outliers_iqr(sal_series)
    zscore_outliers = detect_outliers_zscore(sal_series)

    # Grouped breakdowns
    by_exp = calculate_grouped_stats(df, "experience_level", target_col)
    by_remote = calculate_grouped_stats(df, "remote_type", target_col)
    by_seniority = calculate_grouped_stats(df, "seniority_level", target_col)
    by_city = calculate_grouped_stats(df, "city", target_col, min_group_size=2)

    return {
        "total_salary_records": len(sal_series),
        "target_column_used": target_col,
        "overall_statistics": overall_stats,
        "outlier_analysis_iqr": iqr_outliers,
        "outlier_analysis_zscore": zscore_outliers,
        "by_experience": by_exp,
        "by_remote_type": by_remote,
        "by_seniority": by_seniority,
        "by_city": by_city,
    }
