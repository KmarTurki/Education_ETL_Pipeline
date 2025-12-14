import requests
import json
import time

# Get countries from the full data warehouse
with open('data_warehouse_full.json', 'r', encoding='utf-8') as f:
    dw = json.load(f)

country_codes = [c['country_code'] for c in dw['dim_country']]
print(f"Fetching impact data for {len(country_codes)} countries...")

# World Bank API indicators
INDICATORS = {
    'innovation': 'IP.PAT.RESD',           # Patent applications, residents
    'employment': 'SL.UEM.1524.ZS',        # Youth unemployment (% ages 15-24)
}

def fetch_wb_data(indicator_code, countries):
    """Fetch data from World Bank API"""
    all_data = {}
    countries_str = ';'.join(countries)
    
    url = f"https://api.worldbank.org/v2/country/{countries_str}/indicator/{indicator_code}?format=json&per_page=10000&date=1990:2024"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and data[1]:
                for item in data[1]:
                    country = item['countryiso3code']
                    year = item['date']
                    value = item['value']
                    if value is not None:
                        if country not in all_data:
                            all_data[country] = []
                        all_data[country].append({
                            'year': int(year),
                            'value': float(value)
                        })
    except Exception as e:
        print(f"Error fetching {indicator_code}: {e}")
    
    return all_data

# Fetch data for each indicator
print("\n1. Fetching Innovation (Patent applications)...")
innovation_data = fetch_wb_data(INDICATORS['innovation'], country_codes)
print(f"   Got data for {len(innovation_data)} countries")

print("\n2. Fetching Employment (Youth unemployment)...")
employment_data = fetch_wb_data(INDICATORS['employment'], country_codes)
print(f"   Got data for {len(employment_data)} countries")

# For civic awareness, we'll use a proxy: voter turnout is hard to get via API
# Using literacy rate as proxy for civic awareness (correlated with civic participation)
print("\n3. Fetching Civic Awareness (using SE.ADT.LITR.ZS - Adult literacy as proxy)...")
civic_data = fetch_wb_data('SE.ADT.LITR.ZS', country_codes)
print(f"   Got data for {len(civic_data)} countries")

# Build impact dimension and facts
dim_impact_type = [
    {'impact_type_key': 1, 'impact_name': 'innovation', 'impact_category': 'Socio-Economic', 'impact_code': 'PATENT_APPLICATIONS'},
    {'impact_type_key': 2, 'impact_name': 'civic_awareness', 'impact_category': 'Socio-Economic', 'impact_code': 'ADULT_LITERACY'},
    {'impact_type_key': 3, 'impact_name': 'employment', 'impact_category': 'Socio-Economic', 'impact_code': 'YOUTH_UNEMPLOYMENT'}
]

# Create country key map
country_key_map = {c['country_code']: c['country_key'] for c in dw['dim_country']}

# Build fact table
fact_education_impacts = []
impact_id = 1

# Add innovation data
for country, records in innovation_data.items():
    if country in country_key_map:
        for record in records:
            fact_education_impacts.append({
                'impact_id': impact_id,
                'country_key': country_key_map[country],
                'time_key': record['year'],
                'impact_type_key': 1,  # innovation
                'value': record['value']
            })
            impact_id += 1

# Add civic awareness data
for country, records in civic_data.items():
    if country in country_key_map:
        for record in records:
            fact_education_impacts.append({
                'impact_id': impact_id,
                'country_key': country_key_map[country],
                'time_key': record['year'],
                'impact_type_key': 2,  # civic_awareness
                'value': record['value']
            })
            impact_id += 1

# Add employment data
for country, records in employment_data.items():
    if country in country_key_map:
        for record in records:
            fact_education_impacts.append({
                'impact_id': impact_id,
                'country_key': country_key_map[country],
                'time_key': record['year'],
                'impact_type_key': 3,  # employment
                'value': record['value']
            })
            impact_id += 1

print(f"\nTotal impact records: {len(fact_education_impacts)}")

# Update the data warehouse
dw['dim_impact_type'] = dim_impact_type
dw['fact_education_impacts'] = fact_education_impacts

with open('data_warehouse_full.json', 'w', encoding='utf-8') as f:
    json.dump(dw, f, indent=4)

print(f"\nUpdated data_warehouse_full.json with {len(fact_education_impacts)} impact records")

# Print summary
print("\n=== DATA SOURCES ===")
print("1. Innovation: World Bank - IP.PAT.RESD (Patent applications, residents)")
print("   URL: https://data.worldbank.org/indicator/IP.PAT.RESD")
print("\n2. Civic Awareness: World Bank - SE.ADT.LITR.ZS (Adult literacy rate)")
print("   URL: https://data.worldbank.org/indicator/SE.ADT.LITR.ZS")
print("\n3. Employment: World Bank - SL.UEM.1524.ZS (Youth unemployment rate)")
print("   URL: https://data.worldbank.org/indicator/SL.UEM.1524.ZS")
