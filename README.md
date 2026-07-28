# Real Estate Investment Scanner

A tool for finding and ranking investment properties in the Dallas-Fort Worth (DFW) metro area. It pulls active listings, enriches them with neighborhood demographic data, uses Claude to estimate rent and appreciation, then scores and ranks every property so the best opportunities rise to the top all viewable in a web dashboard.

<img width="2832" height="1466" alt="RealEstateDashboard" src="https://github.com/user-attachments/assets/eec8e6a7-5c4d-43aa-aad1-3f45616a48f0" />
<img width="2796" height="1022" alt="RealEstateGraphs" src="https://github.com/user-attachments/assets/75cbd530-7dab-4d94-8386-a80722900423" />



# How it works

The pipeline runs in a few stages:

1. Collection (backend/collection/) — Pulls active for-sale listings across DFW cities from the RentCast API.
2. Enrichment (backend/enrichment/) — Attaches ZIP-code-level demographic data (median income, education, poverty rate, home values, etc.) from the U.S. Census Bureau's ACS API.
3. AI Estimation (backend/ai/) — Sends batches of properties to Claude, which estimates monthly rent, five-year appreciation, five-year future value, and a confidence score for each one.
4. Scoring (backend/scoring/) — Calculates ROI, cash flow, and neighborhood quality metrics, then combines them into a single weighted investment_score (and letter grade) for every property.
5. API (backend/api/) — A FastAPI server that exposes the scored properties.
6. Dashboard (frontend/) — A React + TypeScript + Tailwind app for browsing, filtering, and comparing ranked properties, with charts showing how ROI varies by neighborhood income and square footage.

# Tech stack
- Backend: Python, FastAPI, pandas, Anthropic SDK
- Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts, Axios
- Data sources: RentCast API (listings), U.S. Census ACS API (demographics), Claude (rent/appreciation estimates)

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
