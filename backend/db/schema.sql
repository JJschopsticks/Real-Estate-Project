-- =====================================================================
-- RealEstateScanner analysis schema (PostgreSQL)
--
-- Runs against the local PostgreSQL instance (see .env for connection
-- details) so Power BI's native PostgreSQL connector can query it
-- directly -- no ODBC driver or CSV export needed.
--
-- Five tables, split strictly by provenance so a SQL join always makes it
-- obvious whether a field is real/observed data, an AI (Claude) estimate,
-- or a composite score derived from other fields. See
-- backend/scoring/field_provenance.py for the field-level version of this
-- same split, and backend/scoring/correlation_guard.py for a guard that
-- enforces it in analysis code.
--
-- Rule of thumb for analysis / correlation work:
--   OK:      zip_demographics  <-> zip_historical_performance  (real vs real)
--   CIRCULAR: anything <-> ai_estimates, or anything <-> computed_scores
--             where one side feeds the other (which is most of them)
--
-- The app/dashboard is free to join all five tables (see v_dashboard_properties
-- below) — this restriction only applies to statistical/correlation analysis.
-- =====================================================================

-- ---------------------------------------------------------------------
-- raw_properties: listing data only. Real, observed. No estimates, no
-- scores. Mirrors backend/collection/rentcast_data.py's PROPERTY_SCHEMA.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_properties (
    id                  TEXT PRIMARY KEY,
    address             TEXT,
    city                TEXT,
    state               TEXT,
    zip_code            TEXT NOT NULL,
    county              TEXT,
    latitude            REAL,
    longitude           REAL,
    property_type       TEXT,
    bedrooms            REAL,
    bathrooms           REAL,
    square_feet         REAL,
    lot_size            REAL,
    year_built          REAL,
    listing_price       REAL,
    last_sale_price     REAL,
    last_sale_date      TEXT,
    hoa_fee             REAL DEFAULT 0,
    garage_spaces       INTEGER DEFAULT 0,
    pool                BOOLEAN DEFAULT FALSE,
    fireplace           BOOLEAN DEFAULT FALSE,
    heating             BOOLEAN DEFAULT FALSE,
    cooling             BOOLEAN DEFAULT FALSE
);

-- ---------------------------------------------------------------------
-- zip_demographics: US Census ACS 5-Year data only. Real, observed.
-- Populated by backend/enrichment/census_enrichment.py.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS zip_demographics (
    zip_code            TEXT PRIMARY KEY,
    median_income        REAL,
    population           REAL,
    bachelors_pct         REAL,
    poverty_pct           REAL,
    owner_occupied_pct    REAL,
    median_home_value     REAL,
    median_rent           REAL,
    source               TEXT DEFAULT 'US Census ACS 5-Year',
    vintage_year          INTEGER
);

-- ---------------------------------------------------------------------
-- zip_historical_performance: Zillow ZHVI actual appreciation. Real,
-- observed history — NOT a model estimate. Populated by
-- backend/enrichment/zhvi_ingestion.py.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS zip_historical_performance (
    zip_code                        TEXT PRIMARY KEY,
    home_value_current              REAL,
    home_value_5yr_ago              REAL,
    home_value_1yr_ago              REAL,
    appreciation_5yr_pct_actual     REAL,
    appreciation_1yr_pct_actual     REAL,
    data_as_of_date                 TEXT,
    source                          TEXT DEFAULT 'Zillow ZHVI (files.zillowstatic.com)'
);

-- ---------------------------------------------------------------------
-- ai_estimates: Claude-generated rent / appreciation / value. Model
-- output, explicitly conditioned on zip_demographics in the prompt
-- (backend/ai/claude_estimates.py). NOT real/observed data — do not
-- correlate these against zip_demographics or zip_historical_performance
-- and call it a market finding.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_estimates (
    property_id                    TEXT PRIMARY KEY REFERENCES raw_properties(id),
    estimated_rent                  REAL,
    confidence_score                REAL,
    ai_estimated_appreciation_pct   REAL,
    estimated_value_5yr             REAL,
    model_name                      TEXT,
    generated_at                    TEXT
);

-- ---------------------------------------------------------------------
-- computed_scores: investment_score and every sub-score, all
-- derived/composite (percentile ranks and weighted sums built from
-- ai_estimates + zip_demographics). Populated by
-- backend/scoring/score_properties.py. Never correlate a column in this
-- table against a field that is one of its own weighted inputs — see
-- backend/scoring/correlation_guard.py.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS computed_scores (
    property_id                    TEXT PRIMARY KEY REFERENCES raw_properties(id),
    roi_pct                         REAL,
    gross_yield                     REAL,
    future_equity_gain              REAL,
    yield_score                     REAL,
    rent_price_score                 REAL,
    rent_sqft_score                  REAL,
    hoa_score                       REAL,
    roi_score                       REAL,
    appreciation_score               REAL,
    equity_gain_score                REAL,
    home_value_score                 REAL,
    income_score                    REAL,
    education_score                  REAL,
    owner_occ_score                  REAL,
    poverty_score                   REAL,
    age_score                       REAL,
    confidence_rank                  REAL,
    rent_advantage_score             REAL,
    population_score                 REAL,
    median_rent_score                REAL,
    cashflow_score                   REAL,
    appreciation_total_score         REAL,
    neighborhood_score               REAL,
    property_quality_score           REAL,
    market_score                    REAL,
    investment_score                 REAL,
    investment_grade                 TEXT,
    rank                            INTEGER
);

-- ---------------------------------------------------------------------
-- Convenience view for the app/dashboard ONLY. It joins across all five
-- provenance tables on purpose — that's fine for the product UI, which
-- needs everything in one place. Do not use this view as the source for
-- correlation/statistical analysis; query the individual tables instead
-- so the provenance boundary stays visible.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_dashboard_properties AS
SELECT
    rp.*,
    zd.median_income, zd.population, zd.bachelors_pct, zd.poverty_pct,
    zd.owner_occupied_pct, zd.median_home_value, zd.median_rent,
    zhp.appreciation_5yr_pct_actual AS actual_zip_appreciation_5yr_pct,
    zhp.appreciation_1yr_pct_actual AS actual_zip_appreciation_1yr_pct,
    ai.estimated_rent, ai.confidence_score,
    ai.ai_estimated_appreciation_pct, ai.estimated_value_5yr,
    cs.roi_pct, cs.investment_score, cs.investment_grade, cs.rank
FROM raw_properties rp
LEFT JOIN zip_demographics zd ON zd.zip_code = rp.zip_code
LEFT JOIN zip_historical_performance zhp ON zhp.zip_code = rp.zip_code
LEFT JOIN ai_estimates ai ON ai.property_id = rp.id
LEFT JOIN computed_scores cs ON cs.property_id = rp.id;
