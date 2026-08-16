"""
Experience requirement analysis module for Job Market Analytics.
"""

from typing import Any, Dict
import pandas as pd
from analytics.statistics.descriptive import calculate_numerical_stats, calculate_categorical_stats


def analyze_experience(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate experience distributions, numeric year statistics, and categorical breakdowns.
    """
    if df.empty:
        return {
            "level_distribution": {},
            "min_years_statistics": calculate_numerical_stats(pd.Series(dtype=float)),
            "max_years_statistics": calculate_numerical_stats(pd.Series(dtype=float)),
        }

    total = len(df)
    level_counts = {}
    if "experience_level" in df.columns:
        counts = df["experience_level"].value_counts()
        for k, v in counts.items():
            level_counts[str(k)] = {
                "count": int(v),
                "percentage": round(float(v) / total * 100.0, 2)
            }

    min_exp_stats = calculate_numerical_stats(df["experience_min_years"]) if "experience_min_years" in df.columns else calculate_numerical_stats(pd.Series(dtype=float))
    max_exp_stats = calculate_numerical_stats(df["experience_max_years"]) if "experience_max_years" in df.columns else calculate_numerical_stats(pd.Series(dtype=float))

    return {
        "level_distribution": level_counts,
        "min_years_statistics": min_exp_stats,
        "max_years_statistics": max_exp_stats,
    }
