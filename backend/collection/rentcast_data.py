 
import requests
import json
import copy

API_KEY = ""  # <-- replace or use env variable


def new_property():
    return copy.deepcopy(PROPERTY_SCHEMA)


PROPERTY_SCHEMA = {
    "id": None,

    # location
    "address": None,
    "city": None,
    "state": None,
    "zip_code": None,
    "county": None,
    "latitude": None,
    "longitude": None,

    # property details
    "property_type": None,
    "bedrooms": None,
    "bathrooms": None,
    "square_feet": None,
    "lot_size": None,
    "year_built": None,

    # listing / sale
    "listing_price": None,
    "last_sale_price": None,
    "last_sale_date": None,

    # HOA
    "hoa_fee": 0,

    # features
    "garage_spaces": 0,
    "pool": False,
    "fireplace": False,
    "heating": False,
    "cooling": False,
}


def map_rentcast_property(data):
    p = new_property()

    # identity
    p["id"] = data.get("id")

    # location
    p["address"] = data.get("formattedAddress")
    p["city"] = data.get("city")
    p["state"] = data.get("state")
    p["zip_code"] = data.get("zipCode")
    p["county"] = data.get("county")
    p["latitude"] = data.get("latitude")
    p["longitude"] = data.get("longitude")

    # property details
    p["property_type"] = data.get("propertyType")
    p["bedrooms"] = data.get("bedrooms")
    p["bathrooms"] = data.get("bathrooms")
    p["square_feet"] = data.get("squareFootage")
    p["lot_size"] = data.get("lotSize")
    p["year_built"] = data.get("yearBuilt")

    # sale info
    p["listing_price"] = data.get("price")
    p["last_sale_price"] = data.get("lastSalePrice")
    p["last_sale_date"] = data.get("lastSaleDate")

    # HOA
    p["hoa_fee"] = data.get("hoa", {}).get("fee", 0)

    # features
    features = data.get("features", {})
    p["garage_spaces"] = features.get("garageSpaces", 0)
    p["pool"] = features.get("pool", False)
    p["fireplace"] = features.get("fireplace", False)
    p["heating"] = features.get("heating", False)
    p["cooling"] = features.get("cooling", False)

    return p

# -----------------------------
# FETCH SINGLE CITY
# -----------------------------

def fetch_listings_by_city(city, api_calls, max_calls):
    listings = []

    for page in range(1, 3):  # ✅ 2 pages per city

        if api_calls[0] >= max_calls:
            print("\n🚫 API CALL LIMIT REACHED")
            return listings

        params = {
            "city": city,
            "state": "TX",
            "limit": 50,
            "page": page
        }

        headers = {
            "X-Api-Key": API_KEY
        }

        try:
            response = requests.get(
                "https://api.rentcast.io/v1/listings/sale",
                headers=headers,
                params=params
            )

            response.raise_for_status()
            data = response.json()

            if not data:
                print(f"{city}: no data at page {page}")
                break

            print(f"{city} | Page {page} | {len(data)} listings")

            mapped = [map_rentcast_property(d) for d in data]
            listings.extend(mapped)

            api_calls[0] += 1
            print(f"API Calls Used: {api_calls[0]}/{max_calls}")

        except Exception as e:
            print(f"Error with {city}, page {page}: {e}")
            break

    return listings

# -----------------------------
# FETCH ALL CITIES
# -----------------------------

def fetch_all_cities():
    cities = [
        "Dallas",
        "Fort Worth",
        "Plano",
        "Frisco",
        "Arlington",
        "Irving",
        "Garland",
        "McKinney",
        "Denton",
        "Allen"
    ]

    all_data = []
    api_calls = [0]
    MAX_CALLS = 20

    for city in cities:
        if api_calls[0] >= MAX_CALLS:
            break

        city_data = fetch_listings_by_city(city, api_calls, MAX_CALLS)
        all_data.extend(city_data)

    return all_data

# Run test
if __name__ == "__main__":
    print("\n🚀 Collecting DFW listings...\n")

    results = fetch_all_cities()

    print(f"\n✅ Total properties collected: {len(results)}")

    with open("../../data/raw/dfw_properties.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("Saved to dfw_properties.json ✅")