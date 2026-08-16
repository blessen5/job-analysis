"""
Comprehensive test suite for Phase 4 EDA and Descriptive Statistics.
"""

import pandas as pd
import pytest
from analytics.eda.overview import get_dataset_overview
from analytics.eda.jobs import analyze_job_distributions, analyze_job_titles
from analytics.eda.company import analyze_companies
from analytics.eda.location import analyze_locations
from analytics.eda.salary import analyze_salaries
from analytics.eda.experience import analyze_experience
from analytics.eda.runner import generate_structured_insights
from analytics.statistics.descriptive import (
    calculate_numerical_stats,
    calculate_categorical_stats,
    calculate_grouped_stats,
)
from analytics.statistics.distributions import (
    detect_outliers_iqr,
    detect_outliers_zscore,
    calculate_correlations,
)


@pytest.fixture
def sample_eda_dataframe():
    """Construct a clean sample dataset for testing Phase 4 EDA logic."""
    return pd.DataFrame({
        "job_id": [f"job_{i}" for i in range(1, 11)],
        "job_title": [
            "Data Analyst", "Data Analyst", "Data Engineer", "Data Scientist",
            "Senior Data Analyst", "ML Engineer", "BI Analyst", "Data Analyst",
            "Software Engineer", "Lead Data Engineer"
        ],
        "seniority_level": [
            "Mid Level", "Mid Level", "Mid Level", "Senior",
            "Senior", "Mid Level", "Junior", "Entry Level",
            "Mid Level", "Lead"
        ],
        "company": [
            "Acme", "Acme", "TechCorp", "DataInc",
            "Acme", "TechCorp", "AnalyticsCo", "Acme",
            "DevCorp", "DataInc"
        ],
        "location": ["Bangalore, India"] * 5 + ["Mumbai, India"] * 5,
        "city": ["Bangalore"] * 5 + ["Mumbai"] * 5,
        "state": ["Karnataka"] * 5 + ["Maharashtra"] * 5,
        "country": ["India"] * 10,
        "remote_type": ["Remote", "Remote", "Hybrid", "Onsite", "Remote", "Hybrid", "Onsite", "Remote", "Onsite", "Hybrid"],
        "employment_type": ["Full-time"] * 8 + ["Contract", "Full-time"],
        "salary_min": [500000.0, 600000.0, 800000.0, 1200000.0, 1500000.0, 1000000.0, 450000.0, 400000.0, 700000.0, 1800000.0],
        "salary_max": [800000.0, 900000.0, 1200000.0, 1600000.0, 2000000.0, 1400000.0, 600000.0, 500000.0, 900000.0, 2400000.0],
        "salary_midpoint": [650000.0, 750000.0, 1000000.0, 1400000.0, 1750000.0, 1200000.0, 525000.0, 450000.0, 800000.0, 2100000.0],
        "experience_min_years": [2.0, 3.0, 4.0, 5.0, 7.0, 4.0, 1.0, 0.0, 3.0, 8.0],
        "experience_max_years": [4.0, 5.0, 7.0, 8.0, 10.0, 6.0, 3.0, 1.0, 5.0, 12.0],
        "experience_level": ["Mid Level", "Mid Level", "Mid Level", "Senior", "Senior", "Mid Level", "Junior", "Entry Level", "Mid Level", "Lead"],
        "posted_date": ["2026-03-01", "2026-03-02", "2026-03-03", "2026-03-04", "2026-03-05", "2026-03-06", "2026-03-07", "2026-03-08", "2026-03-09", "2026-03-10"],
        "posted_year": [2026] * 10,
        "posted_month": [3] * 10,
        "skills": [["Python", "SQL"], ["Python", "Pandas"], ["SQL", "Spark"], ["Python", "PyTorch"], ["Python", "SQL"], ["Python", "TensorFlow"], ["SQL", "Power BI"], ["Excel", "SQL"], ["Java", "Spring"], ["Spark", "Airflow"]]
    })


def test_numerical_statistics():
    """Test calculation of mean, median, mode, IQR, std, min, max."""
    s = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0, 100.0])
    stats = calculate_numerical_stats(s)

    assert stats["count"] == 6
    assert stats["mean"] == pytest.approx(41.6667, abs=0.01)
    assert stats["median"] == 35.0
    assert stats["min"] == 10.0
    assert stats["max"] == 100.0
    assert stats["q1"] == 22.5
    assert stats["q3"] == 47.5
    assert stats["iqr"] == 25.0


def test_categorical_statistics():
    """Test categorical count, unique, top, frequency, and percentage."""
    s = pd.Series(["Remote", "Remote", "Hybrid", "Onsite", "Remote"])
    stats = calculate_categorical_stats(s)

    assert stats["count"] == 5
    assert stats["unique"] == 3
    assert stats["top"] == "Remote"
    assert stats["freq"] == 3
    assert stats["percentage"] == 60.0


def test_outlier_detection_iqr():
    """Test IQR outlier detection logic."""
    # Data with a clear high outlier (1000)
    s = pd.Series([10, 12, 14, 15, 16, 18, 20, 1000])
    iqr_res = detect_outliers_iqr(s, factor=1.5)

    assert iqr_res["method"] == "IQR"
    assert iqr_res["outlier_count"] == 1
    assert iqr_res["high_outlier_count"] == 1
    assert iqr_res["outlier_percentage"] == 12.5


def test_outlier_detection_zscore():
    """Test Z-score outlier detection logic."""
    s = pd.Series([10, 12, 14, 15, 16, 18, 20, 1000])
    z_res = detect_outliers_zscore(s, threshold=2.0)

    assert z_res["method"] == "Z-Score"
    assert z_res["outlier_count"] >= 1


def test_correlation_matrix(sample_eda_dataframe):
    """Test Pearson correlation calculation matrix."""
    corr_df = calculate_correlations(sample_eda_dataframe, ["salary_midpoint", "experience_min_years"])
    assert not corr_df.empty
    assert "salary_midpoint" in corr_df.columns
    assert corr_df.loc["salary_midpoint", "experience_min_years"] > 0.5


def test_dataset_overview(sample_eda_dataframe):
    """Test macro dataset overview calculation."""
    overview = get_dataset_overview(sample_eda_dataframe)

    assert overview["total_job_postings"] == 10
    assert overview["unique_companies"] == 5
    assert overview["unique_locations"] == 2
    assert overview["remote_job_percentage"] == 40.0
    assert overview["salary_completeness_pct"] == 100.0


def test_job_distributions_and_titles(sample_eda_dataframe):
    """Test job titles analysis and distributions."""
    dist = analyze_job_distributions(sample_eda_dataframe)
    assert "by_employment_type" in dist
    assert dist["by_remote_type"]["Remote"]["count"] == 4

    top_titles = analyze_job_titles(sample_eda_dataframe, top_n=5)
    assert not top_titles.empty
    assert top_titles.iloc[0]["job_title"] == "Data Analyst"
    assert top_titles.iloc[0]["count"] == 3


def test_company_and_location_analytics(sample_eda_dataframe):
    """Test company and location EDA functions."""
    comp = analyze_companies(sample_eda_dataframe, top_n=5)
    assert comp["total_unique_companies"] == 5
    assert comp["top_companies"][0]["company"] == "Acme"

    loc = analyze_locations(sample_eda_dataframe, top_n=5)
    assert len(loc["top_cities"]) == 2


def test_salary_and_experience_analytics(sample_eda_dataframe):
    """Test salary and experience module outputs."""
    sal = analyze_salaries(sample_eda_dataframe)
    assert sal["total_salary_records"] == 10
    assert sal["overall_statistics"]["min"] == 450000.0
    assert sal["overall_statistics"]["max"] == 2100000.0

    exp = analyze_experience(sample_eda_dataframe)
    assert "level_distribution" in exp
    assert exp["level_distribution"]["Mid Level"]["count"] == 5


def test_rule_based_insights(sample_eda_dataframe):
    """Test rule-based analytical insights formatting."""
    overview = get_dataset_overview(sample_eda_dataframe)
    dist = analyze_job_distributions(sample_eda_dataframe)
    top_titles = analyze_job_titles(sample_eda_dataframe)
    sal = analyze_salaries(sample_eda_dataframe)

    insights = generate_structured_insights(overview, dist, top_titles, sal, dist["by_remote_type"])
    assert len(insights) >= 2
    assert "topic" in insights[0]
    assert "finding" in insights[0]
    assert "evidence" in insights[0]
    assert "interpretation" in insights[0]
    assert "limitation" in insights[0]


def test_empty_dataframe_handling():
    """Test robustness when handling empty or missing columns."""
    empty_df = pd.DataFrame()
    overview = get_dataset_overview(empty_df)
    assert overview["total_job_postings"] == 0

    comp = analyze_companies(empty_df)
    assert comp["total_unique_companies"] == 0

    sal = analyze_salaries(empty_df)
    assert sal["total_salary_records"] == 0
