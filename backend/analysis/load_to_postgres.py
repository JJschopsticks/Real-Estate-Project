"""
Loads the existing pipeline JSON outputs into the local PostgreSQL database
(real_estate_scanner) that matches backend/db/schema.sql — split into
raw_properties, zip_demographics, zip_historical_performance, ai_estimates,
and computed_scores.

This is the database Power BI connects to natively (Get Data > PostgreSQL
database) — no ODBC driver or CSV export needed. See backend/db/schema.sql
for the table definitions and backend/scoring/field_provenance.py for what
belongs in which table.

Doesn't hit any external API; it just reloads files the pipeline
(rentcast_data.py -> census_enrichment.py -> zhvi_ingestion.py ->
claude_estimates.py -> score_properties.py) already produced on disk.

Requires the PostgreSQL service to be running and POSTGRES_* vars in .env
(see load_env() below).
"""

import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]

RAW_PROPERTIES_FILE = ROOT_DIR / "data" / "raw" / "dfw_properties.json"
ZIP_DEMOGRAPHICS_FILE = ROOT_DIR / "data" / "processed" / "zip_metrics.json"
ZIP_HISTORICAL_FILE = (
    ROOT_DIR / "data" / "processed" / "zip_historical_appreciation.json"
)
SCORED_PROPERTIES_FILE = (
    ROOT_DIR / "data" / "scored" / "properties_scored.json"
)

SCHEMA_FILE = ROOT_DIR / "backend" / "db" / "schema.sql"

TABLES_IN_LOAD_ORDER = [
    "computed_scores",
    "ai_estimates",
    "zip_historical_performance",
    "zip_demographics",
    "raw_properties",
]

AI_ESTIMATE_FIELDS = [
    "estimated_rent",
    "confidence_score",
    "ai_estimated_appreciation_pct",
    "estimated_value_5yr",
]

COMPUTED_SCORE_FIELDS = [
    "roi_pct", "gross_yield", "future_equity_gain",
    "yield_score", "rent_price_score", "rent_sqft_score", "hoa_score",
    "roi_score", "appreciation_score", "equity_gain_score",
    "home_value_score", "income_score", "education_score",
    "owner_occ_score", "poverty_score", "age_score", "confidence_rank",
    "rent_advantage_score", "population_score", "median_rent_score",
    "cashflow_score", "appreciation_total_score", "neighborhood_score",
    "property_quality_score", "market_score", "investment_score",
    "investment_grade", "rank",
]


def load_env():
    load_dotenv(ROOT_DIR / ".env")

    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "dbname": os.getenv("POSTGRES_DB", "real_estate_scanner"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }


def load_json(path):
    if not path.exists():
        print(f"WARNING: {path} not found — skipping.")
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_database():
    conn = psycopg2.connect(**load_env())
    cur = conn.cursor()

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        cur.execute(f.read())

    for table in TABLES_IN_LOAD_ORDER:
        cur.execute(f"TRUNCATE TABLE {table} CASCADE")

    # ---- raw_properties ----
    raw = load_json(RAW_PROPERTIES_FILE)
    if raw:
        properties = raw.get("properties", raw) if isinstance(raw, dict) else raw

        rows = [
            (
                p.get("id"), p.get("address"), p.get("city"), p.get("state"),
                str(p.get("zip_code", "")).strip(), p.get("county"),
                p.get("latitude"), p.get("longitude"), p.get("property_type"),
                p.get("bedrooms"), p.get("bathrooms"), p.get("square_feet"),
                p.get("lot_size"), p.get("year_built"), p.get("listing_price"),
                p.get("last_sale_price"), p.get("last_sale_date"),
                p.get("hoa_fee", 0), p.get("garage_spaces", 0),
                bool(p.get("pool")), bool(p.get("fireplace")),
                bool(p.get("heating")), bool(p.get("cooling")),
            )
            for p in properties
        ]

        cur.executemany(
            """
            INSERT INTO raw_properties (
                id, address, city, state, zip_code, county, latitude,
                longitude, property_type, bedrooms, bathrooms, square_feet,
                lot_size, year_built, listing_price, last_sale_price,
                last_sale_date, hoa_fee, garage_spaces, pool, fireplace,
                heating, cooling
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            rows,
        )
        print(f"Loaded {len(rows)} rows into raw_properties")

    # ---- zip_demographics ----
    demographics = load_json(ZIP_DEMOGRAPHICS_FILE)
    if demographics:
        rows = [
            (
                zip_code, m.get("median_income"), m.get("population"),
                m.get("bachelors_pct"), m.get("poverty_pct"),
                m.get("owner_occupied_pct"), m.get("median_home_value"),
                m.get("median_rent"),
            )
            for zip_code, m in demographics.items()
        ]

        cur.executemany(
            """
            INSERT INTO zip_demographics (
                zip_code, median_income, population, bachelors_pct,
                poverty_pct, owner_occupied_pct, median_home_value,
                median_rent
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            rows,
        )
        print(f"Loaded {len(rows)} rows into zip_demographics")

    # ---- zip_historical_performance ----
    historical = load_json(ZIP_HISTORICAL_FILE)
    if historical:
        rows = [
            (
                zip_code, m.get("home_value_current"),
                m.get("home_value_5yr_ago"), m.get("home_value_1yr_ago"),
                m.get("appreciation_5yr_pct_actual"),
                m.get("appreciation_1yr_pct_actual"),
                m.get("data_as_of"),
            )
            for zip_code, m in historical.items()
        ]

        cur.executemany(
            """
            INSERT INTO zip_historical_performance (
                zip_code, home_value_current, home_value_5yr_ago,
                home_value_1yr_ago, appreciation_5yr_pct_actual,
                appreciation_1yr_pct_actual, data_as_of_date
            ) VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            rows,
        )
        print(f"Loaded {len(rows)} rows into zip_historical_performance")

    # ---- ai_estimates + computed_scores ----
    scored = load_json(SCORED_PROPERTIES_FILE)
    if scored:
        ai_rows = [
            (p.get("id"), *(p.get(f) for f in AI_ESTIMATE_FIELDS))
            for p in scored
        ]
        cur.executemany(
            f"""
            INSERT INTO ai_estimates (
                property_id, {", ".join(AI_ESTIMATE_FIELDS)}
            ) VALUES ({", ".join(["%s"] * (len(AI_ESTIMATE_FIELDS) + 1))})
            """,
            ai_rows,
        )
        print(f"Loaded {len(ai_rows)} rows into ai_estimates")

        score_rows = [
            (p.get("id"), *(p.get(f) for f in COMPUTED_SCORE_FIELDS))
            for p in scored
        ]
        cur.executemany(
            f"""
            INSERT INTO computed_scores (
                property_id, {", ".join(COMPUTED_SCORE_FIELDS)}
            ) VALUES ({", ".join(["%s"] * (len(COMPUTED_SCORE_FIELDS) + 1))})
            """,
            score_rows,
        )
        print(f"Loaded {len(score_rows)} rows into computed_scores")

    conn.commit()
    cur.close()
    conn.close()

    print("\nLoaded into PostgreSQL database: real_estate_scanner")


if __name__ == "__main__":
    build_database()
