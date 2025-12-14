import urllib.request
import json
import ssl

# Disable SSL verification for this script
ssl._create_default_https_context = ssl._create_unverified_context

with open('data_warehouse_full.json', 'r', encoding='utf-8') as f:
    dw = json.load(f)

country_key_map = {c['country_code']: c['country_key'] for c in dw['dim_country']}
countries = list(country_key_map.keys())
max_id = max([r['impact_id'] for r in dw['fact_education_impacts']], default=0)

print(f"Fetching patent data for {len(countries)} countries...")
added = 0

# Fetch in batches of 10 countries
batch_size = 10
for i in range(0, len(countries), batch_size):
    batch = countries[i:i+batch_size]
    countries_str = ';'.join(batch)
    url = f'https://api.worldbank.org/v2/country/{countries_str}/indicator/IP.PAT.RESD?format=json&per_page=2000&date=1990:2023'
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode())
            if len(data) > 1 and data[1]:
                for item in data[1]:
                    country = item.get('countryiso3code', '')
                    year = item.get('date')
                    value = item.get('value')
                    if value is not None and country in country_key_map:
                        max_id += 1
                        dw['fact_education_impacts'].append({
                            'impact_id': max_id,
                            'country_key': country_key_map[country],
                            'time_key': int(year),
                            'impact_type_key': 1,
                            'value': float(value)
                        })
                        added += 1
        print(f"  Batch {i//batch_size + 1}: processed {batch}")
    except Exception as e:
        print(f"  Error on batch {batch}: {e}")

print(f"\nAdded {added} innovation records")
print(f"Total impacts: {len(dw['fact_education_impacts'])}")

with open('data_warehouse_full.json', 'w', encoding='utf-8') as f:
    json.dump(dw, f, indent=4)

print("Saved to data_warehouse_full.json")
