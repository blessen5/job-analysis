"""
Data quality reporting module.

Generates comprehensive data quality metrics, missing value statistics, completeness scores,
and formatted reports for job posting datasets.
"""

from typing import Any, Dict
import pandas as pd


class DataQualityReporter:
    """Calculates data quality metrics and formats summary reports."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def generate_metrics(self) -> Dict[str, Any]:
        """
        Calculate data quality statistics for the dataset.
        """
        total_rows = len(self.df)
        total_cols = len(self.df.columns)

        missing_counts: Dict[str, int] = {}
        missing_pcts: Dict[str, float] = {}
        unique_counts: Dict[str, int] = {}
        data_types: Dict[str, str] = {}

        for col in self.df.columns:
            # Consider empty string/whitespace/Unspecified as missing for completeness
            series = self.df[col]
            data_types[col] = str(series.dtype)
            unique_counts[col] = int(series.nunique(dropna=True))

            if series.dtype == "object":
                null_mask = series.isna() | (series.astype(str).str.strip().isin(["", "nan", "None", "Unspecified"]))
            else:
                null_mask = series.isna()

            missing_cnt = int(null_mask.sum())
            missing_counts[col] = missing_cnt
            missing_pcts[col] = round((missing_cnt / total_rows * 100) if total_rows > 0 else 0.0, 2)

        # Duplicate counts
        if "job_title" in self.df.columns and "company" in self.df.columns and "location" in self.df.columns:
            duplicate_count = int(self.df.duplicated(subset=["job_title", "company", "location"]).sum())
        else:
            duplicate_count = int(self.df.duplicated().sum())

        # Key analytical completeness percentages
        def get_completeness(col_name: str) -> float:
            if col_name not in missing_pcts:
                return 0.0
            return round(100.0 - missing_pcts[col_name], 2)

        completeness = {
            "salary": get_completeness("salary_min") if "salary_min" in self.df.columns else 0.0,
            "location": get_completeness("location"),
            "skills": get_completeness("skills_formatted") if "skills_formatted" in self.df.columns else get_completeness("skills"),
            "description": get_completeness("description"),
            "company": get_completeness("company"),
            "experience": get_completeness("experience"),
        }

        return {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "missing_counts": missing_counts,
            "missing_percentages": missing_pcts,
            "unique_counts": unique_counts,
            "data_types": data_types,
            "duplicates": duplicate_count,
            "completeness": completeness,
        }

    def format_text_report(self) -> str:
        """Format metrics into readable text report format as specified in prompt."""
        m = self.generate_metrics()

        lines = []
        lines.append("Dataset Quality Report")
        lines.append("=" * 35)
        lines.append(f"Rows: {m['total_rows']}")
        lines.append(f"Columns: {m['total_columns']}")
        lines.append(f"Duplicates: {m['duplicates']}")
        lines.append("")
        lines.append("Missing Values")
        lines.append("-" * 35)

        for col, pct in m["missing_percentages"].items():
            lines.append(f"{col:<20}: {pct:.2f}% ({m['missing_counts'][col]} missing)")

        lines.append("")
        lines.append("Completeness Summary")
        lines.append("-" * 35)
        for field, comp in m["completeness"].items():
            lines.append(f"{field:<20}: {comp:.2f}% complete")

        return "\n".join(lines)
