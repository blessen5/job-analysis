"""
Data Quality Visualization module.

Generates analytical quality charts (missing values bar chart, cleaning summary, quality score breakdown)
and saves output images to data/quality/.
"""

from pathlib import Path
from typing import Any, Dict, List
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generate_quality_charts(df: pd.DataFrame, scores: Dict[str, float], quality_dir: Path) -> List[Path]:
    """
    Generate data quality visualization charts and save them to quality_dir.
    """
    quality_dir.mkdir(parents=True, exist_ok=True)
    generated_files = []

    # Configure style
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"

    # 1. Missing Value Percentage Bar Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    missing_pcts = []
    col_names = []

    for col in df.columns:
        series = df[col]
        if series.dtype == "object":
            null_cnt = (series.isna() | series.astype(str).str.strip().isin(["", "nan", "None", "Unknown"])).sum()
        else:
            null_cnt = series.isna().sum()
        pct = (null_cnt / len(df) * 100.0) if len(df) > 0 else 0.0
        missing_pcts.append(pct)
        col_names.append(col)

    missing_df = pd.DataFrame({"Column": col_names, "Missing_Pct": missing_pcts})
    missing_df = missing_df.sort_values(by="Missing_Pct", ascending=False).head(12)

    sns.barplot(data=missing_df, x="Missing_Pct", y="Column", palette="viridis", ax=ax)
    ax.set_title("Missing Value Percentage per Column (%)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Missing Percentage (%)")
    ax.set_ylabel("Dataset Column")
    plt.tight_layout()

    chart1_path = quality_dir / "missing_values.png"
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    generated_files.append(chart1_path)

    # 2. Quality Score Dimension Breakdown Chart
    fig, ax = plt.subplots(figsize=(8, 4.5))
    score_df = pd.DataFrame([
        {"Dimension": "Completeness", "Score": scores.get("completeness", 0.0)},
        {"Dimension": "Validity", "Score": scores.get("validity", 0.0)},
        {"Dimension": "Uniqueness", "Score": scores.get("uniqueness", 0.0)},
        {"Dimension": "Consistency", "Score": scores.get("consistency", 0.0)},
        {"Dimension": "OVERALL", "Score": scores.get("overall_quality_score", 0.0)},
    ])

    colors = ["#3498db", "#2ecc71", "#e74c3c", "#9b59b6", "#2c3e50"]
    bars = ax.bar(score_df["Dimension"], score_df["Score"], color=colors, width=0.55)
    ax.set_ylim(0, 105)
    ax.set_title("Data Quality Score Breakdown (0 - 100)", fontsize=14, fontweight="bold")
    ax.set_ylabel("Score")

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    chart2_path = quality_dir / "quality_score.png"
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    generated_files.append(chart2_path)

    return generated_files
