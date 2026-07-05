import json

INPUT_FILE = "data/processed/properties_with_estimates.json"
OUTPUT_FILE = "data/processed/properties_with_estimates_readable.json"

FIELD_MAP = {
    "c": "city",
    "z": "zip_code",
    "b": "bedrooms",
    "ba": "bathrooms",
    "sq": "square_feet",
    "lot": "lot_size",
    "yr": "year_built",
    "p": "listing_price",
    "hoa": "hoa_fee",

    "mi": "median_income",
    "pop": "population",
    "bp": "bachelors_pct",
    "pp": "poverty_pct",
    "oop": "owner_occupied_pct",
    "mhv": "median_home_value",
    "mr": "median_rent",

    "r": "estimated_rent",
    "conf": "confidence_score",
    "a": "five_year_appreciation_pct",
    "v": "estimated_value_5yr"
}

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    properties = json.load(f)

readable_properties = []

for prop in properties:

    readable = {}

    for key, value in prop.items():

        readable_key = FIELD_MAP.get(key, key)

        readable[readable_key] = value

    readable_properties.append(readable)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        readable_properties,
        f,
        indent=2
    )

print(f"Created {OUTPUT_FILE}")
print(f"Properties: {len(readable_properties)}")