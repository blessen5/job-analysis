# Statistical Analysis Methodology

This document outlines the statistical concepts, descriptive formulas, outlier detection rules, and correlation methods applied in the **Job Market Analytics & Skill Demand Analysis Platform**.

---

## 1. Descriptive Statistical Metrics

For numerical variables (such as `salary_min`, `salary_max`, `salary_midpoint`, `experience_min_years`), both parametric and non-parametric statistics are reported to provide complete distributional context.

### Parametric Metrics:
- **Mean ($\mu$)**:
  $$\mu = \frac{1}{N} \sum_{i=1}^{N} x_i$$
- **Variance ($\sigma^2$)**:
  $$\sigma^2 = \frac{1}{N - 1} \sum_{i=1}^{N} (x_i - \mu)^2$$
- **Standard Deviation ($\sigma$)**:
  $$\sigma = \sqrt{\sigma^2}$$

### Non-Parametric Metrics (Robust to Skewness):
- **Median ($Q_2$)**: The 50th percentile value separating the lower and upper halves of the sorted data.
- **First Quartile ($Q_1$)**: The 25th percentile value.
- **Third Quartile ($Q_3$)**: The 75th percentile value.
- **Interquartile Range (IQR)**:
  $$\text{IQR} = Q_3 - Q_1$$

---

## 2. Outlier Detection Methodologies

Salary and compensation data frequently exhibit right-skewness and extreme values. Two complementary outlier detection algorithms are implemented:

### A. Interquartile Range (IQR) Rule (Primary Non-Parametric Method)
The IQR method constructs non-parametric fences:
$$\text{Lower Bound} = Q_1 - 1.5 \times \text{IQR}$$
$$\text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}$$

Records with values outside $[\text{Lower Bound}, \text{Upper Bound}]$ are flagged as potential outliers.

### B. Z-Score Method (Parametric Method)
For variables exhibiting approximate normality:
$$Z_i = \frac{x_i - \mu}{\sigma}$$
Values where $|Z_i| > 3.0$ are flagged as statistical outliers.

> **Important Analytical Principle**: Outliers are identified for analytical reporting and distribution comparison, but are **not** automatically deleted from the dataset to preserve true high-compensation market realities.

---

## 3. Correlation Analysis

Linear and monotonic relationships between numerical variables are computed using **Pearson Correlation**:

$$r = \frac{\sum_{i=1}^{N} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{N} (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^{N} (y_i - \bar{y})^2}}$$

Assumptions & Constraints:
- Correlation evaluates association, **not causation**.
- Categorical variables are not artificially ordinalized for Pearson correlation matrices.
