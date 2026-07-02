import json

INPUT_FILE = "properties_with_estimates.json"
OUTPUT_FILE = "zip_metrics.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    properties = json.load(f)

zip_metrics = {}

for prop in properties:

    zip_code = str(
        prop.get("zip_code", "")
    ).strip()

    if not zip_code:
        continue

    if zip_code not in zip_metrics:

        zip_metrics[zip_code] = {

            # Census Metrics
            "median_income": None,
            "population": None,
            "bachelors_pct": None,
            "poverty_pct": None,
            "owner_occupied_pct": None,
            "median_home_value": None,
            "median_rent": None
        }

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        zip_metrics,
        f,
        indent=2
    )

print(f"Created {OUTPUT_FILE}")
print(f"ZIP count: {len(zip_metrics)}")