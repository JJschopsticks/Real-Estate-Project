"""
Example non-circular analysis: correlates REAL ZIP demographics
(zip_demographics — US Census) against REAL historical appreciation
(zip_historical_performance — Zillow ZHVI). Neither table is derived from
the other, and neither involves a Claude estimate or a composite score, so
this is the kind of pair backend/scoring/correlation_guard.py allows.

Deliberately does NOT touch ai_estimates or computed_scores — see
backend/db/schema.sql and backend/scoring/field_provenance.py for why those
are kept separate from analysis like this.

Requires backend/analysis/load_to_postgres.py to have been run first
(PostgreSQL service running locally, real_estate_scanner database loaded).
"""

import sys
from pathlib import Path

import psycopg2

ROOT_DIR = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT_DIR / "backend" / "scoring"))
sys.path.insert(0, str(ROOT_DIR / "backend" / "analysis"))

from correlation_guard import assert_valid_correlation_pair  # noqa: E402
from field_provenance import FIELD_PROVENANCE  # noqa: E402
from load_to_postgres import load_env  # noqa: E402

DEMOGRAPHIC_FIELD = "median_income"
APPRECIATION_FIELD = "actual_zip_appreciation_5yr_pct"


def main():
    # Guardrail: raises CircularCorrelationError if this pair were circular.
    # It isn't — both fields are real_observed and neither is an ancestor
    # of the other — so this just documents that the check was done.
    assert_valid_correlation_pair(
        DEMOGRAPHIC_FIELD, APPRECIATION_FIELD, FIELD_PROVENANCE
    )

    conn = psycopg2.connect(**load_env())
    cur = conn.cursor()

    cur.execute(
        f"""
        SELECT zd.{DEMOGRAPHIC_FIELD}, zhp.appreciation_5yr_pct_actual
        FROM zip_demographics zd
        JOIN zip_historical_performance zhp ON zhp.zip_code = zd.zip_code
        WHERE zd.{DEMOGRAPHIC_FIELD} IS NOT NULL
          AND zhp.appreciation_5yr_pct_actual IS NOT NULL
        """
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if len(rows) < 3:
        print(
            f"Only {len(rows)} ZIPs have both fields populated — "
            "not enough to compute a meaningful correlation. Run "
            "zhvi_ingestion.py and load_to_postgres.py first."
        )
        return

    import pandas as pd

    df = pd.DataFrame(rows, columns=[DEMOGRAPHIC_FIELD, APPRECIATION_FIELD])
    correlation = df[DEMOGRAPHIC_FIELD].corr(df[APPRECIATION_FIELD])

    print(f"ZIPs compared: {len(df)}")
    print(
        f"Pearson r between {DEMOGRAPHIC_FIELD} and {APPRECIATION_FIELD}: "
        f"{correlation:.3f}"
    )

    direction = "positive" if correlation > 0 else "negative"
    strength = (
        "strong" if abs(correlation) >= 0.6 else
        "moderate" if abs(correlation) >= 0.3 else
        "weak"
    )

    print(
        f"\nInterpretation: ZIP codes with higher {DEMOGRAPHIC_FIELD} show a "
        f"{strength} {direction} relationship with actual 5-year home value "
        f"appreciation in this dataset. Both sides of this correlation are "
        f"real, observed data (Census + ZHVI) — no AI estimate or composite "
        f"score is involved, so this reflects an actual pattern in the data "
        f"rather than the structure of a formula or a prompt."
    )


if __name__ == "__main__":
    main()
