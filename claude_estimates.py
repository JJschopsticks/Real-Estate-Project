from anthropic import Anthropic
from dotenv import load_dotenv
import json
import os
import time

# =====================================
# CONFIGURATION
# =====================================

MODEL = "claude-sonnet-4-6"
BATCH_SIZE = 50

INPUT_FILE = "dfw_single_family_claude_compact.json"
OUTPUT_FILE = "properties_with_estimates.json"

# Sonnet 4.6 Pricing
INPUT_COST_PER_MILLION = 3.00
OUTPUT_COST_PER_MILLION = 15.00

# =====================================
# LOAD ENVIRONMENT
# =====================================

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in .env")

client = Anthropic(api_key=api_key)

# =====================================
# LOAD PROPERTY DATA
# =====================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

properties = data["properties"]

print(f"Loaded {len(properties)} properties")

# =====================================
# HELPER FUNCTIONS
# =====================================

def chunk_list(items, size):
    """Split list into batches."""
    for i in range(0, len(items), size):
        yield items[i:i + size]

# =====================================
# PROCESS PROPERTIES
# =====================================

all_estimates = []

total_input_tokens = 0
total_output_tokens = 0

total_batches = (len(properties) + BATCH_SIZE - 1) // BATCH_SIZE

for batch_number, batch in enumerate(
    chunk_list(properties, BATCH_SIZE),
    start=1
):

    print("\n" + "=" * 50)
    print(f"Batch {batch_number}/{total_batches}")
    print(f"Properties: {len(batch)}")
    print("=" * 50)

    prompt = f"""
You are a DFW real estate analyst.

All properties are single-family homes.

Field definitions:

c = city
z = zip_code
b = bedrooms
ba = bathrooms
sq = square_feet
lot = lot_size
yr = year_built
p = listing_price
hoa = hoa_fee

For each property estimate:

r = monthly market rent (USD)
conf = confidence score (0-100)
a = five-year appreciation percentage
v = estimated property value in five years

Requirements:

- Use realistic DFW market assumptions.
- Keep appreciation between 10 and 40 percent.
- Return ONLY valid JSON.
- No markdown.
- No explanations.
- No code blocks.
- Return one result for every property provided.

Return format:

[
  {{
    "id": "property-id",
    "r": 2100,
    "conf": 80,
    "a": 22,
    "v": 366000
  }}
]

Properties:

{json.dumps(batch)}
"""

    try:

        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = response.content[0].text.strip()

        batch_results = json.loads(response_text)

        all_estimates.extend(batch_results)

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        print(
            f"Returned {len(batch_results)} estimates"
        )

        print(
            f"Input Tokens: {response.usage.input_tokens:,}"
        )

        print(
            f"Output Tokens: {response.usage.output_tokens:,}"
        )

        # Small delay to be nice to API
        time.sleep(1)

    except Exception as e:

        print(f"\nERROR IN BATCH {batch_number}")
        print(str(e))

# =====================================
# MERGE RESULTS
# =====================================

estimate_lookup = {
    estimate["id"]: estimate
    for estimate in all_estimates
}

final_properties = []

for property_record in properties:

    estimate = estimate_lookup.get(
        property_record["id"],
        {}
    )

    final_properties.append({

        # Property Info
        "id": property_record["id"],
        "city": property_record.get("c"),
        "zip_code": property_record.get("z"),
        "bedrooms": property_record.get("b"),
        "bathrooms": property_record.get("ba"),
        "square_feet": property_record.get("sq"),
        "lot_size": property_record.get("lot"),
        "year_built": property_record.get("yr"),
        "listing_price": property_record.get("p"),
        "hoa_fee": property_record.get("hoa"),

        # Claude Estimates
        "rent_estimate": estimate.get("r"),
        "confidence_score": estimate.get("conf"),
        "five_year_appreciation_pct": estimate.get("a"),
        "five_year_value": estimate.get("v")
    })

# =====================================
# SAVE OUTPUT
# =====================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        final_properties,
        f,
        indent=2
    )

# =====================================
# COST CALCULATION
# =====================================

input_cost = (
    total_input_tokens / 1_000_000
) * INPUT_COST_PER_MILLION

output_cost = (
    total_output_tokens / 1_000_000
) * OUTPUT_COST_PER_MILLION

total_cost = input_cost + output_cost

# =====================================
# SUMMARY
# =====================================

print("\n" + "=" * 60)
print("PROCESSING COMPLETE")
print("=" * 60)

print(f"Properties Loaded: {len(properties)}")
print(f"Estimates Returned: {len(all_estimates)}")

print("\nTOKEN USAGE")
print(f"Input Tokens:  {total_input_tokens:,}")
print(f"Output Tokens: {total_output_tokens:,}")

print("\nESTIMATED COST")
print(f"Input Cost:  ${input_cost:.4f}")
print(f"Output Cost: ${output_cost:.4f}")
print(f"Total Cost:  ${total_cost:.4f}")

print(f"\nSaved file: {OUTPUT_FILE}")