import json
import os

PROPERTY_FILE = "../../data/processed/dfw_single_family_claude_compact.json"
ZIP_FILE = "../../data/processed/zip_metrics.json"

# Real, observed ZHVI appreciation (backend/enrichment/zhvi_ingestion.py).
# Distinct from the Claude-estimated appreciation added later by
# backend/ai/claude_estimates.py — see FIELD_PROVENANCE in
# backend/scoring/field_provenance.py.
ZHVI_FILE = "../../data/processed/zip_historical_appreciation.json"

# Overwrite compact file directly
OUTPUT_FILE = PROPERTY_FILE

# ----------------------------------
# LOAD FILES
# ----------------------------------

with open(PROPERTY_FILE, "r", encoding="utf-8") as f:
    property_data = json.load(f)

with open(ZIP_FILE, "r", encoding="utf-8") as f:
    zip_metrics = json.load(f)

zhvi_metrics = {}

if os.path.exists(ZHVI_FILE):
    with open(ZHVI_FILE, "r", encoding="utf-8") as f:
        zhvi_metrics = json.load(f)
else:
    print(
        f"WARNING: {ZHVI_FILE} not found — run "
        "backend/enrichment/zhvi_ingestion.py first. "
        "Skipping real appreciation merge for now."
    )

# ----------------------------------
# UPDATE LEGEND
# ----------------------------------

property_data["legend"].update({
    "mi": "median_income",
    "pop": "population",
    "bp": "bachelors_pct",
    "pp": "poverty_pct",
    "oop": "owner_occupied_pct",
    "mhv": "median_home_value",
    "mr": "median_rent",
    "za5": "actual_zip_appreciation_5yr_pct",
    "za1": "actual_zip_appreciation_1yr_pct"
})

properties = property_data["properties"]

missing_zips = set()
updated_count = 0

# ----------------------------------
# MERGE ZIP METRICS
# ----------------------------------

for prop in properties:

    zip_code = str(
        prop.get("z", "")
    ).strip()

    metrics = zip_metrics.get(zip_code)

    if not metrics:
        missing_zips.add(zip_code)
        continue

    prop["mi"] = metrics.get("median_income")
    prop["pop"] = metrics.get("population")
    prop["bp"] = metrics.get("bachelors_pct")
    prop["pp"] = metrics.get("poverty_pct")
    prop["oop"] = metrics.get("owner_occupied_pct")
    prop["mhv"] = metrics.get("median_home_value")
    prop["mr"] = metrics.get("median_rent")

    zhvi = zhvi_metrics.get(zip_code)

    if zhvi:
        prop["za5"] = zhvi.get("appreciation_5yr_pct_actual")
        prop["za1"] = zhvi.get("appreciation_1yr_pct_actual")

    updated_count += 1

# ----------------------------------
# SAVE
# ----------------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        property_data,
        f,
        separators=(",", ":")
    )

# ----------------------------------
# SUMMARY
# ----------------------------------

print()
print("=" * 50)
print("ZIP METRICS MERGE COMPLETE")
print("=" * 50)

print(f"Properties Processed: {len(properties)}")
print(f"Properties Updated:   {updated_count}")

if missing_zips:
    print()
    print("Missing ZIP Metrics:")
    for zip_code in sorted(missing_zips):
        print(f"  {zip_code}")

print()
print(f"Saved: {OUTPUT_FILE}")