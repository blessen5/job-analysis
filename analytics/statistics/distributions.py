"""
Distribution and outlier analysis module for Job Market Analytics.

Implements Interquartile Range (IQR) and Z-Score outlier detection methodologies
and Pearson/Spearman correlation matrix calculations.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


def detect_outliers_iqr(series: pd.Series, factor: float = 1.5) -> Dict[str, Any]:
    """
    Detect numerical outliers using the Interquartile Range (IQR) method.

    Rule:
        Lower Bound = Q1 - (factor * IQR)
        Upper Bound = Q3 + (factor * IQR)
    """
    clean_series = pd.to_numeric(series, errors="coerce").dropna()
    total_valid = len(clean_series)

    if total_valid == 0:
        return {
            "method": "IQR",
            "factor": factor,
            "total_records": 0,
            "q1": None,
            "q3": None,
            "iqr": None,
            "lower_bound": None,
            "upper_bound": None,
            "outlier_count": 0,
            "outlier_percentage": 0.0,
            "low_outlier_count": 0,
            "high_outlier_count": 0,
        }

    q1 = float(clean_series.quantile(0.25))
    q3 = float(clean_series.quantile(0.75))
    iqr = q3 - q1

    lower_bound = q1 - (factor * iqr)
    upper_bound = q3 + (factor * iqr)

    low_mask = clean_series < lower_bound
    high_mask = clean_series > upper_bound
    outlier_mask = low_mask | high_mask

    outlier_count = int(outlier_mask.sum())
    outlier_pct = round((outlier_count / total_valid * 100.0) if total_valid > 0 else 0.0, 2)

    return {
        "method": "IQR",
        "factor": factor,
        "total_records": total_valid,
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "iqr": round(iqr, 4),
        "lower_bound": round(lower_bound, 4),
        "upper_bound": round(upper_bound, 4),
        "outlier_count": outlier_count,
        "outlier_percentage": outlier_pct,
        "low_outlier_count": int(low_mask.sum()),
        "high_outlier_count": int(high_mask.sum()),
    }


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> Dict[str, Any]:
    """
    Detect numerical outliers using the Z-Score method.

    Rule:
        Z = (X - mean) / std
        Outliers: |Z| > threshold
    """
    clean_series = pd.to_numeric(series, errors="coerce").dropna()
    total_valid = len(clean_series)

    if total_valid < 2:
        return {
            "method": "Z-Score",
            "threshold": threshold,
            "total_records": total_valid,
            "mean": None,
            "std": None,
            "outlier_count": 0,
            "outlier_percentage": 0.0,
        }

    mean_val = float(clean_series.mean())
    std_val = float(clean_series.std())

    if std_val == 0:
        return {
            "method": "Z-Score",
            "threshold": threshold,
            "total_records": total_valid,
            "mean": round(mean_val, 4),
            "std": 0.0,
            "outlier_count": 0,
            "outlier_percentage": 0.0,
        }

    z_scores = (clean_series - mean_val) / std_val
    outlier_mask = z_scores.abs() > threshold

    outlier_count = int(outlier_mask.sum())
    outlier_pct = round((outlier_count / total_valid * 100.0) if total_valid > 0 else 0.0, 2)

    return {
        "method": "Z-Score",
        "threshold": threshold,
        "total_records": total_valid,
        "mean": round(mean_val, 4),
        "std": round(std_val, 4),
        "outlier_count": outlier_count,
        "outlier_percentage": outlier_pct,
    }


def calculate_correlations(
    df: pd.DataFrame,
    columns: List[str],
    method: str = "pearson"
) -> pd.DataFrame:
    """
    Calculate linear (Pearson) or monotonic (Spearman) correlation matrix across numeric columns.
    """
    existing_cols = [c for c in columns if c in df.columns]
    if not existing_cols:
        return pd.DataFrame()

    numeric_df = df[existing_cols].apply(pd.to_numeric, errors="coerce").dropna()
    if numeric_df.empty or len(numeric_df.columns) < 2:
        return pd.DataFrame()

    corr_matrix = numeric_df.corr(method=method)
    return corr_matrix.round(4)
