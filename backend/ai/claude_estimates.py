from anthropic import Anthropic
from dotenv import load_dotenv
import json
import os
import time

# =====================================
# CONFIGURATION
# =====================================

MODEL = "claude-sonnet-4-6"

BATCH_SIZE = 25

INPUT_FILE = "data/processed/dfw_single_family_claude_compact.json"
OUTPUT_FILE = "data/processed/properties_with_estimates.json"

INPUT_COST_PER_MILLION = 3.00
OUTPUT_COST_PER_MILLION = 15.00

# =====================================
# LOAD ENVIRONMENT
# =====================================

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY not found in .env"
    )

client = Anthropic(api_key=api_key)

# =====================================
# LOAD PROPERTY DATA
# =====================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

properties = data["properties"]

print(f"Loaded {len(properties)} properties")

# =====================================
# HELPERS
# =====================================

def chunk_list(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]

# =====================================
# PROCESS
# =====================================

all_estimates = []

total_input_tokens = 0
total_output_tokens = 0

total_batches = (
    len(properties) + BATCH_SIZE - 1
) // BATCH_SIZE

for batch_number, batch in enumerate(
    chunk_list(properties, BATCH_SIZE),
    start=1
):

    print(
        f"\nProcessing Batch "
        f"{batch_number}/{total_batches}"
    )

    prompt = f"""
You are a DFW real estate investment analyst.

All properties are single-family homes located within the Dallas-Fort Worth metro area.

Field Definitions

Property Data:
c = city
z = zip_code
b = bedrooms
ba = bathrooms
sq = square_feet
lot = lot_size
yr = year_built
p = listing_price
hoa = hoa_fee

Neighborhood Data:
mi = median_income
pop = population
bp = bachelors_pct
pp = poverty_pct
oop = owner_occupied_pct
mhv = median_home_value
mr = median_rent

For each property estimate:

r = estimated monthly market rent (USD)
conf = confidence score (0-100)
a = estimated five-year appreciation percentage
v = estimated property value in five years

Use BOTH property characteristics and neighborhood demographics.

Rent estimates should consider:
- bedrooms
- bathrooms
- square footage
- year built
- listing price
- local median rent
- local median home value
- local income levels

Appreciation estimates should consider:
- median income
- educational attainment
- poverty rate
- owner occupancy
- local home values
- population
- city and ZIP location
- property quality and characteristics

Guidelines:

- Rent estimates should reflect realistic DFW market conditions.
- Appreciation must be between 5 and 40 percent.
- Confidence should reflect certainty of the estimate.
- Return EXACTLY one estimate for every property provided.
- Do not omit any properties.
- Use each property id exactly as provided.
- Return ONLY valid JSON.
- No markdown.
- No explanations.
- No comments.

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

{json.dumps(batch, separators=(",", ":"))}
"""

    try:

        response = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = (
            response.content[0].text
        ).strip()

        estimates = json.loads(response_text)

        all_estimates.extend(estimates)

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

        print(
            f"Returned "
            f"{len(estimates)} estimates"
        )

        print(
            f"Input Tokens: "
            f"{input_tokens:,}"
        )

        print(
            f"Output Tokens: "
            f"{output_tokens:,}"
        )

        time.sleep(1)

    except Exception as e:

        print()
        print("ERROR")
        print(e)

# =====================================
# MERGE RESULTS
# =====================================

estimate_lookup = {
    estimate["id"]: estimate
    for estimate in all_estimates
}

final_properties = []

for property_record in properties:

    merged = property_record.copy()

    estimate = estimate_lookup.get(
        property_record["id"]
    )

    if estimate:

        merged["r"] = estimate.get("r")
        merged["conf"] = estimate.get("conf")
        merged["a"] = estimate.get("a")
        merged["v"] = estimate.get("v")

    final_properties.append(merged)

# =====================================
# SAVE
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
# COSTS
# =====================================

input_cost = (
    total_input_tokens / 1_000_000
) * INPUT_COST_PER_MILLION

output_cost = (
    total_output_tokens / 1_000_000
) * OUTPUT_COST_PER_MILLION

total_cost = (
    input_cost + output_cost
)

# =====================================
# SUMMARY
# =====================================

print("\n" + "=" * 60)
print("PROCESSING COMPLETE")
print("=" * 60)

print(
    f"Properties Loaded: "
    f"{len(properties)}"
)

print(
    f"Estimates Returned: "
    f"{len(all_estimates)}"
)

print("\nTOKEN USAGE")

print(
    f"Input Tokens:  "
    f"{total_input_tokens:,}"
)

print(
    f"Output Tokens: "
    f"{total_output_tokens:,}"
)

print("\nESTIMATED COST")

print(
    f"Input Cost:  "
    f"${input_cost:.4f}"
)

print(
    f"Output Cost: "
    f"${output_cost:.4f}"
)

print(
    f"Total Cost:  "
    f"${total_cost:.4f}"
)

print(
    f"\nSaved file: "
    f"{OUTPUT_FILE}"
)