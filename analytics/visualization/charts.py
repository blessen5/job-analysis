"""
Analytical charts module for Job Market Analytics EDA.

Generates publication-ready visualizations:
- Remote work distribution pie chart
- Employment type bar chart
- Top job titles horizontal bar chart
- Top companies vertical bar chart
- Geographic postings horizontal bar chart
- Experience level breakdown bar chart
- Salary distribution histogram & box plots
- Correlation matrix heatmap
"""

from pathlib import Path
from typing import List, Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from analytics.visualization.save import configure_plot_style, save_chart


def generate_all_eda_charts(df: pd.DataFrame, output_dir: Path) -> List[Path]:
    """
    Generate all EDA charts and save them into output_dir.
    """
    configure_plot_style()
    output_dir.mkdir(parents=True, exist_ok=True)
    chart_paths = []

    if df.empty:
        return chart_paths

    # 1. Remote Work Distribution Chart
    if "remote_type" in df.columns:
        fig, ax = plt.subplots(figsize=(7, 5))
        counts = df["remote_type"].value_counts()
        colors = ["#2ecc71", "#3498db", "#e74c3c", "#95a5a6"]
        ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=140, colors=colors[:len(counts)])
        ax.set_title("Work Modality Distribution (Remote vs Onsite vs Hybrid)")
        chart_paths.append(save_chart(fig, output_dir / "remote_work_distribution.png"))

    # 2. Employment Type Distribution Chart
    if "employment_type" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        counts = df["employment_type"].value_counts()
        sns.barplot(x=counts.index, y=counts.values, palette="Blues_r", ax=ax)
        ax.set_title("Job Postings by Employment Contract Type")
        ax.set_xlabel("Employment Type")
        ax.set_ylabel("Posting Count")
        for p in ax.patches:
            ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', xytext=(0, 3), textcoords='offset points', fontweight='bold')
        chart_paths.append(save_chart(fig, output_dir / "employment_type_distribution.png"))

    # 3. Top 15 Job Titles
    if "job_title" in df.columns:
        titles = df["job_title"].dropna().astype(str).str.strip()
        titles = titles[titles != "Unknown"]
        if not titles.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            top_titles = titles.value_counts().head(15)
            sns.barplot(x=top_titles.values, y=top_titles.index, palette="viridis", ax=ax)
            ax.set_title("Top 15 Most Frequently Advertised Job Titles")
            ax.set_xlabel("Posting Count")
            ax.set_ylabel("Job Title")
            chart_paths.append(save_chart(fig, output_dir / "top_job_titles.png"))

    # 4. Top 15 Companies
    if "company" in df.columns:
        companies = df["company"].dropna().astype(str).str.strip()
        companies = companies[~companies.isin(["", "nan", "None", "Unknown"])]
        if not companies.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            top_comp = companies.value_counts().head(15)
            sns.barplot(x=top_comp.values, y=top_comp.index, palette="mako", ax=ax)
            ax.set_title("Top 15 Hiring Organizations by Posting Count")
            ax.set_xlabel("Posting Count")
            ax.set_ylabel("Company Name")
            chart_paths.append(save_chart(fig, output_dir / "top_companies.png"))

    # 5. Top 15 Locations
    if "city" in df.columns:
        cities = df["city"].dropna().astype(str).str.strip()
        cities = cities[~cities.isin(["", "nan", "None", "Unknown"])]
        if not cities.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            top_cities = cities.value_counts().head(15)
            sns.barplot(x=top_cities.values, y=top_cities.index, palette="rocket", ax=ax)
            ax.set_title("Top 15 Geographic Posting Locations (Cities)")
            ax.set_xlabel("Posting Count")
            ax.set_ylabel("City")
            chart_paths.append(save_chart(fig, output_dir / "top_locations.png"))

    # 6. Experience Level Breakdown
    if "experience_level" in df.columns:
        exp_levels = df["experience_level"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(x=exp_levels.index, y=exp_levels.values, palette="cubehelix", ax=ax)
        ax.set_title("Job Postings by Experience Level Classification")
        ax.set_xlabel("Experience Level")
        ax.set_ylabel("Posting Count")
        for p in ax.patches:
            ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', xytext=(0, 3), textcoords='offset points', fontweight='bold')
        chart_paths.append(save_chart(fig, output_dir / "experience_distribution.png"))

    # 7. Salary Histogram and KDE
    sal_col = "salary_midpoint" if "salary_midpoint" in df.columns and df["salary_midpoint"].notna().any() else "salary_min"
    if sal_col in df.columns:
        sal_data = pd.to_numeric(df[sal_col], errors="coerce").dropna()
        if not sal_data.empty and len(sal_data) > 1:
            fig, ax = plt.subplots(figsize=(9, 5))
            sns.histplot(sal_data, kde=True, color="#2980b9", bins=20, ax=ax)
            ax.set_title(f"Salary Distribution Histogram & Kernel Density Estimation ({sal_col})")
            ax.set_xlabel("Salary Amount")
            ax.set_ylabel("Frequency")
            chart_paths.append(save_chart(fig, output_dir / "salary_histogram.png"))

            # Salary Box Plot by Experience Level
            if "experience_level" in df.columns:
                sal_exp_df = df[[sal_col, "experience_level"]].dropna()
                sal_exp_df[sal_col] = pd.to_numeric(sal_exp_df[sal_col], errors="coerce")
                sal_exp_df = sal_exp_df[sal_exp_df["experience_level"] != "Unknown"].dropna()
                if not sal_exp_df.empty:
                    fig, ax = plt.subplots(figsize=(9, 5))
                    sns.boxplot(data=sal_exp_df, x="experience_level", y=sal_col, palette="Set2", ax=ax)
                    ax.set_title("Salary Distribution by Experience Level")
                    ax.set_xlabel("Experience Level")
                    ax.set_ylabel("Salary Amount")
                    chart_paths.append(save_chart(fig, output_dir / "salary_box_experience.png"))

    # 8. Numeric Correlation Matrix Heatmap
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Filter out year/month/day derived date fields for pure metric correlations
    corr_cols = [c for c in num_cols if c not in ["posted_year", "posted_month", "posted_day"]]
    if len(corr_cols) >= 2:
        corr_df = df[corr_cols].dropna()
        if len(corr_df) >= 3:
            fig, ax = plt.subplots(figsize=(8, 6))
            corr_mat = corr_df.corr(method="pearson")
            sns.heatmap(corr_mat, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
            ax.set_title("Pearson Correlation Heatmap (Numeric Metrics)")
            chart_paths.append(save_chart(fig, output_dir / "correlation_heatmap.png"))

    return chart_paths
