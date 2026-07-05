import json
import pandas as pd
from datetime import datetime
from pathlib import Path

CURRENT_YEAR = datetime.now().year

# ==================================================
# PATHS
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT_DIR /
    "data" /
    "processed" /
    "properties_with_estimates_readable.json"
)

OUTPUT_FILE = (
    ROOT_DIR /
    "data" /
    "scored" /
    "properties_scored.json"
)

# ==================================================
# INVESTMENT ASSUMPTIONS
# ==================================================

DOWN_PAYMENT_PCT = 0.20

INTEREST_RATE = 0.065
LOAN_TERM_YEARS = 30

PROPERTY_TAX_RATE = 0.0225
INSURANCE_RATE = 0.004

VACANCY_RATE = 0.04
MAINTENANCE_RATE = 0.04
CAPEX_RATE = 0.03
TURNOVER_RATE = 0.01

BUYING_COST_RATE = 0.02
SELLING_COST_RATE = 0.06

# ==================================================
# LOAD
# ==================================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    properties = json.load(f)

df = pd.DataFrame(properties)

df = df.drop_duplicates(subset=["id"])

# ==================================================
# CLEAN
# ==================================================

df["year_built"] = df["year_built"].fillna(1980)

df["square_feet"] = df["square_feet"].fillna(
    df["square_feet"].median()
)

df["hoa_fee"] = df["hoa_fee"].fillna(0)

# ==================================================
# PROPERTY METRICS
# ==================================================

df["annual_rent"] = (
    df["estimated_rent"] * 12
)

df["gross_yield"] = (
    df["annual_rent"] /
    df["listing_price"]
)

df["rent_to_price"] = (
    df["estimated_rent"] /
    df["listing_price"]
)

df["rent_per_sqft"] = (
    df["estimated_rent"] /
    df["square_feet"]
)

df["hoa_ratio"] = (
    (df["hoa_fee"] * 12) /
    df["annual_rent"]
)

df["age"] = (
    CURRENT_YEAR -
    df["year_built"]
)

# ==================================================
# ROI CALCULATIONS
# ==================================================

monthly_rate = INTEREST_RATE / 12
n_payments = LOAN_TERM_YEARS * 12

df["loan_amount"] = (
    df["listing_price"] *
    (1 - DOWN_PAYMENT_PCT)
)

df["monthly_mortgage"] = (
    (
        monthly_rate *
        df["loan_amount"]
    ) /
    (
        1 -
        (1 + monthly_rate)
        ** (-n_payments)
    )
)

annual_property_tax = (
    df["listing_price"] *
    PROPERTY_TAX_RATE
)

annual_insurance = (
    df["listing_price"] *
    INSURANCE_RATE
)

annual_vacancy = (
    df["annual_rent"] *
    VACANCY_RATE
)

annual_maintenance = (
    df["annual_rent"] *
    MAINTENANCE_RATE
)

annual_capex = (
    df["annual_rent"] *
    CAPEX_RATE
)

annual_turnover = (
    df["annual_rent"] *
    TURNOVER_RATE
)

annual_hoa = (
    df["hoa_fee"] * 12
)

annual_mortgage = (
    df["monthly_mortgage"] * 12
)

annual_cashflow = (
    df["annual_rent"]
    - annual_property_tax
    - annual_insurance
    - annual_vacancy
    - annual_maintenance
    - annual_capex
    - annual_turnover
    - annual_hoa
    - annual_mortgage
)

purchase_costs = (
    df["listing_price"] *
    BUYING_COST_RATE
)

selling_costs = (
    df["estimated_value_5yr"] *
    SELLING_COST_RATE
)

df["future_equity_gain"] = (
    df["estimated_value_5yr"]
    - df["listing_price"]
    - purchase_costs
    - selling_costs
)

five_year_profit = (
    annual_cashflow * 5
    +
    df["future_equity_gain"]
)

invested_capital = (
    df["listing_price"] *
    DOWN_PAYMENT_PCT
) + purchase_costs

total_return_multiple = (
    invested_capital +
    five_year_profit
) / invested_capital

total_return_multiple = (
    total_return_multiple.clip(
        lower=0.05
    )
)

df["roi_pct"] = (
    (
        total_return_multiple
        ** (1 / 5)
    ) - 1
) * 100

# ==================================================
# HELPERS
# ==================================================

def percentile_score(series):
    return series.rank(
        pct=True
    ) * 100

def inverse_percentile_score(series):
    return (
        1 -
        series.rank(pct=True)
    ) * 100

# ==================================================
# SCORES
# ==================================================

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

df["roi_score"] = percentile_score(
    df["roi_pct"]
)

df["appreciation_score"] = percentile_score(
    df["five_year_appreciation_pct"]
)

df["equity_gain_score"] = percentile_score(
    df["future_equity_gain"]
)

df["home_value_score"] = percentile_score(
    df["median_home_value"]
)

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

df["age_score"] = inverse_percentile_score(
    df["age"]
)

df["confidence_rank"] = percentile_score(
    df["confidence_score"]
)

city_avg_rent_sqft = (
    df.groupby("city")["rent_per_sqft"]
    .mean()
)

df["city_avg_rent_sqft"] = (
    df["city"]
    .map(city_avg_rent_sqft)
)

df["rent_advantage"] = (
    df["rent_per_sqft"] /
    df["city_avg_rent_sqft"]
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

# ==================================================
# CATEGORY SCORES
# ==================================================

df["cashflow_score"] = (
    df["yield_score"] * 0.40 +
    df["rent_price_score"] * 0.30 +
    df["rent_sqft_score"] * 0.20 +
    df["hoa_score"] * 0.10
)

df["appreciation_total_score"] = (
    df["roi_score"] * 0.35 +
    df["appreciation_score"] * 0.30 +
    df["equity_gain_score"] * 0.25 +
    df["home_value_score"] * 0.10
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

# ==================================================
# FINAL SCORE
# ==================================================

df["investment_score"] = (
    df["roi_score"] * 0.20 +
    df["cashflow_score"] * 0.25 +
    df["appreciation_total_score"] * 0.20 +
    df["neighborhood_score"] * 0.20 +
    df["property_quality_score"] * 0.10 +
    df["market_score"] * 0.05
)

# ==================================================
# SORT
# ==================================================

df = df.sort_values(
    by="investment_score",
    ascending=False
)

df["rank"] = range(
    1,
    len(df) + 1
)

# ==================================================
# GRADE
# ==================================================

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
    return "D"

df["investment_grade"] = df[
    "investment_score"
].apply(grade)

# ==================================================
# ROUND
# ==================================================

for col in [
    "roi_pct",
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

# ==================================================
# SAVE
# ==================================================

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

print(
    df[
        [
            "rank",
            "city",
            "listing_price",
            "roi_pct",
            "investment_score",
            "investment_grade"
        ]
    ].head(20)
)