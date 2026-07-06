import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CENSUS_API_KEY")

if not API_KEY:
    raise ValueError(
        "CENSUS_API_KEY not found in .env file"
    )

ZIP_FILE = "../../data/processed/zip_metrics.json"

# ACS 2024 5-Year variables
ACS_VARS = {
    "median_income": "B19013_001E",
    "population": "B01003_001E",
    "median_rent": "B25064_001E",
    "median_home_value": "B25077_001E",

    "education_total": "B15003_001E",
    "bachelors": "B15003_022E",
    "masters": "B15003_023E",
    "professional": "B15003_024E",
    "doctorate": "B15003_025E",

    "poverty_total": "B17001_001E",
    "poverty_below": "B17001_002E",

    "owner_occupied": "B25003_002E",
    "renter_occupied": "B25003_003E",
}

BASE_URL = (
    "https://api.census.gov/data/2024/acs/acs5"
)


def safe_int(value):
    try:
        if value in (
            None,
            "",
            "-666666666",
            "-222222222",
            "-333333333",
            "-555555555",
        ):
            return None

        return int(float(value))

    except Exception:
        return None


with open(ZIP_FILE, "r", encoding="utf-8") as f:
    zip_metrics = json.load(f)

variables = ",".join(ACS_VARS.values())

processed = 0

for zip_code, metrics in zip_metrics.items():

    # Skip already populated ZIPs
    if metrics.get("median_income") is not None:
        print(f"Skipping {zip_code}")
        continue

    print(f"Processing {zip_code}")

    try:

        response = requests.get(
            BASE_URL,
            params={
                "get": variables,
                "for": f"zip code tabulation area:{zip_code}",
                "key": API_KEY
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if len(data) < 2:
            print(f"No data for {zip_code}")
            continue

        headers = data[0]
        values = data[1]

        row = dict(zip(headers, values))

        # --------------------------------------------------
        # Basic Fields
        # --------------------------------------------------

        metrics["median_income"] = safe_int(
            row[ACS_VARS["median_income"]]
        )

        metrics["population"] = safe_int(
            row[ACS_VARS["population"]]
        )

        metrics["median_rent"] = safe_int(
            row[ACS_VARS["median_rent"]]
        )

        metrics["median_home_value"] = safe_int(
            row[ACS_VARS["median_home_value"]]
        )

        # --------------------------------------------------
        # Education %
        # --------------------------------------------------

        education_total = safe_int(
            row[ACS_VARS["education_total"]]
        )

        degree_total = sum(
            filter(
                None,
                [
                    safe_int(row[ACS_VARS["bachelors"]]),
                    safe_int(row[ACS_VARS["masters"]]),
                    safe_int(row[ACS_VARS["professional"]]),
                    safe_int(row[ACS_VARS["doctorate"]]),
                ]
            )
        )

        if education_total and education_total > 0:

            metrics["bachelors_pct"] = round(
                degree_total /
                education_total * 100,
                2
            )

        # --------------------------------------------------
        # Poverty %
        # --------------------------------------------------

        poverty_total = safe_int(
            row[ACS_VARS["poverty_total"]]
        )

        poverty_below = safe_int(
            row[ACS_VARS["poverty_below"]]
        )

        if (
            poverty_total and
            poverty_total > 0 and
            poverty_below is not None
        ):

            metrics["poverty_pct"] = round(
                poverty_below /
                poverty_total * 100,
                2
            )

        # --------------------------------------------------
        # Owner Occupied %
        # --------------------------------------------------

        owner = safe_int(
            row[ACS_VARS["owner_occupied"]]
        )

        renter = safe_int(
            row[ACS_VARS["renter_occupied"]]
        )

        if (
            owner is not None and
            renter is not None and
            (owner + renter) > 0
        ):

            metrics["owner_occupied_pct"] = round(
                owner /
                (owner + renter) * 100,
                2
            )

        processed += 1

    except Exception as e:

        print(
            f"Error processing {zip_code}: {e}"
        )

# --------------------------------------------------
# SAVE
# --------------------------------------------------

with open(
    ZIP_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        zip_metrics,
        f,
        indent=2
    )

print()
print(f"Updated {processed} ZIP codes")
print(f"Saved {ZIP_FILE}")