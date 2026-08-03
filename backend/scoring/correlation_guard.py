"""
Guardrail against circular correlation analysis.

score_properties.py builds investment_score as a weighted sum of sub-scores
that are themselves weighted sums of fields like median_income and
poverty_pct. Correlating investment_score against those same demographic
inputs doesn't measure a market relationship — it just re-derives the
weights already baked into the formula. Same problem, one level removed,
for anything computed from a Claude estimate (see FIELD_PROVENANCE in
field_provenance.py): estimated_rent and ai_estimated_appreciation_pct were
produced by a prompt that was explicitly told to factor in demographics, so
roi_pct or appreciation_score correlated against those demographics mostly
tells you whether the LLM followed instructions.

assert_valid_correlation_pair() raises CircularCorrelationError when either
of those situations applies. It does NOT block real-vs-real pairs (e.g.
median_income vs. actual_zip_appreciation_5yr_pct) — that's the whole point.
"""

from field_provenance import (
    AI_DERIVED,
    COMPOSITE_DERIVED,
    FIELD_PROVENANCE,
)

# Direct inputs to each derived field, mirroring the formulas in
# score_properties.py. Keep this in sync if those formulas change — it's
# what lets the guard catch indirect/transitive circularity, not just
# same-category pairs.
DIRECT_COMPONENTS = {
    # single-field percentile scores -> underlying field
    "yield_score": {"gross_yield"},
    "rent_price_score": {"rent_to_price"},
    "rent_sqft_score": {"rent_per_sqft"},
    "hoa_score": {"hoa_ratio"},
    "roi_score": {"roi_pct"},
    "appreciation_score": {"ai_estimated_appreciation_pct"},
    "equity_gain_score": {"future_equity_gain"},
    "home_value_score": {"median_home_value"},
    "income_score": {"median_income"},
    "education_score": {"bachelors_pct"},
    "owner_occ_score": {"owner_occupied_pct"},
    "poverty_score": {"poverty_pct"},
    "age_score": {"age"},
    "confidence_rank": {"confidence_score"},
    "rent_advantage_score": {"rent_advantage"},
    "population_score": {"population"},
    "median_rent_score": {"median_rent"},

    # intermediate calculated fields -> their raw inputs
    "age": {"year_built"},
    "loan_amount": {"listing_price"},
    "monthly_mortgage": {"loan_amount"},
    "annual_rent": {"estimated_rent"},
    "gross_yield": {"annual_rent", "listing_price"},
    "rent_to_price": {"estimated_rent", "listing_price"},
    "rent_per_sqft": {"estimated_rent", "square_feet"},
    "hoa_ratio": {"hoa_fee", "annual_rent"},
    "future_equity_gain": {"estimated_value_5yr", "listing_price"},
    "roi_pct": {
        "annual_rent", "future_equity_gain",
        "loan_amount", "monthly_mortgage", "hoa_fee",
    },
    "city_avg_rent_sqft": {"rent_per_sqft", "city"},
    "rent_advantage": {"rent_per_sqft", "city_avg_rent_sqft"},

    # category (weighted-sum) scores -> their direct sub-scores
    "cashflow_score": {
        "yield_score", "rent_price_score", "rent_sqft_score", "hoa_score",
    },
    "appreciation_total_score": {
        "roi_score", "appreciation_score", "equity_gain_score",
        "home_value_score",
    },
    "neighborhood_score": {
        "income_score", "education_score", "owner_occ_score",
        "poverty_score",
    },
    "property_quality_score": {"age_score", "confidence_rank"},
    "market_score": {
        "rent_advantage_score", "population_score", "median_rent_score",
    },

    # final composite
    "investment_score": {
        "roi_score", "cashflow_score", "appreciation_total_score",
        "neighborhood_score", "property_quality_score", "market_score",
    },

    # bucketed / ordered from the final composite
    "investment_grade": {"investment_score"},
    "rank": {"investment_score"},
}


class CircularCorrelationError(ValueError):
    pass


def _transitive_ancestry(field, seen=None):
    """All fields that field is directly or indirectly computed from."""

    if seen is None:
        seen = set()

    for parent in DIRECT_COMPONENTS.get(field, ()):
        if parent not in seen:
            seen.add(parent)
            _transitive_ancestry(parent, seen)

    return seen


def assert_valid_correlation_pair(field_a, field_b, provenance_map=FIELD_PROVENANCE):
    """Raises CircularCorrelationError if correlating field_a against
    field_b would be circular. Returns True otherwise."""

    if field_a == field_b:
        raise CircularCorrelationError(
            f"'{field_a}' correlated against itself."
        )

    for field in (field_a, field_b):
        if field not in provenance_map:
            raise ValueError(
                f"'{field}' is not in provenance_map — add it to "
                "FIELD_PROVENANCE before correlating it."
            )

    category_a = provenance_map[field_a]
    category_b = provenance_map[field_b]

    if category_a == category_b and category_a in (AI_DERIVED, COMPOSITE_DERIVED):
        raise CircularCorrelationError(
            f"'{field_a}' and '{field_b}' are both '{category_a}' fields — "
            "this measures how the AI prompt or scoring formula was built, "
            "not a market relationship."
        )

    ancestry_a = _transitive_ancestry(field_a)
    ancestry_b = _transitive_ancestry(field_b)

    if field_b in ancestry_a:
        raise CircularCorrelationError(
            f"'{field_b}' is a direct or indirect component of '{field_a}' "
            "— circular by construction."
        )

    if field_a in ancestry_b:
        raise CircularCorrelationError(
            f"'{field_a}' is a direct or indirect component of '{field_b}' "
            "— circular by construction."
        )

    return True
