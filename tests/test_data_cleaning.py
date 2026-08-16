"""
Comprehensive test suite for Phase 3 Data Cleaning and Data Quality Analysis.
"""

import pandas as pd
import pytest
from analytics.cleaning.pipeline import JobDataCleaner
from analytics.cleaning.quality_report import DataQualityReporter
from analytics.cleaning.schema import ColumnNormalizer


def test_missing_value_analysis():
    """Test calculation of missing count, missing percentage, and non-null count."""
    df = pd.DataFrame({
        "job_title": ["Data Analyst", "Data Engineer", "ML Engineer"],
        "salary_min": [50000.0, None, 80000.0],
        "location": ["Bangalore", "Unknown", ""],
    })

    reporter = DataQualityReporter(df)
    missing_df = reporter.generate_missing_value_analysis()

    salary_row = missing_df[missing_df["Column"] == "salary_min"].iloc[0]
    assert salary_row["Non_Null_Count"] == 2
    assert salary_row["Missing_Count"] == 1
    assert salary_row["Missing_Percentage"] == pytest.approx(33.33, abs=0.1)

    location_row = missing_df[missing_df["Column"] == "location"].iloc[0]
    assert location_row["Missing_Count"] == 2  # 'Unknown' and '' are missing


def test_duplicate_detection():
    """Test exact vs likely duplicate detection and summary metrics."""
    raw_data = {
        "jobTitle": ["Data Analyst", "Data Analyst", "Data Analyst", "Data Engineer"],
        "companyName": ["Acme", "Acme", "Acme", "TechCorp"],
        "jobLocation": ["Bangalore", "Bangalore", "Bangalore", "Mumbai"],
        "jobDescription": ["SQL Python", "SQL Python", "Different desc", "Spark AWS"],
    }
    df = pd.DataFrame(raw_data)

    cleaner = JobDataCleaner()
    df_clean, stats = cleaner.clean_dataframe(df)

    assert stats["initial_rows"] == 4
    assert stats["exact_duplicates"] == 1  # Rows 0 & 1 are exact raw matches
    assert stats["likely_duplicates"] == 2  # Rows 1 & 2 match Title/Company/Location
    assert stats["processed_rows"] == 2


def test_job_title_and_seniority():
    """Test job title cleaning and seniority level parsing."""
    assert JobDataCleaner.parse_seniority_level("Senior Data Analyst") == "Senior"
    assert JobDataCleaner.parse_seniority_level("Junior Software Engineer") == "Junior"
    assert JobDataCleaner.parse_seniority_level("Data Science Intern") == "Intern"
    assert JobDataCleaner.parse_seniority_level("Lead Architect") == "Lead"
    assert JobDataCleaner.parse_seniority_level("Engineering Director") == "Director"
    assert JobDataCleaner.parse_seniority_level("Data Analyst") == "Unknown"


def test_experience_normalization():
    """Test experience min/max years and level classification."""
    min_y, max_y, level = JobDataCleaner.parse_experience("0-1 years")
    assert min_y == 0.0 and max_y == 1.0 and level == "Entry Level"

    min_y, max_y, level = JobDataCleaner.parse_experience("3 to 5 yrs")
    assert min_y == 3.0 and max_y == 5.0 and level == "Mid Level"

    min_y, max_y, level = JobDataCleaner.parse_experience("7+ years")
    assert min_y == 7.0 and max_y == 10.0 and level == "Senior"

    min_y, max_y, level = JobDataCleaner.parse_experience("Freshers welcome")
    assert min_y == 0.0 and level == "Entry Level"

    min_y, max_y, level = JobDataCleaner.parse_experience("")
    assert min_y is None and max_y is None and level == "Unknown"


def test_salary_cleaning_and_midpoint():
    """Test salary parsing across LPA, USD, monthly, hourly, and midpoint calculation."""
    # LPA
    s_min, s_max, curr, period, mid = JobDataCleaner.parse_salary_string("4-7 LPA")
    assert s_min == 400000.0 and s_max == 700000.0 and curr == "INR" and period == "Annual" and mid == 550000.0

    # USD Range
    s_min, s_max, curr, period, mid = JobDataCleaner.parse_salary_string("$50,000 - $70,000")
    assert s_min == 50000.0 and s_max == 70000.0 and curr == "USD" and period == "Annual" and mid == 60000.0

    # Monthly
    s_min, s_max, curr, period, mid = JobDataCleaner.parse_salary_string("₹30,000 per month")
    assert s_min == 30000.0 and curr == "INR" and period == "Monthly"

    # Hourly
    s_min, s_max, curr, period, mid = JobDataCleaner.parse_salary_string("$40 / hr")
    assert s_min == 40.0 and curr == "USD" and period == "Hourly"

    # Confidential
    s_min, s_max, curr, period, mid = JobDataCleaner.parse_salary_string("Not Disclosed")
    assert s_min is None and s_max is None and period == "Unknown" and mid is None


def test_location_normalization():
    """Test city, state, country extraction."""
    city, state, country = JobDataCleaner.parse_location("Bangalore, Karnataka, India")
    assert city == "Bangalore" and state == "Karnataka" and country == "India"

    city, state, country = JobDataCleaner.parse_location("Mumbai")
    assert city == "Mumbai" and state == "Maharashtra" and country == "India"

    city, state, country = JobDataCleaner.parse_location("Unknown")
    assert city == "Unknown" and state == "Unknown" and country == "India"


def test_remote_and_employment_normalization():
    """Test remote modality and employment type classification."""
    assert JobDataCleaner.parse_remote_type("Work From Home") == "Remote"
    assert JobDataCleaner.parse_remote_type("Hybrid") == "Hybrid"
    assert JobDataCleaner.parse_remote_type("In-Office") == "Onsite"
    assert JobDataCleaner.parse_remote_type("") == "Unknown"

    assert JobDataCleaner.parse_employment_type("Full-Time") == "Full-time"
    assert JobDataCleaner.parse_employment_type("Part Time") == "Part-time"
    assert JobDataCleaner.parse_employment_type("Contractor") == "Contract"
    assert JobDataCleaner.parse_employment_type("Internship") == "Internship"
    assert JobDataCleaner.parse_employment_type("Temporary") == "Temporary"


def test_text_cleaning_description():
    """Test HTML stripping, entity unescaping, and preserving raw text."""
    raw_html = "<p>Required: <b>Python &amp; SQL</b> skills.&nbsp;</p>"
    cleaned = JobDataCleaner.clean_text(raw_html)
    assert cleaned == "Required: Python & SQL skills."


def test_date_normalization():
    """Test date parsing to YYYY-MM-DD and year/month/day extraction."""
    iso_date, y, m, d = JobDataCleaner.parse_posted_date("2026-03-15")
    assert iso_date == "2026-03-15" and y == 2026 and m == 3 and d == 15

    iso_date, y, m, d = JobDataCleaner.parse_posted_date("15-03-2026")
    assert iso_date == "2026-03-15" and y == 2026 and m == 3 and d == 15

    iso_date, y, m, d = JobDataCleaner.parse_posted_date("Invalid Date")
    assert iso_date is None and y is None


def test_data_validation_logical_rules():
    """Test flagging of logical violations (salary_min > salary_max)."""
    raw_df = pd.DataFrame({
        "jobTitle": ["Data Analyst", "Data Engineer"],
        "salary_min": [100000.0, 50000.0],
        "salary_max": [50000.0, 80000.0],  # Row 0 has s_min > s_max
    })

    cleaner = JobDataCleaner()
    df_clean, stats = cleaner.clean_dataframe(raw_df)

    assert stats["invalid_salaries"] == 1
    assert "INVALID_SALARY_RANGE" in df_clean["validation_flags"].iloc[0]
    assert df_clean["validation_flags"].iloc[1] == "VALID"


def test_quality_score_calculation():
    """Test 4-dimension transparent Data Quality Score formula."""
    clean_df = pd.DataFrame({
        "job_title": ["Data Analyst", "Data Engineer"],
        "company": ["Acme", "TechCorp"],
        "location": ["Bangalore", "Delhi"],
        "salary_min": [500000.0, 800000.0],
        "experience_level": ["Mid Level", "Senior"],
        "description_clean": ["Desc 1", "Desc 2"],
        "skills_formatted": ["Python, SQL", "Spark, AWS"],
        "seniority_level": ["Mid Level", "Senior"],
        "remote_type": ["Hybrid", "Remote"],
        "employment_type": ["Full-time", "Full-time"],
        "validation_flags": ["VALID", "VALID"]
    })

    stats = {
        "initial_rows": 2,
        "exact_duplicates": 0,
        "likely_duplicates": 0,
    }

    reporter = DataQualityReporter(clean_df, cleaning_stats=stats)
    scores = reporter.calculate_quality_score()

    assert scores["completeness"] == 100.0
    assert scores["validity"] == 100.0
    assert scores["uniqueness"] == 100.0
    assert scores["consistency"] == 100.0
    assert scores["overall_quality_score"] == 100.0


def test_edge_cases():
    """Test edge cases: empty strings, None, invalid values."""
    cleaner = JobDataCleaner()
    
    # Empty string text
    assert cleaner.clean_text("") == ""
    assert cleaner.clean_text(None) == ""

    # Invalid salary
    s_min, s_max, curr, period, mid = cleaner.parse_salary_string("Negative -100")
    assert s_min is None

    # Invalid date
    d_iso, y, m, d = cleaner.parse_posted_date("")
    assert d_iso is None
