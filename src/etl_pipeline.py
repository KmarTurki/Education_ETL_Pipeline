import csv
import json
import requests
import time

# Configuration
CSV_FILE = '../data/education_data_final.csv'
OUTPUT_FILE = '../data/data_warehouse.json'
WB_API_BASE = "https://api.worldbank.org/v2/country/{}/indicator/{}?format=json&per_page=10000&date=1990:2024"

# Impact Indicators (World Bank Codes)
IMPACT_INDICATORS = {
    'innovation': 'IP.PAT.RESD',           # Patent applications, residents
    'employment': 'SL.UEM.1524.ZS',        # Youth unemployment (% ages 15-24)
    'civic_awareness': 'SE.ADT.LITR.ZS'    # Adult literacy rate (Proxy)
}

def load_csv_data(filepath):
    """Reads the CSV data."""
    print(f"Loading data from {filepath}...")
    rows = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return []
    return rows

def build_initial_warehouse(rows):
    """Builds the initial warehouse structure (Dimensions + Metrics Fact) from CSV."""
    print("Building Data Warehouse dimensions and metrics...")
    
    # 1. Dim Country
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
            'region': 'Global'
        })

    # 2. Dim Time
    years = set(int(row['Year']) for row in rows)
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

    # 3. Dim Indicator
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
            'measurement_unit': 'Percentage', # Default assumption based on typical WB education data
            'data_source': 'World Bank'
        })

    # 4. Fact Metrics
    fact_education_metrics = []
    for i, row in enumerate(rows, 1):
        fact_education_metrics.append({
            'metric_id': i,
            'country_key': country_key_map[row['Country Code']],
            'time_key': int(row['Year']),
            'indicator_key': indicator_key_map[row['Indicator Code']],
            'value': float(row['Value'])
        })

    warehouse = {
        'dim_country': dim_country,
        'dim_time': dim_time,
        'dim_indicator': dim_indicator,
        'dim_impact_type': [],
        'fact_education_metrics': fact_education_metrics,
        'fact_education_impacts': []
    }
    
    print(f"Reference Data Loaded: {len(dim_country)} Countries, {len(dim_time)} Years, {len(dim_indicator)} Indicators.")
    return warehouse

def fetch_wb_data(indicator_code, country_codes):
    """Fetch data from World Bank API for a list of countries."""
    all_data = {}
    
    # Process in batches to avoid URL length limits
    batch_size = 15
    for i in range(0, len(country_codes), batch_size):
        batch = country_codes[i:i+batch_size]
        countries_str = ';'.join(batch)
        url = WB_API_BASE.format(countries_str, indicator_code)
        
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
            else:
                print(f"Failed to fetch batch starting with {batch[0]}: Status {response.status_code}")
        except Exception as e:
            print(f"Error fetching {indicator_code} for batch {batch[0]}...: {e}")
        
    return all_data

def enrich_with_impacts(warehouse):
    """Fetches impact data and builds the impacts fact table."""
    print("\n--- Enriching Data Warehouse with Impact Metrics ---")
    
    country_codes = [c['country_code'] for c in warehouse['dim_country']]
    country_key_map = {c['country_code']: c['country_key'] for c in warehouse['dim_country']}
    
    # 1. Build Dim Impact Type
    print("Building Impact Dimension...")
    dim_impact_type = [
        {'impact_type_key': 1, 'impact_name': 'innovation', 'impact_category': 'Socio-Economic', 'impact_code': IMPACT_INDICATORS['innovation']},
        {'impact_type_key': 2, 'impact_name': 'employment', 'impact_category': 'Socio-Economic', 'impact_code': IMPACT_INDICATORS['employment']},
        {'impact_type_key': 3, 'impact_name': 'civic_awareness', 'impact_category': 'Socio-Economic', 'impact_code': IMPACT_INDICATORS['civic_awareness']}
    ]
    warehouse['dim_impact_type'] = dim_impact_type
    
    # 2. Fetch and Build Fact Impacts
    fact_education_impacts = []
    impact_id_counter = 1
    
    for impact_key, (name, code) in enumerate(IMPACT_INDICATORS.items(), 1):
        print(f"Fetching {name} data ({code})...")
        data = fetch_wb_data(code, country_codes)
        print(f"  > Retrieved records for {len(data)} countries.")
        
        for country_code, records in data.items():
            if country_code in country_key_map:
                for rec in records:
                    fact_education_impacts.append({
                        'impact_id': impact_id_counter,
                        'country_key': country_key_map[country_code],
                        'time_key': rec['year'],
                        'impact_type_key': impact_key, 
                        'value': rec['value']
                    })
                    impact_id_counter += 1
                    
    warehouse['fact_education_impacts'] = fact_education_impacts
    print(f"Impact enrichment complete. Added {len(fact_education_impacts)} impact records.")
    return warehouse

def main():
    print("Starting ETL Pipeline...")
    
    # Step 1: Extract & Transform CSV Data
    csv_rows = load_csv_data(CSV_FILE)
    if not csv_rows:
        return

    # Step 2: Build Core Warehouse (Dims + Metrics)
    warehouse = build_initial_warehouse(csv_rows)
    
    # Step 3: Fetch & Load Impact Data (API)
    warehouse = enrich_with_impacts(warehouse)
    
    # Step 4: Load (Save to JSON)
    print(f"\nSaving Data Warehouse to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(warehouse, f, indent=4)
        
    print("ETL Pipeline Completed Successfully.")
    print("Summary:")
    print(f"  Countries: {len(warehouse['dim_country'])}")
    print(f"  Years: {len(warehouse['dim_time'])}")
    print(f"  Indicators: {len(warehouse['dim_indicator'])}")
    print(f"  Impact Types: {len(warehouse['dim_impact_type'])}")
    print(f"  Fact Metrics: {len(warehouse['fact_education_metrics'])}")
    print(f"  Fact Impacts: {len(warehouse['fact_education_impacts'])}")

if __name__ == "__main__":
    main()
