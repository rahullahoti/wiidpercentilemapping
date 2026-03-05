"""
Generate extended rawData and countriesInfo JSON from percentiledata-withregions.csv.
Includes country data + region/income group aggregates as first-class entities.

Usage: python generate_data.py
Output: rawdata_extended.js (paste into index.html lines 610-611)
"""

import csv
import json
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), 'percentiledata-withregions.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'rawdata_extended.js')

# Mapping from CSV column suffixes to year keys
YEAR_MAP = {
    '90': '1990',
    '00': '2000',
    '10': '2010',
    '19': '2019',
    '22': '2022',
}

# Filter out junk aggregate names (header row leak etc.)
SKIP_NAMES = {'incomegroup', 'region_wb', ''}

# Normalize aggregate names (CSV has "Latin American" instead of "Latin America")
NAME_FIXES = {
    'Latin American and the Caribbean': 'Latin America and the Caribbean',
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
    raw_data = {}       # {name: {year: [{percentile, global, region, income}, ...]}}
    countries_info = {}  # {name: {region, incomegroup, type?}}

    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['country'].strip()
            if not name or name in SKIP_NAMES:
                continue
            name = NAME_FIXES.get(name, name)

            area = row.get('area', '').strip()  # empty=country, "Region", "Income group"

            # Build countriesInfo (only need once per entity)
            if name not in countries_info:
                if area == 'Region':
                    countries_info[name] = {'region': name, 'type': 'region'}
                elif area == 'Income group':
                    countries_info[name] = {'incomegroup': name, 'type': 'income'}
                else:
                    # Country
                    region = row.get('region_wb', '').strip()
                    incomegroup = row.get('incomegroup', '').strip()
                    countries_info[name] = {
                        'region': region if region else None,
                        'incomegroup': incomegroup if incomegroup else None,
                    }

            if name not in raw_data:
                raw_data[name] = {}

            # Parse p_country to get the domestic percentile number
            p_country_raw = row.get('p_country', '').strip()
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

                if year_key not in raw_data[name]:
                    raw_data[name][year_key] = []

                point = {'percentile': percentile}
                if global_val is not None: point['global'] = global_val
                if region_val is not None: point['region'] = region_val
                if income_val is not None: point['income'] = income_val
                raw_data[name][year_key].append(point)

    # Sort data points by percentile within each year
    for name in raw_data:
        for year in raw_data[name]:
            raw_data[name][year].sort(key=lambda x: x['percentile'])

    # Clean up countries_info: remove None values for countries
    for name in countries_info:
        info = countries_info[name]
        for key in list(info.keys()):
            if info[key] is None:
                del info[key]

    # Generate JS output
    raw_json = json.dumps(raw_data, separators=(',', ':'))
    info_json = json.dumps(countries_info, separators=(',', ':'))

    output = f"    const rawData = {raw_json};\n    const countriesInfo = {info_json};\n"

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(output)

    # Stats
    num_countries = sum(1 for v in countries_info.values() if 'type' not in v)
    num_aggregates = sum(1 for v in countries_info.values() if 'type' in v)
    total_points = sum(len(pts) for c in raw_data.values() for pts in c.values())
    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"Generated {OUTPUT_PATH}")
    print(f"  Countries: {num_countries}, Aggregates: {num_aggregates}")
    print(f"  Total data points: {total_points}")
    print(f"  File size: {file_size / 1024 / 1024:.1f} MB")

    # List aggregates
    for name, info in sorted(countries_info.items()):
        if 'type' in info:
            print(f"  Aggregate: {name} ({info['type']})")

    # Spot-check
    if 'India' in raw_data and '2022' in raw_data['India']:
        sample = raw_data['India']['2022'][:3]
        print(f"  Sample (India 2022 first 3): {json.dumps(sample)}")
    if 'South Asia' in raw_data and '2022' in raw_data['South Asia']:
        sample = raw_data['South Asia']['2022'][:3]
        print(f"  Sample (South Asia 2022 first 3): {json.dumps(sample)}")

if __name__ == '__main__':
    main()
