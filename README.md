# Real Estate Investment Scanner

An end-to-end data pipeline and analytics project for evaluating investment
properties in the Dallas-Fort Worth (DFW) metro area. The pipeline collects
active listings, enriches them with real Census demographic data and Zillow
historical home-value data, uses Claude to generate rent/appreciation
estimates, and scores every property on a weighted investment model all
served through a React dashboard and a PostgreSQL + Power BI analytics layer
for deeper market analysis.

Beyond the pipeline itself, this project involved auditing the data for
circular/misleading relationships (e.g., correlating AI-estimated appreciation
against the same demographics used to generate it) and correcting them by
separating the schema strictly by data provenance and bringing in independent,
real historical performance data (Zillow ZHVI) see **Key Findings** and
**Data Integrity** below.

<img width="2832" height="1466" alt="RealEstateDashboard" src="https://github.com/user-attachments/assets/eec8e6a7-5c4d-43aa-aad1-3f45616a48f0" />
<img width="2796" height="1022" alt="RealEstateGraphs" src="https://github.com/user-attachments/assets/75cbd530-7dab-4d94-8386-a80722900423" />

## Key Findings

- **Income is a weak predictor of appreciation.** Across DFW ZIP codes, median
  income and 5-year home value appreciation show only a weak-to-moderate
  positive relationship. Notably, ZIPs 76109, 75038, and 75039 substantially
  outperformed the metro-wide appreciation average despite below-average
  income suggesting these areas may be under-priced relative to their
  growth trajectory. Conversely, the highest-income ZIP in the dataset
  (76226) appreciated only at the metro average, showing that high income
  does not guarantee outperformance.

- **Composite investment scores and raw ROI frequently disagree.** The
  top-ranked property by AI-generated investment score had below-median ROI,
  while one of the highest-ROI properties in the dataset scored only
  moderately overall. This reflects the scoring model's design it
  balances ROI against appreciation, cashflow, and neighborhood quality
  and highlights why "best overall investment" and "best cash return" are
  different questions that can point to different properties.

- **Grade distribution skews low, consistent with composite-score math.**
  ~45% of properties fall into the lowest ("D") grade tier, with very few
  reaching A-tier. This reflects the statistical effect of averaging several
  independent sub-scores it becomes increasingly unlikely for any single
  property to score well across all of them simultaneously.

- **Quality clusters geographically.** Higher-tier properties visibly
  concentrate around Frisco, The Colony, and McKinney rather than
  distributing evenly across the metro.

## Data Integrity Note

Appreciation and rent estimates are AI-generated and explicitly conditioned
on neighborhood demographics, so they can't be validated against those same
demographics without circularity. Real historical appreciation (Zillow ZHVI)
was integrated as independent ground truth, and the schema separates
observed data, AI estimates, and composite scores into distinct tables to
keep this boundary explicit for any future analysis.

# How it works

The pipeline runs in a few stages:

1. Collection (backend/collection/) — Pulls active for-sale listings across DFW cities from the RentCast API.
2. Enrichment (backend/enrichment/) — Attaches ZIP-code-level demographic data (median income, education, poverty rate, home values, etc.) from the U.S. Census Bureau's ACS API.
3. AI Estimation (backend/ai/) — Sends batches of properties to Claude, which estimates monthly rent, five-year appreciation, five-year future value, and a confidence score for each one.
4. Scoring (backend/scoring/) — Calculates ROI, cash flow, and neighborhood quality metrics, then combines them into a single weighted investment_score (and letter grade) for every property.
5. API (backend/api/) — A FastAPI server that exposes the scored properties.
6. Dashboard (frontend/) — A React + TypeScript + Tailwind app for browsing,       filtering, and comparing ranked properties, with charts showing how ROI varies by neighborhood income and square footage.
7. Analysis DB (backend/db/, backend/analysis/) Loads all pipeline outputs
   into a PostgreSQL database, split into five tables by data provenance
   (raw observed data, AI estimates, and composite scores kept strictly
   separate) so downstream analysis never mixes them incorrectly.
8. Power BI Dashboard A three-page analytics dashboard connected directly
   to PostgreSQL: an overview page (KPIs, map, grade distribution), a
   market diagnostic page (real income vs. real appreciation by ZIP, with
   quadrant analysis), and an AI-recommendation page (top-ranked properties
   by investment score, clearly labeled as model output).

# Tech stack
- Backend: Python, FastAPI, pandas, Anthropic SDK
- Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts, Axios
- Data sources: RentCast API (listings), U.S. Census ACS API (demographics),
  Zillow ZHVI (historical home value/appreciation), Claude (rent/appreciation estimates)
- Analytics: PostgreSQL, Power BI (DAX measures, Key Influencers analysis)

# How to Start
Backend
bash
cd backend
pip install -r requirements.txt

Create a .env file with your API keys:

ANTHROPIC_API_KEY=your_key_here
CENSUS_API_KEY=your_key_here

Add your RentCast API key in backend/collection/rentcast_data.py.

Run the pipeline in order:

bash
1. python collection/rentcast_data.py
2.python ai/data_transform_claude.py
3. python enrichment/build_zip_metrics.py
4. python enrichment/census_enrichment.py
5. python enrichment/merge_zip_metrics.py
6. python ai/claude_estimates.py
7. python ai/make_readable.py
8. python scoring/score_properties.py

Then start the API:

bash
cd api

uvicorn main:app --reload

Frontend
bash

cd frontend

npm install
npm run dev

The dashboard will be available at http://localhost:5173 and expects the API at http://127.0.0.1:8000.


# License
MIT — see LICENSE.
