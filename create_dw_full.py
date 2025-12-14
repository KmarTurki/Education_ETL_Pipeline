import csv
import json

# Read CSV data
rows = []
with open('education_data_final.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Extract unique countries
countries = {}
for row in rows:
    code = row['Country Code']
    if code not in countries:
        countries[code] = row['Country Name']

dim_country = []
country_key_map = {}
for i, (code, name) in enumerate(sorted(countries.items()), 1):
    country_key_map[code] = i
    dim_country.append({
        'country_key': i,
        'country_code': code,
        'country_name': name,
        'region': 'Global',
        'continent': None,
        'income_level': None,
        'population': None,
        'gdp_per_capita': None
    })

# Extract unique years
years = set()
for row in rows:
    years.add(int(row['Year']))

dim_time = []
for year in sorted(years):
    dim_time.append({
        'time_key': year,
        'year': year,
        'quarter': 1,
        'semester': 1,
        'decade': (year // 10) * 10,
        'is_current_year': 1 if year == 2024 else 0,
        'fiscal_year': year
    })

# Extract unique indicators
indicators = {}
for row in rows:
    code = row['Indicator Code']
    name = row['Indicator Name']
    if code not in indicators:
        indicators[code] = name

dim_indicator = []
indicator_key_map = {}
for i, (code, name) in enumerate(sorted(indicators.items()), 1):
    indicator_key_map[code] = i
    dim_indicator.append({
        'indicator_key': i,
        'indicator_code': code,
        'indicator_name': name,
        'indicator_category': 'Education',
        'indicator_subcategory': None,
        'measurement_unit': 'Percentage',
        'calculation_method': None,
        'data_source': 'World Bank'
    })

# Create fact table
fact_education_metrics = []
for i, row in enumerate(rows, 1):
    fact_education_metrics.append({
        'metric_id': i,
        'country_key': country_key_map[row['Country Code']],
        'time_key': int(row['Year']),
        'indicator_key': indicator_key_map[row['Indicator Code']],
        'value': float(row['Value'])
    })

# Build final structure
data_warehouse = {
    'dim_country': dim_country,
    'dim_time': dim_time,
    'dim_indicator': dim_indicator,
    'dim_impact_type': [],
    'fact_education_metrics': fact_education_metrics,
    'fact_education_impacts': []
}

# Write to file
with open('data_warehouse_full.json', 'w', encoding='utf-8') as f:
    json.dump(data_warehouse, f, indent=4)

print(f'Created data_warehouse_full.json')
print(f'  Countries: {len(dim_country)}')
print(f'  Years: {len(dim_time)}')
print(f'  Indicators: {len(dim_indicator)}')
print(f'  Metrics: {len(fact_education_metrics)}')
print(f'Sample indicators: {[i["indicator_name"] for i in dim_indicator]}')
