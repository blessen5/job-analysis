"""
Data quality reporting module.

Generates comprehensive data quality metrics, missing value statistics, duplicate metrics,
transparent Data Quality Score calculations, and outputs JSON/CSV reports to data/quality/.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd


class DataQualityReporter:
    """Calculates data quality metrics and exports structured quality reports."""

    def __init__(self, df: pd.DataFrame, cleaning_stats: Optional[Dict[str, Any]] = None):
        self.df = df.copy()
        self.stats = cleaning_stats or {}

    def generate_missing_value_analysis(self) -> pd.DataFrame:
        """
        Generate detailed missing value analysis per column.
        Columns: Column, Non_Null_Count, Missing_Count, Missing_Percentage
        """
        total_rows = len(self.df)
        records = []

        def _is_missing(val: Any) -> bool:
            if pd.isna(val) or val is None:
                return True
            s_val = str(val).strip().lower()
            return s_val in ("", "nan", "none", "unknown")

        for col in self.df.columns:
            series = self.df[col]
            null_mask = series.apply(_is_missing)

            missing_cnt = int(null_mask.sum())
            non_null_cnt = total_rows - missing_cnt
            missing_pct = round((missing_cnt / total_rows * 100.0) if total_rows > 0 else 0.0, 2)

            records.append({
                "Column": col,
                "Non_Null_Count": non_null_cnt,
                "Missing_Count": missing_cnt,
                "Missing_Percentage": missing_pct,
            })

        return pd.DataFrame(records)

    def calculate_quality_score(self) -> Dict[str, float]:
        """
        Calculate transparent 4-dimension Data Quality Score:
        - Completeness (35%): Average non-null % across key analytical fields
        - Validity (25%): Percentage of records passing logical rules
        - Uniqueness (20%): 100% - duplicate percentage
        - Consistency (20%): Percentage of standardized categorical fields mapped to non-Unknown values
        """
        total_rows = len(self.df)
        if total_rows == 0:
            return {
                "completeness": 0.0,
                "validity": 0.0,
                "uniqueness": 0.0,
                "consistency": 0.0,
                "overall_quality_score": 0.0
            }

        # 1. Completeness Score
        key_fields = ["job_title", "company", "location", "salary_min", "experience_level", "description_clean", "skills_formatted"]
        comp_scores = []
        for f in key_fields:
            if f in self.df.columns:
                series = self.df[f]
                null_cnt = (series.isna() | series.astype(str).str.strip().isin(["", "nan", "None", "Unknown"])).sum()
                comp_scores.append(100.0 - (null_cnt / total_rows * 100.0))
        completeness = round(sum(comp_scores) / len(comp_scores) if comp_scores else 0.0, 2)

        # 2. Validity Score
        if "validation_flags" in self.df.columns:
            valid_cnt = (self.df["validation_flags"] == "VALID").sum()
            validity = round(valid_cnt / total_rows * 100.0, 2)
        else:
            validity = 100.0

        # 3. Uniqueness Score
        exact_dups = self.stats.get("exact_duplicates", 0)
        likely_dups = self.stats.get("likely_duplicates", 0)
        initial_rows = self.stats.get("initial_rows", total_rows)
        dup_pct = ((exact_dups + likely_dups) / initial_rows * 100.0) if initial_rows > 0 else 0.0
        uniqueness = round(max(0.0, 100.0 - dup_pct), 2)

        # 4. Consistency Score
        cat_cols = ["seniority_level", "remote_type", "employment_type", "experience_level"]
        cat_scores = []
        for col in cat_cols:
            if col in self.df.columns:
                known_cnt = (self.df[col] != "Unknown").sum()
                cat_scores.append(known_cnt / total_rows * 100.0)
        consistency = round(sum(cat_scores) / len(cat_scores) if cat_scores else 0.0, 2)

        # Overall Quality Score
        overall = round(
            (0.35 * completeness) +
            (0.25 * validity) +
            (0.20 * uniqueness) +
            (0.20 * consistency),
            2
        )

        return {
            "completeness": completeness,
            "validity": validity,
            "uniqueness": uniqueness,
            "consistency": consistency,
            "overall_quality_score": overall
        }

    def generate_before_after_summary(self) -> pd.DataFrame:
        """Generate before vs after cleaning comparison metrics."""
        init_rows = self.stats.get("initial_rows", len(self.df))
        final_rows = len(self.df)

        exact_dups = self.stats.get("exact_duplicates", 0)
        likely_dups = self.stats.get("likely_duplicates", 0)

        missing_sal_pct = (self.df["salary_min"].isna().sum() / final_rows * 100.0) if final_rows > 0 else 0.0
        missing_loc_pct = ((self.df["location"] == "Unknown").sum() / final_rows * 100.0) if final_rows > 0 else 0.0

        records = [
            {"Metric": "Rows", "Before": init_rows, "After": final_rows},
            {"Metric": "Exact Duplicates", "Before": exact_dups, "After": 0},
            {"Metric": "Likely Duplicates", "Before": likely_dups, "After": 0},
            {"Metric": "Missing Salary %", "Before": "N/A", "After": f"{missing_sal_pct:.2f}%"},
            {"Metric": "Missing Location %", "Before": "N/A", "After": f"{missing_loc_pct:.2f}%"},
            {"Metric": "Invalid Salary", "Before": self.stats.get("invalid_salaries", 0), "After": 0},
            {"Metric": "Invalid Dates", "Before": self.stats.get("invalid_dates", 0), "After": 0},
        ]
        return pd.DataFrame(records)

    def export_reports(self, quality_dir: Path) -> Dict[str, Any]:
        """
        Export quality metrics, CSV report, and JSON summary to data/quality/.
        """
        quality_dir.mkdir(parents=True, exist_ok=True)

        missing_df = self.generate_missing_value_analysis()
        scores = self.calculate_quality_score()
        before_after_df = self.generate_before_after_summary()

        # Save CSV report
        csv_path = quality_dir / "data_quality_report.csv"
        missing_df.to_csv(csv_path, index=False)

        # Save Cleaning Summary JSON
        summary_json_path = quality_dir / "cleaning_summary.json"
        summary_data = {
            "cleaning_statistics": self.stats,
            "data_quality_scores": scores,
            "before_after_comparison": before_after_df.to_dict(orient="records"),
        }
        with open(summary_json_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)

        # Save Full Data Quality Report JSON
        report_json_path = quality_dir / "data_quality_report.json"
        full_report_data = {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "missing_value_analysis": missing_df.to_dict(orient="records"),
            "data_quality_scores": scores,
            "cleaning_statistics": self.stats,
        }
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(full_report_data, f, indent=2)

        return full_report_data

    def format_text_report(self) -> str:
        """Format metrics into readable text console report."""
        scores = self.calculate_quality_score()
        before_after_df = self.generate_before_after_summary()
        missing_df = self.generate_missing_value_analysis()

        lines = []
        lines.append("Data Quality & Cleaning Summary Report")
        lines.append("=" * 45)
        lines.append(f"Original Rows:       {self.stats.get('initial_rows', len(self.df))}")
        lines.append(f"Processed Rows:      {len(self.df)}")
        lines.append(f"Exact Duplicates:    {self.stats.get('exact_duplicates', 0)}")
        lines.append(f"Likely Duplicates:   {self.stats.get('likely_duplicates', 0)}")
        lines.append("")
        lines.append("Transparent Data Quality Scores")
        lines.append("-" * 45)
        lines.append(f"Completeness Score:  {scores['completeness']:.2f} / 100")
        lines.append(f"Validity Score:      {scores['validity']:.2f} / 100")
        lines.append(f"Uniqueness Score:    {scores['uniqueness']:.2f} / 100")
        lines.append(f"Consistency Score:   {scores['consistency']:.2f} / 100")
        lines.append(f"OVERALL QUALITY:     {scores['overall_quality_score']:.2f} / 100")
        lines.append("")
        lines.append("Before / After Comparison")
        lines.append("-" * 45)
        for _, row in before_after_df.iterrows():
            lines.append(f"{row['Metric']:<22}: Before={row['Before']} | After={row['After']}")

        return "\n".join(lines)
