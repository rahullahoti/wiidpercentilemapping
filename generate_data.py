"""
Generate extended rawData and countriesInfo JSON from percentiledata.csv.
Adds region and income percentile fields alongside global percentile.

Usage: python generate_data.py
Output: rawdata_extended.js (paste into index.html lines 581-582)
"""

import csv
import json
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), 'percentiledata.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'rawdata_extended.js')

# Mapping from CSV column suffixes to year keys
YEAR_MAP = {
    '90': '1990',
    '00': '2000',
    '10': '2010',
    '19': '2019',
    '22': '2022',
}

def parse_int_or_none(val):
    """Parse a string to int, return None if empty/invalid."""
    if val is None or val.strip() == '':
        return None
    try:
        return int(round(float(val)))
    except (ValueError, TypeError):
        return None

def main():
    raw_data = {}       # {country: {year: [{percentile, global, region, income}, ...]}}
    countries_info = {}  # {country: {region, incomegroup}}

    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row['country'].strip()
            if not country:
                continue

            # Build countriesInfo (only need once per country)
            if country not in countries_info:
                region = row.get('region_wb', '').strip()
                incomegroup = row.get('incomegroup', '').strip()
                countries_info[country] = {
                    'region': region if region else None,
                    'incomegroup': incomegroup if incomegroup else None,
                }

            if country not in raw_data:
                raw_data[country] = {}

            # Parse p_country to get the domestic percentile number
            p_country_raw = row.get('p_country', '').strip()
            # p_country can be "Contact 1", "Contact 2", "3", "4", etc.
            # Extract the numeric part
            if p_country_raw.startswith('Contact '):
                percentile = parse_int_or_none(p_country_raw.replace('Contact ', ''))
            else:
                percentile = parse_int_or_none(p_country_raw)

            if percentile is None:
                continue

            # For each year, extract global, region, income percentiles
            for suffix, year_key in YEAR_MAP.items():
                global_val = parse_int_or_none(row.get(f'p_global_{suffix}', ''))
                region_val = parse_int_or_none(row.get(f'p_region_{suffix}', ''))
                income_val = parse_int_or_none(row.get(f'p_income_{suffix}', ''))

                if global_val is None and region_val is None and income_val is None:
                    continue

                if year_key not in raw_data[country]:
                    raw_data[country][year_key] = []

                point = {'percentile': percentile}
                if global_val is not None: point['global'] = global_val
                if region_val is not None: point['region'] = region_val
                if income_val is not None: point['income'] = income_val
                raw_data[country][year_key].append(point)

    # Sort data points by percentile within each year
    for country in raw_data:
        for year in raw_data[country]:
            raw_data[country][year].sort(key=lambda x: x['percentile'])

    # Remove countries_info entries with None values
    for country in countries_info:
        info = countries_info[country]
        if info['region'] is None:
            del info['region']
        if info['incomegroup'] is None:
            del info['incomegroup']

    # Generate JS output
    raw_json = json.dumps(raw_data, separators=(',', ':'))
    info_json = json.dumps(countries_info, separators=(',', ':'))

    output = f"    const rawData = {raw_json};\n    const countriesInfo = {info_json};\n"

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(output)

    # Stats
    num_countries = len(raw_data)
    total_points = sum(len(pts) for c in raw_data.values() for pts in c.values())
    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"Generated {OUTPUT_PATH}")
    print(f"  Countries: {num_countries}")
    print(f"  Total data points: {total_points}")
    print(f"  File size: {file_size / 1024 / 1024:.1f} MB")

    # Spot-check India
    if 'India' in raw_data and '2022' in raw_data['India']:
        sample = raw_data['India']['2022'][:3]
        print(f"  Sample (India 2022 first 3): {json.dumps(sample)}")

if __name__ == '__main__':
    main()
