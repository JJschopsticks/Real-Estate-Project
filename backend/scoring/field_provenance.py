"""
Canonical provenance labels for every field that ends up in
data/scored/properties_scored.json.

Three categories:

REAL_OBSERVED     — pulled directly from a listing/Census/ZHVI source, or a
                     deterministic calculation over ONLY such fields (no AI
                     estimate and no other composite score in its inputs).
AI_DERIVED         — a Claude estimate, or any value calculated using one
                     (e.g. gross_yield uses estimated_rent, so it's tainted).
COMPOSITE_DERIVED  — a percentile rank or weighted-sum score computed by
                      score_properties.py (investment_score and everything
                      that feeds it).

Before correlating any two fields for analysis, run them through
backend/scoring/correlation_guard.py with this map — it blocks pairs that
would just measure how the AI prompt or the scoring formula was built,
rather than a real market relationship.
"""

REAL_OBSERVED = "real_observed"
AI_DERIVED = "ai_derived"
COMPOSITE_DERIVED = "composite_derived"

FIELD_PROVENANCE = {
    # ---- Identifiers / raw listing attributes ----
    "id": REAL_OBSERVED,
    "city": REAL_OBSERVED,
    "zip_code": REAL_OBSERVED,
    "bedrooms": REAL_OBSERVED,
    "bathrooms": REAL_OBSERVED,
    "square_feet": REAL_OBSERVED,
    "lot_size": REAL_OBSERVED,
    "year_built": REAL_OBSERVED,
    "listing_price": REAL_OBSERVED,
    "hoa_fee": REAL_OBSERVED,
    "age": REAL_OBSERVED,  # current_year - year_built, no AI involved

    # ---- Census ZIP demographics (real) ----
    "median_income": REAL_OBSERVED,
    "population": REAL_OBSERVED,
    "bachelors_pct": REAL_OBSERVED,
    "poverty_pct": REAL_OBSERVED,
    "owner_occupied_pct": REAL_OBSERVED,
    "median_home_value": REAL_OBSERVED,
    "median_rent": REAL_OBSERVED,

    # ---- ZHVI actual historical appreciation (real) ----
    "actual_zip_appreciation_5yr_pct": REAL_OBSERVED,
    "actual_zip_appreciation_1yr_pct": REAL_OBSERVED,

    # ---- Financing math: deterministic function of listing_price + fixed
    # assumptions (interest rate, loan term) only. No AI, no demographics.
    # NOT SURE / FLAGGED: these aren't "observed" data either — they're
    # calculated. Bucketed as real_observed because they carry none of the
    # AI-prompt or demographic-weighting taint that makes a field circular
    # here. Reclassify if that distinction matters for your analysis.
    "loan_amount": REAL_OBSERVED,
    "monthly_mortgage": REAL_OBSERVED,

    # ---- Claude / LLM estimates ----
    "estimated_rent": AI_DERIVED,
    "confidence_score": AI_DERIVED,
    "ai_estimated_appreciation_pct": AI_DERIVED,
    "estimated_value_5yr": AI_DERIVED,

    # ---- Calculated FROM an AI estimate (still AI-tainted) ----
    "annual_rent": AI_DERIVED,
    "gross_yield": AI_DERIVED,
    "rent_to_price": AI_DERIVED,
    "rent_per_sqft": AI_DERIVED,
    "hoa_ratio": AI_DERIVED,
    "roi_pct": AI_DERIVED,
    "future_equity_gain": AI_DERIVED,
    "city_avg_rent_sqft": AI_DERIVED,
    "rent_advantage": AI_DERIVED,

    # ---- Percentile / composite scores (score_properties.py) ----
    "yield_score": COMPOSITE_DERIVED,
    "rent_price_score": COMPOSITE_DERIVED,
    "rent_sqft_score": COMPOSITE_DERIVED,
    "hoa_score": COMPOSITE_DERIVED,
    "roi_score": COMPOSITE_DERIVED,
    "appreciation_score": COMPOSITE_DERIVED,
    "equity_gain_score": COMPOSITE_DERIVED,
    "home_value_score": COMPOSITE_DERIVED,
    "income_score": COMPOSITE_DERIVED,
    "education_score": COMPOSITE_DERIVED,
    "owner_occ_score": COMPOSITE_DERIVED,
    "poverty_score": COMPOSITE_DERIVED,
    "age_score": COMPOSITE_DERIVED,
    "confidence_rank": COMPOSITE_DERIVED,
    "rent_advantage_score": COMPOSITE_DERIVED,
    "population_score": COMPOSITE_DERIVED,
    "median_rent_score": COMPOSITE_DERIVED,

    "cashflow_score": COMPOSITE_DERIVED,
    "appreciation_total_score": COMPOSITE_DERIVED,
    "neighborhood_score": COMPOSITE_DERIVED,
    "property_quality_score": COMPOSITE_DERIVED,
    "market_score": COMPOSITE_DERIVED,

    "investment_score": COMPOSITE_DERIVED,
    "investment_grade": COMPOSITE_DERIVED,
    "rank": COMPOSITE_DERIVED,
}
