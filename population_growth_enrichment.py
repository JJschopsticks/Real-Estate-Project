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

ZIP_FILE = "zip_metrics.json"

POP_VAR = "B01003_001E"

ACS_2019_URL = (
    "https://api.census.gov/data/2019/acs/acs5"
)

ACS_2024_URL = (
    "https://api.census.gov/data/2024/acs/acs5"
)


def get_population(zip_code, year_url):

    try:

        response = requests.get(
            year_url,
            params={
                "get": POP_VAR,
                "for": f"zip code tabulation area:{zip_code}",
                "key": API_KEY
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if len(data) < 2:
            return None

        return int(data[1][0])

    except Exception as e:

        print(
            f"Population lookup failed for {zip_code}: {e}"
        )

        return None


with open(
    ZIP_FILE,
    "r",
    encoding="utf-8"
) as f:

    zip_metrics = json.load(f)


updated = 0

for zip_code, metrics in zip_metrics.items():

    # Skip already processed ZIPs
    if metrics.get("population_growth_pct") is not None:
        continue

    print(f"Processing {zip_code}")

    pop_2019 = get_population(
        zip_code,
        ACS_2019_URL
    )

    pop_2024 = get_population(
        zip_code,
        ACS_2024_URL
    )

    if (
        pop_2019 is None or
        pop_2024 is None or
        pop_2019 == 0
    ):
        print(
            f"Skipping {zip_code} - insufficient data"
        )
        continue

    growth_pct = round(
        ((pop_2024 - pop_2019) / pop_2019) * 100,
        2
    )

    metrics["population_2019"] = pop_2019
    metrics["population_2024"] = pop_2024
    metrics["population_growth_pct"] = growth_pct

    updated += 1

    print(
        f"{zip_code}: "
        f"{pop_2019:,} -> {pop_2024:,} "
        f"({growth_pct:+.2f}%)"
    )

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
print(f"Updated {updated} ZIP codes")
print(f"Saved {ZIP_FILE}")