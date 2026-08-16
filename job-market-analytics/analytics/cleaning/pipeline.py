"""
Data cleaning and preprocessing pipeline for job market postings.

This module cleans raw job postings, parses salary/experience/location/remote specifications,
removes HTML tags, validates data quality logic, deduplicates records, and saves output.
Executable via: `python -m analytics.cleaning.pipeline`
"""

import html
import logging
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from analytics.cleaning.schema import ColumnNormalizer, CANONICAL_SCHEMA

logger = logging.getLogger(__name__)


class JobDataCleaner:
    """Pipeline for cleaning, standardizing, and validating job posting datasets."""

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
        # Clean excessive punctuation / whitespace
        text_str = re.sub(r"\s+", " ", text_str).strip()

        return text_str

    @staticmethod
    def parse_seniority_level(title: str, description: str = "") -> str:
        """
        Extract standardized seniority level from job title and description.
        Allowed: Intern, Entry Level, Junior, Mid Level, Senior, Lead, Manager, Director, Executive, Unknown
        """
        combined = f"{title} {description}".lower()

        if re.search(r"\b(intern|internship|trainee|apprentice)\b", combined):
            return "Intern"
        if re.search(r"\b(entry|entry-level|fresher|freshers|graduate)\b", combined):
            return "Entry Level"
        if re.search(r"\b(junior|jr|associate|assistant)\b", combined):
            return "Junior"
        if re.search(r"\b(director|head of|vp|vice president)\b", combined):
            return "Director"
        if re.search(r"\b(executive|c-level|ceo|cto|cfo|cio)\b", combined):
            return "Executive"
        if re.search(r"\b(manager|lead manager|engineering manager)\b", combined):
            return "Manager"
        if re.search(r"\b(lead|team lead|principal|architect|staff)\b", combined):
            return "Lead"
        if re.search(r"\b(senior|sr|sr\.)\b", combined):
            return "Senior"
        if re.search(r"\b(mid|mid-level|intermediate)\b", combined):
            return "Mid Level"

        return "Unknown"

    @staticmethod
    def parse_salary_string(
        salary_str: Any,
        default_currency: str = "INR"
    ) -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str], Optional[float]]:
        """
        Parse raw salary string into (salary_min, salary_max, salary_currency, salary_period, salary_midpoint).

        Supports formats like:
        - "4-7 LPA", "10 LPA - 15 LPA", "5-8 Lakhs"
        - "$50,000-$70,000", "$80,000", "50k - 80k"
        - "₹4,00,000 - ₹7,00,000", "30,000 per month"
        - "$40 / hr"
        """
        if pd.isna(salary_str) or salary_str is None:
            return None, None, None, "Unknown", None

        s = str(salary_str).strip()
        if not s or s.lower() in ["not disclosed", "confidential", "na", "n/a", "none", "unknown"] or "negative" in s.lower():
            return None, None, None, "Unknown", None

        if s.startswith("-") and not re.search(r"\d+.*\d+", s):
            return None, None, None, "Unknown", None

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

        # Period detection
        period = "Annual"
        if re.search(r"\b(month|monthly|pm|per month)\b", s, re.IGNORECASE):
            period = "Monthly"
        elif re.search(r"\b(hour|hourly|hr|per hour)\b", s, re.IGNORECASE):
            period = "Hourly"

        # Check multiplier: LPA / Lakhs
        is_lpa = bool(re.search(r"\b(lpa|lakh|lakhs|lac|lacs)\b", s, re.IGNORECASE))

        # Clean commas (handling Indian numbering like 4,00,000)
        s_clean = s.replace(",", "")
        
        # Handle 'k' / 'm' suffixes
        km_matches = re.findall(r"(\d+(?:\.\d+)?)\s*([kmKM])\b", s_clean)
        if km_matches:
            numbers = []
            for val, unit in km_matches:
                mult = 1_000 if unit.lower() == "k" else 1_000_000
                numbers.append(float(val) * mult)
        else:
            numbers = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", s_clean)]

        if not numbers or s.strip().startswith("-"):
            return None, None, currency, period, None

        if is_lpa:
            # Convert Lakhs/LPA to annual INR (1 Lakh = 100,000)
            numbers = [num * 100_000 if num < 500 else num for num in numbers]

        if len(numbers) == 1:
            sal_min = sal_max = numbers[0]
        else:
            sal_min = min(numbers[0], numbers[1])
            sal_max = max(numbers[0], numbers[1])

        # Basic sanity bounds check
        if sal_min <= 0 or sal_min > 500_000_000:
            return None, None, currency, period, None

        midpoint = round((sal_min + sal_max) / 2.0, 2)
        return sal_min, sal_max, currency, period, midpoint

    @staticmethod
    def parse_experience(
        exp_val: Any,
        job_title: str = "",
        description: str = ""
    ) -> Tuple[Optional[float], Optional[float], str]:
        """
        Extract experience_min_years, experience_max_years, experience_level.
        Levels: Entry Level, Junior, Mid Level, Senior, Lead, Unknown
        """
        exp_str = str(exp_val).strip() if pd.notna(exp_val) and exp_val is not None else ""
        combined_text = f"{exp_str} {job_title} {description}".lower()

        # Check numeric years in experience string (e.g. "0-2 years", "1 to 3 yrs", "5+ years", "Freshers")
        if re.search(r"\b(fresher|freshers|no experience|0 years)\b", combined_text):
            return 0.0, 1.0, "Entry Level"

        years_match = re.search(r"(\d+)\s*\+?\s*(?:-\s*(\d+)\s*\+?|to\s*(\d+))?\s*(?:years?|yrs?)", exp_str.lower())
        if years_match:
            min_y = float(years_match.group(1))
            max_y_val = years_match.group(2) or years_match.group(3)
            max_y = float(max_y_val) if max_y_val else (min_y + 3.0 if "+" in exp_str else min_y)
            avg_y = (min_y + max_y) / 2.0

            if avg_y <= 1.0:
                level = "Entry Level"
            elif avg_y <= 3.0:
                level = "Junior"
            elif avg_y <= 6.0:
                level = "Mid Level"
            elif avg_y <= 10.0:
                level = "Senior"
            else:
                level = "Lead"

            return min_y, max_y, level

        # Keyword fallback
        if re.search(r"\b(entry|entry-level|fresher|freshers|graduate|intern)\b", combined_text):
            return 0.0, 1.0, "Entry Level"
        if re.search(r"\b(junior|jr)\b", combined_text):
            return 1.0, 3.0, "Junior"
        if re.search(r"\b(senior|sr|principal|architect|staff)\b", combined_text):
            return 5.0, 8.0, "Senior"
        if re.search(r"\b(lead|manager|head|director)\b", combined_text):
            return 8.0, 15.0, "Lead"
        if re.search(r"\b(mid|mid-level|intermediate)\b", combined_text):
            return 3.0, 5.0, "Mid Level"

        return None, None, "Unknown"

    @staticmethod
    def parse_location(location_val: Any) -> Tuple[str, str, str]:
        """
        Extract (city, state, country) from location string.
        """
        if pd.isna(location_val) or location_val is None:
            return "Unknown", "Unknown", "India"

        loc_str = str(location_val).strip()
        if not loc_str or loc_str.lower() in ["unknown", "n/a", "na", "remote", "none"]:
            return "Unknown", "Unknown", "India"

        parts = [p.strip() for p in loc_str.split(",") if p.strip()]

        city = parts[0] if len(parts) >= 1 else "Unknown"
        state = parts[1] if len(parts) >= 2 else "Unknown"
        country = parts[2] if len(parts) >= 3 else "India"

        # Standard Indian state/city mappings
        indian_cities = {
            "bangalore": ("Bangalore", "Karnataka"),
            "bengaluru": ("Bangalore", "Karnataka"),
            "mumbai": ("Mumbai", "Maharashtra"),
            "pune": ("Pune", "Maharashtra"),
            "hyderabad": ("Hyderabad", "Telangana"),
            "delhi": ("Delhi", "Delhi"),
            "new delhi": ("New Delhi", "Delhi"),
            "noida": ("Noida", "Uttar Pradesh"),
            "gurgaon": ("Gurgaon", "Haryana"),
            "gurugram": ("Gurgaon", "Haryana"),
            "chennai": ("Chennai", "Tamil Nadu"),
            "kolkata": ("Kolkata", "West Bengal"),
            "ahmedabad": ("Ahmedabad", "Gujarat"),
            "kochi": ("Kochi", "Kerala"),
            "trivandrum": ("Trivandrum", "Kerala"),
            "thiruvananthapuram": ("Trivandrum", "Kerala"),
        }

        city_lower = city.lower()
        if city_lower in indian_cities:
            std_city, std_state = indian_cities[city_lower]
            return std_city, std_state, "India"

        return city, state, country

    @staticmethod
    def parse_remote_type(
        remote_val: Any,
        location: str = "",
        job_title: str = "",
        description: str = ""
    ) -> str:
        """Classify remote modality into: Remote, Hybrid, Onsite, Unknown."""
        combined = f"{str(remote_val)} {location} {job_title} {description}".lower()

        if re.search(r"\b(work from home|wfh|remote|telecommute|anywhere|virtual)\b", combined):
            if re.search(r"\b(hybrid|partial|days in office)\b", combined):
                return "Hybrid"
            return "Remote"
        if re.search(r"\b(hybrid|flexible work)\b", combined):
            return "Hybrid"
        if re.search(r"\b(onsite|on-site|in-office|office based|in office|office)\b", combined):
            return "Onsite"

        return "Unknown"

    @staticmethod
    def parse_employment_type(emp_val: Any, description: str = "") -> str:
        """Standardize employment type into: Full-time, Part-time, Contract, Internship, Temporary, Unknown."""
        combined = f"{str(emp_val)} {description}".lower()

        if re.search(r"\b(full-time|fulltime|full time|permanent)\b", combined):
            return "Full-time"
        if re.search(r"\b(part-time|parttime|part time)\b", combined):
            return "Part-time"
        if re.search(r"\b(contract|contractor|freelance)\b", combined):
            return "Contract"
        if re.search(r"\b(internship|intern|trainee)\b", combined):
            return "Internship"
        if re.search(r"\b(temporary|temp)\b", combined):
            return "Temporary"

        return "Unknown"

    @staticmethod
    def parse_posted_date(date_val: Any) -> Tuple[Optional[str], Optional[int], Optional[int], Optional[int]]:
        """
        Normalize date string to ISO YYYY-MM-DD and extract year, month, day.
        """
        if pd.isna(date_val) or date_val is None:
            return None, None, None, None

        d_str = str(date_val).strip()
        if not d_str or d_str.lower() in ["unknown", "n/a", "none"]:
            return None, None, None, None

        # Try parsing ISO or standard date formats
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y", "%b %d, %Y", "%B %d, %Y"):
            try:
                dt = datetime.strptime(d_str.split("T")[0], fmt)
                iso_date = dt.strftime("%Y-%m-%d")
                return iso_date, dt.year, dt.month, dt.day
            except ValueError:
                continue

        # Regex fallback for YYYY-MM-DD or YYYY
        ymd_match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", d_str)
        if ymd_match:
            y, m, d = int(ymd_match.group(1)), int(ymd_match.group(2)), int(ymd_match.group(3))
            return f"{y:04d}-{m:02d}-{d:02d}", y, m, d

        return None, None, None, None

    @staticmethod
    def parse_skills(skills_val: Any) -> List[str]:
        """Normalize raw skill strings or lists into cleaned deduplicated skills list."""
        if pd.isna(skills_val) or skills_val is None:
            return []

        if isinstance(skills_val, list):
            raw_list = skills_val
        else:
            s = str(skills_val).strip()
            raw_list = re.split(r"[,|\n;]", s)

        cleaned_skills = []
        for sk in raw_list:
            sk_clean = str(sk).strip()
            if sk_clean and len(sk_clean) <= 50:
                cleaned_skills.append(sk_clean)

        return list(dict.fromkeys(cleaned_skills))

    def clean_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Execute full Phase 3 cleaning and validation pipeline.

        Returns:
            Tuple of (cleaned_df, summary_metrics_dict)
        """
        raw_count = len(df)
        stats = {
            "initial_rows": raw_count,
            "dropped_missing_title": 0,
            "exact_duplicates": 0,
            "likely_duplicates": 0,
            "processed_rows": 0,
            "invalid_salaries": 0,
            "invalid_experiences": 0,
            "invalid_dates": 0,
        }

        # Step 1: Detect exact duplicates before column normalization
        stats["exact_duplicates"] = int(df.duplicated().sum())

        # Step 2: Normalize columns
        df_norm, mapping_used = self.normalizer.normalize_dataframe(df)

        # Step 3: Clean job_title and drop missing titles
        df_norm["job_title"] = df_norm["job_title"].apply(self.clean_text)
        valid_title_mask = df_norm["job_title"].str.len() > 0
        stats["dropped_missing_title"] = int((~valid_title_mask).sum())
        df_clean = df_norm[valid_title_mask].copy()

        # Step 4: Seniority Level
        df_clean["seniority_level"] = df_clean.apply(
            lambda r: self.parse_seniority_level(r["job_title"], str(r.get("description", ""))),
            axis=1
        )

        # Step 5: Clean text fields
        df_clean["company"] = df_clean["company"].apply(self.clean_text).replace("", "Unknown")
        df_clean["location"] = df_clean["location"].apply(self.clean_text).replace("", "Unknown")
        df_clean["description_clean"] = df_clean["description"].apply(self.clean_text)

        # Step 6: Location Normalization
        loc_parsed = df_clean["location"].apply(self.parse_location)
        df_clean["city"] = [l[0] for l in loc_parsed]
        df_clean["state"] = [l[1] for l in loc_parsed]
        df_clean["country"] = [l[2] for l in loc_parsed]

        # Step 7: Parse Salary
        raw_sal_col = df_clean.get("raw_salary_string")
        has_min_max = pd.notna(df_clean["salary_min"]).any() or pd.notna(df_clean["salary_max"]).any()

        if raw_sal_col is not None and not has_min_max:
            sal_results = raw_sal_col.apply(self.parse_salary_string)
            df_clean["salary_min"] = [r[0] for r in sal_results]
            df_clean["salary_max"] = [r[1] for r in sal_results]
            df_clean["salary_currency"] = [r[2] or "INR" for r in sal_results]
            df_clean["salary_period"] = [r[3] for r in sal_results]
            df_clean["salary_midpoint"] = [r[4] for r in sal_results]
        else:
            df_clean["salary_min"] = pd.to_numeric(df_clean["salary_min"], errors="coerce")
            df_clean["salary_max"] = pd.to_numeric(df_clean["salary_max"], errors="coerce")
            df_clean["salary_currency"] = df_clean["salary_currency"].fillna("INR")
            df_clean["salary_period"] = df_clean.get("salary_period", pd.Series(["Annual"] * len(df_clean))).fillna("Annual")
            
            # Compute midpoint where possible
            df_clean["salary_midpoint"] = np.where(
                pd.notna(df_clean["salary_min"]) & pd.notna(df_clean["salary_max"]),
                (df_clean["salary_min"] + df_clean["salary_max"]) / 2.0,
                np.nan
            )

        # Step 8: Parse Experience
        exp_results = df_clean.apply(
            lambda r: self.parse_experience(r.get("experience", ""), r.get("job_title", ""), r.get("description_clean", "")),
            axis=1
        )
        df_clean["experience_min_years"] = [e[0] for e in exp_results]
        df_clean["experience_max_years"] = [e[1] for e in exp_results]
        df_clean["experience_level"] = [e[2] for e in exp_results]

        # Step 9: Parse Remote & Employment Type
        df_clean["remote_type"] = df_clean.apply(
            lambda r: self.parse_remote_type(r.get("remote_type", ""), r.get("location", ""), r.get("job_title", ""), r.get("description_clean", "")),
            axis=1
        )
        df_clean["employment_type"] = df_clean.apply(
            lambda r: self.parse_employment_type(r.get("employment_type", ""), r.get("description_clean", "")),
            axis=1
        )

        # Step 10: Date Parsing
        date_results = df_clean["posted_date"].apply(self.parse_posted_date)
        df_clean["posted_date"] = [d[0] for d in date_results]
        df_clean["posted_year"] = [d[1] for d in date_results]
        df_clean["posted_month"] = [d[2] for d in date_results]
        df_clean["posted_day"] = [d[3] for d in date_results]

        # Step 11: Skills Parsing
        df_clean["skills"] = df_clean["skills"].apply(self.parse_skills)

        # Step 12: Assign job_id if missing
        df_clean["job_id"] = df_clean["job_id"].apply(
            lambda x: str(x).strip() if pd.notna(x) and str(x).strip() else f"job_{uuid.uuid4().hex[:10]}"
        )

        # Step 13: Logical Rules & Validation Flags
        validation_flags_list = []
        for idx, row in df_clean.iterrows():
            flags = []
            # Check Salary Logic
            s_min, s_max = row["salary_min"], row["salary_max"]
            if pd.notna(s_min) and pd.notna(s_max) and s_min > s_max:
                flags.append("INVALID_SALARY_RANGE")
                stats["invalid_salaries"] += 1
            
            # Check Experience Logic
            e_min, e_max = row["experience_min_years"], row["experience_max_years"]
            if pd.notna(e_min) and pd.notna(e_max) and e_min > e_max:
                flags.append("INVALID_EXPERIENCE_RANGE")
                stats["invalid_experiences"] += 1

            # Check Date Logic
            if pd.isna(row["posted_date"]) and pd.notna(df_norm.loc[idx, "posted_date"]):
                flags.append("INVALID_DATE_FORMAT")
                stats["invalid_dates"] += 1

            validation_flags_list.append(", ".join(flags) if flags else "VALID")

        df_clean["validation_flags"] = validation_flags_list

        # Step 14: Deduplication (Likely duplicates)
        dedup_subset = ["job_title", "company", "location"]
        dedup_df = df_clean.drop_duplicates(subset=dedup_subset, keep="first")
        stats["likely_duplicates"] = len(df_clean) - len(dedup_df)
        df_final = dedup_df.copy()

        stats["processed_rows"] = len(df_final)

        # Format skills for export compatibility
        df_final["skills_formatted"] = df_final["skills"].apply(
            lambda sk: ", ".join(sk) if isinstance(sk, list) else ""
        )

        return df_final, stats


def main():
    """Module entry point: python -m analytics.cleaning.pipeline"""
    from analytics.cleaning.run_pipeline import run_pipeline
    sys.exit(run_pipeline())


if __name__ == "__main__":
    main()
