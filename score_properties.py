import json
import pandas as pd
from datetime import datetime

CURRENT_YEAR = datetime.now().year

INPUT_FILE = "properties_with_estimates_readable.json"
OUTPUT_FILE = "properties_scored.json"

# --------------------------------------------------
# LOAD
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    properties = json.load(f)

df = pd.DataFrame(properties)

df = df.drop_duplicates(subset=["id"])

# --------------------------------------------------
# CLEAN
# --------------------------------------------------

df["year_built"] = df["year_built"].fillna(1980)
df["square_feet"] = df["square_feet"].fillna(
    df["square_feet"].median()
)

df["hoa_fee"] = df["hoa_fee"].fillna(0)

# --------------------------------------------------
# RAW METRICS
# --------------------------------------------------

df["annual_rent"] = (
    df["estimated_rent"] * 12
)

df["gross_yield"] = (
    df["annual_rent"]
    / df["listing_price"]
)

df["rent_to_price"] = (
    df["estimated_rent"]
    / df["listing_price"]
)

df["rent_per_sqft"] = (
    df["estimated_rent"]
    / df["square_feet"]
)

df["hoa_ratio"] = (
    (df["hoa_fee"] * 12)
    / df["annual_rent"]
)

df["future_equity_gain"] = (
    df["estimated_value_5yr"]
    - df["listing_price"]
)

df["age"] = (
    CURRENT_YEAR
    - df["year_built"]
)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def percentile_score(series):
    return series.rank(pct=True) * 100

def inverse_percentile_score(series):
    return (1 - series.rank(pct=True)) * 100

# --------------------------------------------------
# PROPERTY SCORES
# --------------------------------------------------

df["yield_score"] = percentile_score(
    df["gross_yield"]
)

df["rent_price_score"] = percentile_score(
    df["rent_to_price"]
)

df["rent_sqft_score"] = percentile_score(
    df["rent_per_sqft"]
)

df["hoa_score"] = inverse_percentile_score(
    df["hoa_ratio"]
)

df["age_score"] = inverse_percentile_score(
    df["age"]
)

df["confidence_rank"] = percentile_score(
    df["confidence_score"]
)

# --------------------------------------------------
# APPRECIATION
# --------------------------------------------------

df["appreciation_score"] = percentile_score(
    df["five_year_appreciation_pct"]
)

df["equity_gain_score"] = percentile_score(
    df["future_equity_gain"]
)

df["home_value_score"] = percentile_score(
    df["median_home_value"]
)

# --------------------------------------------------
# NEIGHBORHOOD
# --------------------------------------------------

df["income_score"] = percentile_score(
    df["median_income"]
)

df["education_score"] = percentile_score(
    df["bachelors_pct"]
)

df["owner_occ_score"] = percentile_score(
    df["owner_occupied_pct"]
)

df["poverty_score"] = inverse_percentile_score(
    df["poverty_pct"]
)

# --------------------------------------------------
# MARKET
# --------------------------------------------------

city_rent_sqft = (
    df.groupby("city")["rent_per_sqft"]
    .mean()
)

df["city_avg_rent_sqft"] = (
    df["city"]
    .map(city_rent_sqft)
)

df["rent_advantage"] = (
    df["rent_per_sqft"]
    / df["city_avg_rent_sqft"]
)

df["rent_advantage_score"] = percentile_score(
    df["rent_advantage"]
)

df["population_score"] = percentile_score(
    df["population"]
)

df["median_rent_score"] = percentile_score(
    df["median_rent"]
)

# --------------------------------------------------
# CATEGORY SCORES
# --------------------------------------------------

df["cashflow_score"] = (
    df["yield_score"] * 0.40 +
    df["rent_price_score"] * 0.30 +
    df["rent_sqft_score"] * 0.20 +
    df["hoa_score"] * 0.10
)

df["appreciation_total_score"] = (
    df["appreciation_score"] * 0.50 +
    df["equity_gain_score"] * 0.30 +
    df["home_value_score"] * 0.20
)

df["neighborhood_score"] = (
    df["income_score"] * 0.30 +
    df["education_score"] * 0.25 +
    df["owner_occ_score"] * 0.25 +
    df["poverty_score"] * 0.20
)

df["property_quality_score"] = (
    df["age_score"] * 0.40 +
    df["confidence_rank"] * 0.60
)

df["market_score"] = (
    df["rent_advantage_score"] * 0.40 +
    df["population_score"] * 0.20 +
    df["median_rent_score"] * 0.40
)

# --------------------------------------------------
# FINAL SCORE
# --------------------------------------------------

df["investment_score"] = (
    df["cashflow_score"] * 0.35 +
    df["appreciation_total_score"] * 0.25 +
    df["neighborhood_score"] * 0.20 +
    df["property_quality_score"] * 0.10 +
    df["market_score"] * 0.10
)

# --------------------------------------------------
# RANK
# --------------------------------------------------

df = df.sort_values(
    by="investment_score",
    ascending=False
)

df["rank"] = range(
    1,
    len(df) + 1
)

# --------------------------------------------------
# GRADE
# --------------------------------------------------

def grade(score):

    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    else:
        return "D"

df["investment_grade"] = (
    df["investment_score"]
    .apply(grade)
)

# --------------------------------------------------
# ROUND
# --------------------------------------------------

for col in [
    "gross_yield",
    "future_equity_gain",
    "cashflow_score",
    "appreciation_total_score",
    "neighborhood_score",
    "property_quality_score",
    "market_score",
    "investment_score"
]:
    df[col] = df[col].round(2)

# --------------------------------------------------
# SAVE
# --------------------------------------------------

results = df.to_dict(
    orient="records"
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        results,
        f,
        indent=2
    )

print(f"\nSaved: {OUTPUT_FILE}")

print("\nTOP 10 PROPERTIES\n")

print(
    df[
        [
            "rank",
            "city",
            "listing_price",
            "investment_score",
            "cashflow_score",
            "appreciation_total_score",
            "neighborhood_score",
            "market_score",
            "investment_grade"
        ]
    ].head(10)
)