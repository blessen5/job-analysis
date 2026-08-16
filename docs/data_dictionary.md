# Data Dictionary

This data dictionary defines the target analytical data model for the Job Market Analytics project. Every raw job posting ingested into the pipeline is validated, cleaned, and mapped to this schema.

---

## Target Analytical Schema Definition

### 1. `job_id`
* **Description**: Unique identifier assigned to each job posting.
* **Expected Type**: String / UUID
* **Example Format**: `"job_9f8e7d6a5b"` or `"550e8400-e29b-41d4-a716-446655440000"`
* **Required**: Yes
* **Cleaning Considerations**: Strip whitespace, ensure global uniqueness across raw source datasets, drop records with null identifiers.

### 2. `job_title`
* **Description**: The title of the job position as posted by the employer.
* **Expected Type**: String
* **Example Format**: `"Senior Data Engineer"`, `"Machine Learning Specialist"`
* **Required**: Yes
* **Cleaning Considerations**: Standardize character casing, strip trailing spaces, remove special characters/emojis, and map to normalized job role buckets in subsequent analytics phases.

### 3. `company`
* **Description**: Name of the hiring company or recruitment agency.
* **Expected Type**: String
* **Example Format**: `"Acme Analytics Inc."`, `"TechCorp"`
* **Required**: No
* **Cleaning Considerations**: Trim surrounding whitespace, normalize common corporate suffixes (`Inc.`, `LLC`, `Ltd.`), handle anonymized poster tags (e.g., `"Confidential"`).

### 4. `location`
* **Description**: Geographic location string detailing city, state, or region.
* **Expected Type**: String
* **Example Format**: `"London, UK"`, `"New York, NY"`, `"San Francisco, CA"`
* **Required**: No
* **Cleaning Considerations**: Split into city and state/country components, parse multi-location postings, remove duplicate whitespace.

### 5. `country`
* **Description**: Country where the job position is based or registered.
* **Expected Type**: String
* **Example Format**: `"United Kingdom"`, `"United States"`, `"Germany"`
* **Required**: No
* **Cleaning Considerations**: Map country names and 2-letter ISO codes (e.g., `"UK"` -> `"United Kingdom"`, `"USA"` -> `"United States"`) to standardized country strings.

### 6. `remote_type`
* **Description**: The work modality specification for the posting.
* **Expected Type**: Enum / String
* **Allowed Values**: `"Remote"`, `"Hybrid"`, `"Onsite"`, `"Unspecified"`
* **Example Format**: `"Remote"`
* **Required**: Yes (Defaults to `"Unspecified"` if missing)
* **Cleaning Considerations**: Extract keywords from job titles and descriptions (e.g., `"Work from Home"`, `"WFH"`, `"Telecommute"`, `"In-office"`) to infer modality.

### 7. `salary_min`
* **Description**: Lower bound of the reported annual salary range in numeric format.
* **Expected Type**: Float / Decimal
* **Example Format**: `85000.00`
* **Required**: No
* **Cleaning Considerations**: Convert hourly/monthly compensation rates to annual equivalents (assuming 2,080 working hours/year), remove currency symbols and commas, filter negative or implausible values.

### 8. `salary_max`
* **Description**: Upper bound of the reported annual salary range in numeric format.
* **Expected Type**: Float / Decimal
* **Example Format**: `115000.00`
* **Required**: No
* **Cleaning Considerations**: Ensure `salary_max` >= `salary_min`. Handle single-value salaries by setting `salary_min` equal to `salary_max`. Filter implausible upper bounds.

### 9. `salary_currency`
* **Description**: Three-letter ISO 4217 code representing the currency of reported compensation.
* **Expected Type**: String (ISO 4217)
* **Example Format**: `"USD"`, `"EUR"`, `"GBP"`
* **Required**: No (Defaults to `"USD"` or local market currency upon conversion)
* **Cleaning Considerations**: Standardize currency symbols (`$`, `£`, `€`) to standard 3-letter codes.

### 10. `experience`
* **Description**: Required seniority or experience level for the position.
* **Expected Type**: Enum / String
* **Allowed Values**: `"Entry"`, `"Mid"`, `"Senior"`, `"Lead"`, `"Executive"`, `"Unspecified"`
* **Example Format**: `"Senior"`
* **Required**: Yes (Defaults to `"Unspecified"`)
* **Cleaning Considerations**: Parse explicitly stated years of experience (e.g., `"5+ years"` -> `"Senior"`) and infer from title keywords (`"Junior"`, `"Senior"`, `"Principal"`).

### 11. `employment_type`
* **Description**: Employment contract terms.
* **Expected Type**: Enum / String
* **Allowed Values**: `"Full-time"`, `"Part-time"`, `"Contract"`, `"Internship"`, `"Unspecified"`
* **Example Format**: `"Full-time"`
* **Required**: Yes (Defaults to `"Unspecified"`)
* **Cleaning Considerations**: Map raw variants (`"Full Time"`, `"Permanent"`, `"Contractor"`) to standard values.

### 12. `description`
* **Description**: Full body text of the job advertisement.
* **Expected Type**: Text
* **Example Format**: `"We are looking for a skilled Data Engineer proficient in Python, SQL, and Docker..."`
* **Required**: Yes
* **Cleaning Considerations**: Strip HTML tags, unescape HTML entities, normalize whitespace, convert unicode non-breaking spaces.

### 13. `posted_date`
* **Description**: The date when the job posting was published.
* **Expected Type**: Date / ISO 8601 Timestamp
* **Example Format**: `"2026-03-15"` or `"2026-03-15T09:30:00Z"`
* **Required**: No
* **Cleaning Considerations**: Standardize relative date expressions (`"3 days ago"`) into absolute ISO dates relative to ingestion execution date.

### 14. `skills`
* **Description**: Extracted list of technical skills, tools, frameworks, and programming languages required by the posting.
* **Expected Type**: List of Strings
* **Example Format**: `["Python", "SQL", "PostgreSQL", "FastAPI", "Docker"]`
* **Required**: No (Populated during NLP skill extraction)
* **Cleaning Considerations**: Perform case-insensitive deduplication, map synonyms (e.g., `"Postgres"` -> `"PostgreSQL"`, `"JS"` -> `"JavaScript"`), remove generic stopwords.
