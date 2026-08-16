"""
Geographic location analysis module for Job Market Analytics.
"""

from typing import Any, Dict
import pandas as pd


def analyze_locations(df: pd.DataFrame, top_n: int = 15) -> Dict[str, Any]:
    """
    Calculate geographic posting concentrations across cities, states, and countries.
    """
    if df.empty:
        return {
            "top_cities": [],
            "top_states": [],
            "top_countries": [],
            "remote_by_location": [],
        }

    total = len(df)

    def _get_top(col: str) -> pd.DataFrame:
        if col not in df.columns:
            return pd.DataFrame(columns=[col, "count", "percentage"])
        series = df[col].dropna().astype(str).str.strip()
        series = series[~series.isin(["", "nan", "None", "Unknown"])]
        if series.empty:
            return pd.DataFrame(columns=[col, "count", "percentage"])
        c = series.value_counts().head(top_n).reset_index()
        c.columns = [col, "count"]
        c["percentage"] = (c["count"] / total * 100.0).round(2)
        return c

    cities_df = _get_top("city")
    states_df = _get_top("state")
    countries_df = _get_top("country")

    # Remote breakdown for top 10 cities
    remote_by_loc = []
    if "city" in df.columns and "remote_type" in df.columns:
        top_city_names = cities_df["city"].head(10).tolist()
        city_df = df[df["city"].isin(top_city_names)]
        if not city_df.empty:
            ct = pd.crosstab(city_df["city"], city_df["remote_type"]).reset_index()
            remote_by_loc = ct.to_dict(orient="records")

    return {
        "top_cities": cities_df.to_dict(orient="records"),
        "top_states": states_df.to_dict(orient="records"),
        "top_countries": countries_df.to_dict(orient="records"),
        "remote_by_location": remote_by_loc,
    }
