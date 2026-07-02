import json

PROPERTY_FILE = "dfw_single_family_claude_compact.json"
ZIP_FILE = "zip_metrics.json"

# Overwrite compact file directly
OUTPUT_FILE = PROPERTY_FILE

# ----------------------------------
# LOAD FILES
# ----------------------------------

with open(PROPERTY_FILE, "r", encoding="utf-8") as f:
    property_data = json.load(f)

with open(ZIP_FILE, "r", encoding="utf-8") as f:
    zip_metrics = json.load(f)

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
    "mr": "median_rent"
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