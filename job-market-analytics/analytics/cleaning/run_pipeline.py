"""
CLI Execution Entry Point for Dataset Ingestion and Data Pipeline.

Checks data/raw/ for raw CSV dataset, performs column normalization, cleans records,
generates transparent data quality scores, exports data/quality/ reports, and saves clean data.
"""

import sys
from pathlib import Path
import pandas as pd

from analytics.cleaning.pipeline import JobDataCleaner
from analytics.cleaning.quality_report import DataQualityReporter
from analytics.cleaning.quality_charts import generate_quality_charts


def find_raw_dataset(raw_dir: Path) -> Path:
    """Find the raw CSV dataset in raw_dir."""
    if not raw_dir.exists():
        raw_dir.mkdir(parents=True, exist_ok=True)

    csv_files = list(raw_dir.glob("*.csv"))
    if not csv_files:
        return None
    return csv_files[0]


def run_pipeline():
    """Execute dataset ingestion, cleaning, reporting, visualization, and saving."""
    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    quality_dir = project_root / "data" / "quality"

    processed_dir.mkdir(parents=True, exist_ok=True)
    quality_dir.mkdir(parents=True, exist_ok=True)

    raw_csv = find_raw_dataset(raw_dir)

    if raw_csv is None:
        print("\n" + "=" * 70)
        print(" [!] DATASET NOT FOUND")
        print("=" * 70)
        print(" No raw CSV dataset was found in:")
        print(f"   {raw_dir}")
        print("\n Per project rules, synthetic/fake data is NOT generated.")
        print("\n Please download the preferred dataset:")
        print("   Kaggle - Indian Job Market Dataset 2025-2026")
        print(" And place the CSV file in:")
        print(f"   {raw_dir}/")
        print("=" * 70 + "\n")
        return 1

    print(f"\n[+] Found raw dataset: {raw_csv.name}")
    try:
        df_raw = pd.read_csv(raw_csv)
        print(f"[+] Successfully loaded {len(df_raw)} raw records with {len(df_raw.columns)} columns.")
    except Exception as e:
        print(f"[-] Error reading CSV file: {e}")
        return 1

    cleaner = JobDataCleaner()
    print("[+] Executing data cleaning and normalization pipeline...")
    df_cleaned, stats = cleaner.clean_dataframe(df_raw)

    print("\n[+] Cleaning Summary:")
    print(f"    - Initial rows:          {stats['initial_rows']}")
    print(f"    - Dropped missing title: {stats['dropped_missing_title']}")
    print(f"    - Exact duplicates:      {stats['exact_duplicates']}")
    print(f"    - Likely duplicates:     {stats['likely_duplicates']}")
    print(f"    - Final processed rows:  {stats['processed_rows']}")

    reporter = DataQualityReporter(df_cleaned, cleaning_stats=stats)
    report_text = reporter.format_text_report()
    print("\n" + report_text + "\n")

    print("[+] Exporting quality reports to data/quality/...")
    reporter.export_reports(quality_dir)

    print("[+] Generating data quality visualization charts...")
    scores = reporter.calculate_quality_score()
    charts = generate_quality_charts(df_cleaned, scores, quality_dir)
    for c in charts:
        print(f"    - Chart generated: {c.name}")

    output_path = processed_dir / "clean_job_postings.csv"
    df_cleaned.to_csv(output_path, index=False)
    print(f"[+] Processed dataset saved to: {output_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(run_pipeline())
