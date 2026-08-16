"""
Unit tests for data loading, column normalization, cleaning pipeline, and quality reporting.
"""

import pandas as pd
import pytest
from analytics.cleaning.schema import ColumnNormalizer
from analytics.cleaning.pipeline import JobDataCleaner
from analytics.cleaning.quality_report import DataQualityReporter
from analytics.cleaning.run_pipeline import find_raw_dataset, run_pipeline


def test_column_normalizer():
    """Test column detection and mapping against heterogeneous column names."""
    normalizer = ColumnNormalizer()

    raw_cols = [
        "jobTitle", "companyName", "jobLocation", "workMode",
        "salaryRange", "experienceLevel", "jobDescription", "keySkills"
    ]

    mapping, compound_sal = normalizer.detect_column_mapping(raw_cols)

    assert mapping.get("jobTitle") == "job_title"
    assert mapping.get("companyName") == "company"
    assert mapping.get("jobLocation") == "location"
    assert mapping.get("workMode") == "remote_type"
    assert mapping.get("experienceLevel") == "experience"
    assert mapping.get("jobDescription") == "description"
    assert mapping.get("keySkills") == "skills"
    assert compound_sal == "salaryRange"


def test_clean_text():
    """Test HTML tag removal, entity unescaping, and whitespace trimming."""
    raw_html = "<p>We are seeking a <b>Data Scientist</b> proficient in Python &amp; SQL.&nbsp;</p>"
    cleaned = JobDataCleaner.clean_text(raw_html)
    assert cleaned == "We are seeking a Data Scientist proficient in Python & SQL."


def test_parse_salary_string():
    """Test parsing various raw salary format strings."""
    # Test LPA (Lakhs Per Annum)
    sal_min, sal_max, curr = JobDataCleaner.parse_salary_string("10 LPA - 15 LPA")
    assert sal_min == 1_000_000.0
    assert sal_max == 1_500_000.0
    assert curr == "INR"

    # Test USD Range
    sal_min, sal_max, curr = JobDataCleaner.parse_salary_string("$80,000 - $120,000")
    assert sal_min == 80000.0
    assert sal_max == 120000.0
    assert curr == "USD"

    # Test Monthly salary
    sal_min, sal_max, curr = JobDataCleaner.parse_salary_string("₹30,000 per month")
    assert sal_min == 360000.0
    assert sal_max == 360000.0
    assert curr == "INR"

    # Test Hourly rate
    sal_min, sal_max, curr = JobDataCleaner.parse_salary_string("$50/hr")
    assert sal_min == 104000.0
    assert sal_max == 104000.0
    assert curr == "USD"

    # Test missing / confidential salary
    sal_min, sal_max, curr = JobDataCleaner.parse_salary_string("Not Disclosed")
    assert sal_min is None
    assert sal_max is None


def test_parse_experience():
    """Test experience level classification."""
    assert JobDataCleaner.parse_experience("0-1 years") == "Entry"
    assert JobDataCleaner.parse_experience("3-5 yrs") == "Mid"
    assert JobDataCleaner.parse_experience("7+ years") == "Senior"
    assert JobDataCleaner.parse_experience("", job_title="Senior Data Engineer") == "Senior"
    assert JobDataCleaner.parse_experience("", job_title="Junior Analyst") == "Entry"


def test_parse_remote_type():
    """Test remote work modality parsing."""
    assert JobDataCleaner.parse_remote_type("Work From Home") == "Remote"
    assert JobDataCleaner.parse_remote_type("Hybrid") == "Hybrid"
    assert JobDataCleaner.parse_remote_type("In-Office") == "Onsite"
    assert JobDataCleaner.parse_remote_type("", location="Remote, India") == "Remote"


def test_pipeline_clean_dataframe():
    """Test end-to-end cleaning pipeline on mock raw dataframe."""
    raw_data = {
        "jobTitle": ["<p>Data Analyst</p>", "Senior Data Engineer", "Data Analyst"],
        "companyName": ["Acme Corp", "TechCorp", "Acme Corp"],
        "jobLocation": ["Bangalore", "Mumbai", "Bangalore"],
        "salaryRange": ["6-10 LPA", "$100,000", "6-10 LPA"],
        "experienceLevel": ["1-3 years", "5-8 years", "1-3 years"],
        "workMode": ["Hybrid", "Remote", "Hybrid"],
        "jobDescription": ["Skills: Python, SQL", "Skills: Spark, AWS", "Skills: Python, SQL"],
        "keySkills": ["Python, SQL", "Spark, Python, AWS", "Python, SQL"]
    }

    df_raw = pd.DataFrame(raw_data)

    cleaner = JobDataCleaner()
    df_clean, stats = cleaner.clean_dataframe(df_raw)

    assert stats["initial_rows"] == 3
    # 3rd row is an exact duplicate of 1st row
    assert stats["duplicates_removed"] == 1
    assert len(df_clean) == 2

    assert "job_id" in df_clean.columns
    assert "salary_min" in df_clean.columns
    assert df_clean["job_title"].iloc[0] == "Data Analyst"
    assert df_clean["company"].iloc[0] == "Acme Corp"


def test_data_quality_reporter():
    """Test quality report metric generation and text formatting."""
    clean_data = {
        "job_id": ["job_1", "job_2"],
        "job_title": ["Data Analyst", "Data Engineer"],
        "company": ["Acme", "TechCorp"],
        "location": ["Bangalore", "Delhi"],
        "salary_min": [600000.0, None],
        "salary_max": [1000000.0, None],
        "salary_currency": ["INR", "INR"],
        "experience": ["Mid", "Senior"],
        "remote_type": ["Hybrid", "Remote"],
        "description": ["Details 1", "Details 2"],
        "skills_formatted": ["Python, SQL", "Python, Spark"]
    }

    df = pd.DataFrame(clean_data)
    reporter = DataQualityReporter(df)
    metrics = reporter.generate_metrics()

    assert metrics["total_rows"] == 2
    assert metrics["total_columns"] == 11
    assert metrics["duplicates"] == 0
    assert metrics["completeness"]["company"] == 100.0

    report_text = reporter.format_text_report()
    assert "Dataset Quality Report" in report_text
    assert "Rows: 2" in report_text


def test_find_raw_dataset_missing(tmp_path):
    """Test raw dataset finder when folder is empty."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    assert find_raw_dataset(raw_dir) is None
