"""
Descriptive statistics module for Job Market Analytics.

Calculates numerical and categorical statistics, quartiles, interquartile ranges,
modes, and grouped metric breakdowns for analytical datasets.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd


def calculate_numerical_stats(series: pd.Series) -> Dict[str, Any]:
    """
    Calculate comprehensive descriptive statistics for a numerical Series.

    Metrics:
        count, mean, median, mode, min, max, std, variance, q1, q2, q3, iqr
    """
    clean_series = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean_series) == 0:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "mode": None,
            "min": None,
            "max": None,
            "std": None,
            "variance": None,
            "q1": None,
            "q2": None,
            "q3": None,
            "iqr": None,
        }

    count = int(len(clean_series))
    mean_val = float(clean_series.mean())
    median_val = float(clean_series.median())

    # Mode calculation
    mode_res = clean_series.mode()
    mode_val = float(mode_res.iloc[0]) if not mode_res.empty else median_val

    min_val = float(clean_series.min())
    max_val = float(clean_series.max())
    std_val = float(clean_series.std()) if count > 1 else 0.0
    var_val = float(clean_series.var()) if count > 1 else 0.0

    q1 = float(clean_series.quantile(0.25))
    q2 = median_val
    q3 = float(clean_series.quantile(0.75))
    iqr = round(q3 - q1, 4)

    return {
        "count": count,
        "mean": round(mean_val, 4),
        "median": round(median_val, 4),
        "mode": round(mode_val, 4),
        "min": round(min_val, 4),
        "max": round(max_val, 4),
        "std": round(std_val, 4),
        "variance": round(var_val, 4),
        "q1": round(q1, 4),
        "q2": round(q2, 4),
        "q3": round(q3, 4),
        "iqr": round(iqr, 4),
    }


def calculate_categorical_stats(series: pd.Series) -> Dict[str, Any]:
    """
    Calculate descriptive metrics for a categorical Series.

    Metrics:
        count, unique, top, freq, percentage
    """
    clean_series = series.dropna().astype(str).str.strip()
    clean_series = clean_series[~clean_series.isin(["", "nan", "None", "Unknown"])]

    total_count = int(len(series))
    non_null_count = int(len(clean_series))

    if non_null_count == 0:
        return {
            "count": total_count,
            "non_null_count": 0,
            "unique": 0,
            "top": "N/A",
            "freq": 0,
            "percentage": 0.0,
        }

    val_counts = clean_series.value_counts()
    unique_cnt = int(len(val_counts))
    top_val = str(val_counts.index[0])
    freq_val = int(val_counts.iloc[0])
    pct_val = round((freq_val / total_count * 100.0) if total_count > 0 else 0.0, 2)

    return {
        "count": total_count,
        "non_null_count": non_null_count,
        "unique": unique_cnt,
        "top": top_val,
        "freq": freq_val,
        "percentage": pct_val,
    }


def calculate_grouped_stats(
    df: pd.DataFrame,
    group_col: str,
    target_col: str,
    min_group_size: int = 1
) -> pd.DataFrame:
    """
    Calculate descriptive statistics for target_col grouped by group_col.

    Returns DataFrame with columns:
        [group_col, count, mean, median, std, min, max]
    """
    if df.empty or group_col not in df.columns or target_col not in df.columns:
        return pd.DataFrame(columns=[group_col, "count", "mean", "median", "std", "min", "max"])

    valid_df = df.copy()
    valid_df[target_col] = pd.to_numeric(valid_df[target_col], errors="coerce")
    valid_df = valid_df.dropna(subset=[target_col])

    if valid_df.empty:
        return pd.DataFrame(columns=[group_col, "count", "mean", "median", "std", "min", "max"])

    grouped = valid_df.groupby(group_col)[target_col].agg(
        count="count",
        mean="mean",
        median="median",
        std="std",
        min="min",
        max="max"
    ).reset_index()

    # Filter out groups smaller than min_group_size
    grouped = grouped[grouped["count"] >= min_group_size].copy()

    # Round numeric output
    grouped["mean"] = grouped["mean"].round(2)
    grouped["median"] = grouped["median"].round(2)
    grouped["std"] = grouped["std"].fillna(0.0).round(2)
    grouped["min"] = grouped["min"].round(2)
    grouped["max"] = grouped["max"].round(2)

    return grouped.sort_values(by="count", ascending=False)
