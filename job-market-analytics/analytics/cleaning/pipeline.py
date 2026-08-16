"""
Data cleaning and preprocessing pipeline for job market postings.

This module cleans raw job postings, parses salary/experience/location/remote specifications,
removes HTML tags, deduplicates records, and saves the cleaned dataset to data/processed/.
"""

import html
import logging
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from analytics.cleaning.schema import ColumnNormalizer, CANONICAL_SCHEMA

logger = logging.getLogger(__name__)


class JobDataCleaner:
    """Pipeline for cleaning and standardizing job posting datasets."""

    def __init__(self, custom_mapping: Optional[Dict[str, str]] = None):
        self.normalizer = ColumnNormalizer(custom_mapping=custom_mapping)

    @staticmethod
    def clean_text(text: Any) -> str:
        """Strip HTML tags, unescape HTML entities, and normalize whitespace."""
        if pd.isna(text) or text is None:
            return ""

        text_str = str(text)
        # Unescape HTML entities (e.g., &amp;, &lt;, &nbsp;)
        text_str = html.unescape(text_str)
        # Remove HTML tags using regex
        text_str = re.sub(r"<[^>]+>", " ", text_str)
        # Convert non-breaking spaces and clean whitespace
        text_str = text_str.replace("\xa0", " ")
        text_str = re.sub(r"\s+", " ", text_str).strip()

        return text_str

    @staticmethod
    def parse_salary_string(
        salary_str: Any,
        default_currency: str = "INR"
    ) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Parse raw salary string into (salary_min, salary_max, salary_currency).

        Supports formats like:
        - "10 LPA - 15 LPA", "5-8 Lakhs", "12.5 LPA"
        - "$80,000 - $120,000", "$50,000", "50k - 80k"
        - "₹4,000,000", "30,000 per month"
        - "$40 / hr"
        """
        if pd.isna(salary_str) or salary_str is None:
            return None, None, None

        s = str(salary_str).strip()
        if not s or s.lower() in ["not disclosed", "confidential", "na", "n/a", "none"]:
            return None, None, None

        # Currency detection
        currency = default_currency
        if "$" in s or "USD" in s.upper():
            currency = "USD"
        elif "€" in s or "EUR" in s.upper():
            currency = "EUR"
        elif "£" in s or "GBP" in s.upper():
            currency = "GBP"
        elif "₹" in s or "INR" in s.upper() or "LPA" in s.upper() or "LAKH" in s.upper():
            currency = "INR"

        # Check multiplier: LPA / Lakhs
        is_lpa = bool(re.search(r"\b(lpa|lakh|lakhs|lac|lacs)\b", s, re.IGNORECASE))
        is_monthly = bool(re.search(r"\b(month|monthly|pm|per month)\b", s, re.IGNORECASE))
        is_hourly = bool(re.search(r"\b(hour|hourly|hr|per hour)\b", s, re.IGNORECASE))

        # Extract all numeric values (integers or decimals)
        # Replace commas inside numbers first
        s_clean = s.replace(",", "")
        numbers = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", s_clean)]

        if not numbers:
            return None, None, currency

        # Handle 'k' / 'm' suffixes if present in clean string
        # Re-check numbers with k/m suffixes
        km_matches = re.findall(r"(\d+(?:\.\d+)?)\s*([kmKM])\b", s_clean)
        if km_matches:
            numbers = []
            for val, unit in km_matches:
                mult = 1_000 if unit.lower() == "k" else 1_000_000
                numbers.append(float(val) * mult)

        if is_lpa:
            # Convert Lakhs/LPA to actual amount (1 Lakh = 100,000)
            numbers = [num * 100_000 if num < 500 else num for num in numbers]
        elif is_monthly:
            # Convert monthly salary to annual equivalent
            numbers = [num * 12 for num in numbers]
        elif is_hourly:
            # Convert hourly salary to annual (2080 hours)
            numbers = [num * 2080 for num in numbers]

        # Calculate min and max
        if len(numbers) == 1:
            sal_min = sal_max = numbers[0]
        else:
            sal_min = min(numbers[0], numbers[1])
            sal_max = max(numbers[0], numbers[1])

        # Basic sanity bounds check
        if sal_min <= 0 or sal_min > 500_000_000:
            return None, None, currency

        return sal_min, sal_max, currency

    @staticmethod
    def parse_experience(
        exp_val: Any,
        job_title: str = "",
        description: str = ""
    ) -> str:
        """
        Classify experience into: Entry, Mid, Senior, Lead, Executive, Unspecified.
        """
        exp_str = str(exp_val).strip() if pd.notna(exp_val) and exp_val is not None else ""
        combined_text = f"{exp_str} {job_title} {description}".lower()

        # Check numeric years in experience string (e.g. "0-2 years", "7+ yrs", "5+ years")
        years_match = re.search(r"(\d+)\s*\+?\s*(?:-\s*(\d+)\s*\+?)?\s*(?:years?|yrs?)", exp_str.lower())
        if years_match:
            min_y = int(years_match.group(1))
            max_y = int(years_match.group(2)) if years_match.group(2) else min_y
            avg_y = (min_y + max_y) / 2

            if avg_y <= 2:
                return "Entry"
            elif avg_y <= 5:
                return "Mid"
            elif avg_y <= 8:
                return "Senior"
            else:
                return "Lead"

        # Keyword matching on title/text
        if re.search(r"\b(entry|fresher|graduate|junior|jr|intern|trainee)\b", combined_text):
            return "Entry"
        if re.search(r"\b(senior|sr|principal|architect|staff)\b", combined_text):
            return "Senior"
        if re.search(r"\b(lead|manager|head|director|vp|chief|executive)\b", combined_text):
            return "Lead"
        if re.search(r"\b(mid|intermediate|associate)\b", combined_text):
            return "Mid"

        return "Unspecified"

    @staticmethod
    def parse_remote_type(
        remote_val: Any,
        location: str = "",
        job_title: str = "",
        description: str = ""
    ) -> str:
        """
        Classify remote modality into: Remote, Hybrid, Onsite, Unspecified.
        """
        combined = f"{str(remote_val)} {location} {job_title} {description}".lower()

        if re.search(r"\b(work from home|wfh|remote|telecommute|anywhere|virtual)\b", combined):
            if re.search(r"\b(hybrid|partial|days in office)\b", combined):
                return "Hybrid"
            return "Remote"
        if re.search(r"\b(hybrid|flexible work)\b", combined):
            return "Hybrid"
        if re.search(r"\b(onsite|on-site|in-office|office based|in office)\b", combined):
            return "Onsite"

        return "Unspecified"

    @staticmethod
    def parse_employment_type(emp_val: Any, description: str = "") -> str:
        """
        Standardize employment contract terms: Full-time, Part-time, Contract, Internship, Unspecified.
        """
        combined = f"{str(emp_val)} {description}".lower()

        if re.search(r"\b(full-time|fulltime|full time|permanent)\b", combined):
            return "Full-time"
        if re.search(r"\b(part-time|parttime|part time)\b", combined):
            return "Part-time"
        if re.search(r"\b(contract|contractor|freelance|temporary)\b", combined):
            return "Contract"
        if re.search(r"\b(internship|intern|trainee)\b", combined):
            return "Internship"

        return "Unspecified"

    @staticmethod
    def parse_skills(skills_val: Any) -> List[str]:
        """Normalize raw skill strings or lists into a cleaned list of skill strings."""
        if pd.isna(skills_val) or skills_val is None:
            return []

        if isinstance(skills_val, list):
            raw_list = skills_val
        else:
            s = str(skills_val).strip()
            # Split by comma, pipe, or newline
            raw_list = re.split(r"[,|\n;]", s)

        cleaned_skills = []
        for sk in raw_list:
            sk_clean = str(sk).strip()
            if sk_clean and len(sk_clean) <= 50:
                cleaned_skills.append(sk_clean)

        return list(dict.fromkeys(cleaned_skills))

    def clean_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Execute full cleaning pipeline on input DataFrame.

        Returns:
            Tuple of (cleaned_df, cleaning_stats_summary)
        """
        raw_count = len(df)
        stats = {
            "initial_rows": raw_count,
            "dropped_missing_title": 0,
            "duplicates_removed": 0,
            "processed_rows": 0,
        }

        # Step 1: Normalize columns
        df_norm, mapping_used = self.normalizer.normalize_dataframe(df)

        # Step 2: Clean job_title and drop empty titles
        df_norm["job_title"] = df_norm["job_title"].apply(self.clean_text)
        valid_title_mask = df_norm["job_title"].str.len() > 0
        stats["dropped_missing_title"] = int((~valid_title_mask).sum())
        df_clean = df_norm[valid_title_mask].copy()

        # Step 3: Clean text fields
        text_cols = ["company", "location", "country", "description"]
        for col in text_cols:
            df_clean[col] = df_clean[col].apply(self.clean_text)

        # Fill missing text defaults
        df_clean["company"] = df_clean["company"].replace("", "Unspecified")
        df_clean["location"] = df_clean["location"].replace("", "Unspecified")
        df_clean["country"] = df_clean["country"].replace("", "India")  # Default to target dataset market

        # Step 4: Parse Salary
        raw_sal_col = df_clean.get("raw_salary_string")
        has_min_max = pd.notna(df_clean["salary_min"]).any() or pd.notna(df_clean["salary_max"]).any()

        if raw_sal_col is not None and not has_min_max:
            sal_results = raw_sal_col.apply(self.parse_salary_string)
            df_clean["salary_min"] = [r[0] for r in sal_results]
            df_clean["salary_max"] = [r[1] for r in sal_results]
            df_clean["salary_currency"] = [r[2] or "INR" for r in sal_results]
        else:
            df_clean["salary_min"] = pd.to_numeric(df_clean["salary_min"], errors="coerce")
            df_clean["salary_max"] = pd.to_numeric(df_clean["salary_max"], errors="coerce")
            df_clean["salary_currency"] = df_clean["salary_currency"].fillna("INR")

        # Step 5: Parse Experience
        df_clean["experience"] = df_clean.apply(
            lambda r: self.parse_experience(r["experience"], r["job_title"], r["description"]),
            axis=1
        )

        # Step 6: Parse Remote Type
        df_clean["remote_type"] = df_clean.apply(
            lambda r: self.parse_remote_type(r["remote_type"], r["location"], r["job_title"], r["description"]),
            axis=1
        )

        # Step 7: Parse Employment Type
        df_clean["employment_type"] = df_clean.apply(
            lambda r: self.parse_employment_type(r["employment_type"], r["description"]),
            axis=1
        )

        # Step 8: Parse Skills
        df_clean["skills"] = df_clean["skills"].apply(self.parse_skills)

        # Step 9: Assign job_id if missing
        df_clean["job_id"] = df_clean["job_id"].apply(
            lambda x: str(x).strip() if pd.notna(x) and str(x).strip() else f"job_{uuid.uuid4().hex[:10]}"
        )

        # Step 10: Deduplicate based on core content
        dedup_subset = ["job_title", "company", "location"]
        # Include description snippet in deduplication if available
        dedup_df = df_clean.drop_duplicates(subset=dedup_subset, keep="first")
        stats["duplicates_removed"] = len(df_clean) - len(dedup_df)
        df_final = dedup_df.copy()

        stats["processed_rows"] = len(df_final)

        # Format skills as comma-separated string for CSV export compatibility
        df_final_export = df_final.copy()
        df_final_export["skills_formatted"] = df_final_export["skills"].apply(
            lambda sk: ", ".join(sk) if isinstance(sk, list) else ""
        )

        return df_final_export, stats
