"""
Schema normalization and column mapping module for job market analytics.

This module provides standardized field definitions and automatic mapping logic to convert
heterogeneous raw job posting datasets (e.g. Kaggle datasets, scraped job boards)
into a unified analytical schema.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd


CANONICAL_SCHEMA: Dict[str, str] = {
    "job_id": "Unique identifier assigned to each job posting",
    "job_title": "Cleaned title of the job position as posted",
    "seniority_level": "Seniority tier: Intern, Entry Level, Junior, Mid Level, Senior, Lead, Manager, Director, Executive, Unknown",
    "company": "Name of the hiring company or employer",
    "location": "Geographic location string detailing city, state, or region",
    "city": "Extracted city name",
    "state": "Extracted state or province name",
    "country": "Country where the job position is located",
    "remote_type": "Work modality specification: Remote, Hybrid, Onsite, Unknown",
    "salary_min": "Lower bound of salary range",
    "salary_max": "Upper bound of salary range",
    "salary_currency": "3-letter currency code (INR, USD, etc.)",
    "salary_period": "Pay period: Annual, Monthly, Hourly, Unknown",
    "salary_midpoint": "Midpoint calculated as (salary_min + salary_max) / 2",
    "experience_min_years": "Minimum required experience in numeric years",
    "experience_max_years": "Maximum required experience in numeric years",
    "experience_level": "Standardized experience category: Entry Level, Junior, Mid Level, Senior, Lead, Unknown",
    "employment_type": "Employment terms: Full-time, Part-time, Contract, Internship, Temporary, Unknown",
    "description": "Original raw text body of the job advertisement",
    "description_clean": "HTML-stripped and whitespace-normalized job description text",
    "posted_date": "Publication date of job posting (YYYY-MM-DD)",
    "posted_year": "Publication year (YYYY)",
    "posted_month": "Publication month (1-12)",
    "posted_day": "Publication day of month (1-31)",
    "skills": "Extracted list of technical skills or required keywords",
    "validation_flags": "Comma-separated list of quality or logical validation warnings",
}

# Mapping of raw column name variations to canonical schema keys
COLUMN_SYNONYMS: Dict[str, List[str]] = {
    "job_id": [
        "job_id", "id", "posting_id", "jobid", "job_key", "job_code",
        "uniq_id", "position_id", "job_number"
    ],
    "job_title": [
        "job_title", "title", "jobtitle", "job_role", "designation",
        "position", "role", "job_name", "title_raw"
    ],
    "company": [
        "company", "company_name", "companyname", "organization",
        "employer", "company_raw", "hirer", "recruiter"
    ],
    "location": [
        "location", "job_location", "joblocation", "city", "place",
        "job_city", "work_location", "location_raw"
    ],
    "country": [
        "country", "country_name", "nation", "job_country"
    ],
    "remote_type": [
        "remote_type", "remote", "work_mode", "workmode", "work_type",
        "job_mode", "is_remote", "work_from_home", "wfh_status"
    ],
    "salary_min": [
        "salary_min", "min_salary", "minsalary", "salary_from",
        "salary_low", "min_ctc", "minimum_salary"
    ],
    "salary_max": [
        "salary_max", "max_salary", "maxsalary", "salary_to",
        "salary_high", "max_ctc", "maximum_salary"
    ],
    "salary_currency": [
        "salary_currency", "currency", "salarycurrency", "pay_currency"
    ],
    "experience": [
        "experience", "experience_level", "experiencelevel", "exp_required",
        "exp", "years_experience", "seniority", "experience_raw"
    ],
    "employment_type": [
        "employment_type", "job_type", "jobtype", "employmenttype",
        "contract_type", "type", "job_contract"
    ],
    "description": [
        "description", "job_description", "jobdescription", "summary",
        "details", "description_raw", "job_details", "content"
    ],
    "posted_date": [
        "posted_date", "date_posted", "posteddate", "post_date",
        "created_at", "posting_date", "date"
    ],
    "skills": [
        "skills", "key_skills", "keyskills", "skills_required",
        "technologies", "tags", "required_skills", "skill_set"
    ],
}

# Compound/unparsed salary columns to look out for
SALARY_COMPOUND_SYNONYMS: List[str] = [
    "salary", "salary_range", "salaryrange", "compensation",
    "pay_range", "ctc", "remuneration", "pay"
]


class ColumnNormalizer:
    """Class responsible for identifying and standardizing raw DataFrame columns."""

    def __init__(self, custom_mapping: Optional[Dict[str, str]] = None):
        self.custom_mapping = custom_mapping or {}

    def _normalize_name(self, col: str) -> str:
        """Normalize a column string into lowercase underscore format."""
        return (
            col.strip()
            .replace(" ", "_")
            .replace("-", "_")
            .replace(".", "_")
            .lower()
        )

    def detect_column_mapping(self, columns: List[str]) -> Tuple[Dict[str, str], Optional[str]]:
        """
        Map a list of raw column names to canonical schema fields.

        Returns:
            Tuple of (mapping_dict, compound_salary_col_if_any)
        """
        mapping: Dict[str, str] = {}
        assigned_canonical: set = set()
        compound_salary_col: Optional[str] = None

        normalized_cols = {col: self._normalize_name(col) for col in columns}

        # Apply custom mapping first
        for raw_col, canonical in self.custom_mapping.items():
            if raw_col in columns and canonical in CANONICAL_SCHEMA:
                mapping[raw_col] = canonical
                assigned_canonical.add(canonical)

        # Match against column synonyms
        for raw_col, norm_col in normalized_cols.items():
            if raw_col in mapping:
                continue

            for canonical_key, synonyms in COLUMN_SYNONYMS.items():
                if canonical_key in assigned_canonical:
                    continue
                norm_synonyms = [self._normalize_name(s) for s in synonyms]
                if norm_col in norm_synonyms:
                    mapping[raw_col] = canonical_key
                    assigned_canonical.add(canonical_key)
                    break

        # Check for unparsed compound salary column if min/max aren't explicitly mapped
        if "salary_min" not in assigned_canonical or "salary_max" not in assigned_canonical:
            for raw_col, norm_col in normalized_cols.items():
                if raw_col not in mapping:
                    norm_compound = [self._normalize_name(s) for s in SALARY_COMPOUND_SYNONYMS]
                    if norm_col in norm_compound:
                        compound_salary_col = raw_col
                        break

        return mapping, compound_salary_col

    def normalize_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Rename DataFrame columns to canonical schema names and ensure all canonical columns exist.

        Returns:
            Tuple of (normalized_df, mapping_used)
        """
        raw_columns = list(df.columns)
        mapping, compound_salary_col = self.detect_column_mapping(raw_columns)

        df_normalized = df.rename(columns=mapping).copy()

        # Preserve compound salary column if present
        if compound_salary_col and compound_salary_col not in mapping:
            df_normalized["raw_salary_string"] = df_normalized[compound_salary_col]

        # Ensure all canonical columns exist
        for canonical_field in CANONICAL_SCHEMA.keys():
            if canonical_field not in df_normalized.columns:
                df_normalized[canonical_field] = None

        return df_normalized, mapping
