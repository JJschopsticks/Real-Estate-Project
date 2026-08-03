"""
Downloads Zillow's public ZHVI (Zillow Home Value Index) ZIP-level time
series and computes REAL trailing 1-year and 5-year home value appreciation
per ZIP code — as opposed to the Claude-estimated appreciation produced by
backend/ai/claude_estimates.py.

This is observed historical data, not a model estimate. It exists so that
downstream analysis can correlate demographics against an appreciation
number that isn't the output of an LLM that was told to factor demographics
into its answer (see backend/scoring/correlation_guard.py).

NOTE ON THE DOWNLOAD URL: Zillow periodically re-versions these files on
https://www.zillow.com/research/data/. ZHVI_URL below points at the
"ZHVI All Homes (SFR+Condo), Time Series, Smoothed, Seasonally Adjusted,
$ - ZIP" file, which is the standard ZIP-level series used for this kind of
analysis. Before running this for real, open the research data page and
confirm the URL still resolves — if Zillow has renamed the file, update the
constant below.
"""

import json
from pathlib import Path

import pandas as pd
import requests

# =====================================
# CONFIGURATION
# =====================================

ZHVI_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
    "Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)

ROOT_DIR = Path(__file__).resolve().parents[2]

RAW_CSV_CACHE = ROOT_DIR / "data" / "raw" / "zhvi_zip_all_homes.csv"

# Only compute/keep ZIPs we actually have properties for, to keep the
# output small. Set to None to keep every ZIP in the Zillow file.
ZIP_FILTER_FILE = ROOT_DIR / "data" / "processed" / "zip_metrics.json"

OUTPUT_FILE = (
    ROOT_DIR / "data" / "processed" / "zip_historical_appreciation.json"
)

APPRECIATION_WINDOWS_MONTHS = {
    "1yr": 12,
    "5yr": 60,
}

# =====================================
# DOWNLOAD
# =====================================


def download_zhvi_csv(force=False):
    """Downloads the ZHVI CSV to a local cache file and returns its path."""

    if RAW_CSV_CACHE.exists() and not force:
        print(f"Using cached ZHVI CSV: {RAW_CSV_CACHE}")
        return RAW_CSV_CACHE

    print(f"Downloading ZHVI data from {ZHVI_URL}")

    response = requests.get(ZHVI_URL, timeout=60)
    response.raise_for_status()

    RAW_CSV_CACHE.parent.mkdir(parents=True, exist_ok=True)

    with open(RAW_CSV_CACHE, "wb") as f:
        f.write(response.content)

    print(f"Saved raw ZHVI CSV to {RAW_CSV_CACHE}")

    return RAW_CSV_CACHE


# =====================================
# LOAD ZIP FILTER
# =====================================


def load_zip_filter():
    if ZIP_FILTER_FILE is None or not ZIP_FILTER_FILE.exists():
        return None

    with open(ZIP_FILTER_FILE, "r", encoding="utf-8") as f:
        zip_metrics = json.load(f)

    return set(zip_metrics.keys())


# =====================================
# PARSE + COMPUTE APPRECIATION
# =====================================


def _nearest_date_column(date_columns, target_date):
    """Returns the date column closest to target_date (Zillow sometimes
    skips a calendar month, so an exact match isn't guaranteed)."""

    return min(date_columns, key=lambda d: abs((d - target_date).days))


def compute_appreciation(csv_path, zip_filter=None):
    df = pd.read_csv(csv_path, dtype={"RegionName": str})

    date_columns = [c for c in df.columns if c[:4].isdigit() and "-" in c]
    date_columns_sorted = sorted(
        date_columns, key=lambda c: pd.to_datetime(c)
    )

    if not date_columns_sorted:
        raise ValueError(
            "No date columns found in ZHVI CSV — check ZHVI_URL / file format."
        )

    latest_col = date_columns_sorted[-1]
    latest_date = pd.to_datetime(latest_col)

    date_lookup = {pd.to_datetime(c): c for c in date_columns_sorted}

    window_cols = {}
    for label, months_back in APPRECIATION_WINDOWS_MONTHS.items():
        target_date = latest_date - pd.DateOffset(months=months_back)
        nearest = _nearest_date_column(date_lookup.keys(), target_date)
        window_cols[label] = date_lookup[nearest]

    results = {}

    for _, row in df.iterrows():
        zip_code = str(row["RegionName"]).strip().zfill(5)

        if zip_filter is not None and zip_code not in zip_filter:
            continue

        current_value = row.get(latest_col)

        if pd.isna(current_value):
            continue

        record = {
            "zip_code": zip_code,
            "home_value_current": float(current_value),
            "data_as_of": latest_col,
        }

        valid = True

        for label, col in window_cols.items():
            past_value = row.get(col)

            if pd.isna(past_value) or past_value == 0:
                valid = False
                continue

            past_value = float(past_value)
            pct_change = (
                (current_value - past_value) / past_value
            ) * 100

            record[f"home_value_{label}_ago"] = past_value
            record[f"appreciation_{label}_pct_actual"] = round(
                pct_change, 2
            )

        if not valid:
            # Keep whatever windows resolved; leave the rest absent
            # rather than guessing.
            pass

        results[zip_code] = record

    return results


# =====================================
# MAIN
# =====================================


def main(force_download=False):
    csv_path = download_zhvi_csv(force=force_download)

    zip_filter = load_zip_filter()

    if zip_filter is not None:
        print(f"Filtering to {len(zip_filter)} ZIPs from {ZIP_FILTER_FILE}")

    results = compute_appreciation(csv_path, zip_filter=zip_filter)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nComputed real appreciation for {len(results)} ZIPs")
    print(f"Saved: {OUTPUT_FILE}")

    missing = (zip_filter or set()) - set(results.keys())
    if missing:
        print(f"\nZIPs with no ZHVI match ({len(missing)}):")
        for z in sorted(missing):
            print(f"  {z}")


if __name__ == "__main__":
    main()
