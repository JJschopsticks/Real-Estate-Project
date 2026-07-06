import json

INPUT_FILE = "../../data/raw/dfw_properties.json"
OUTPUT_FILE = "../../data/processed/dfw_single_family_claude_compact.json"

# Short field names to reduce token usage
LEGEND = {
    "c": "city",
    "z": "zip_code",
    "b": "bedrooms",
    "ba": "bathrooms",
    "sq": "square_feet",
    "lot": "lot_size",
    "yr": "year_built",
    "p": "listing_price",
    "hoa": "hoa_fee"
}

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    properties = json.load(f)

compact_properties = []

for p in properties:

    # Only keep Single Family homes
    if p.get("property_type") != "Single Family":
        continue

    compact_properties.append({
        "id": p.get("id"),
        "c": p.get("city"),
        "z": p.get("zip_code"),
        "b": p.get("bedrooms"),
        "ba": p.get("bathrooms"),
        "sq": p.get("square_feet"),
        "lot": p.get("lot_size"),
        "yr": p.get("year_built"),
        "p": p.get("listing_price"),
        "hoa": p.get("hoa_fee", 0)
    })

output = {
    "legend": LEGEND,
    "properties": compact_properties
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, separators=(",", ":"))

print(f"Saved {len(compact_properties)} properties to {OUTPUT_FILE}")