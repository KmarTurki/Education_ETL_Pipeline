import json

DATA_FILE = '../data/data_warehouse.json'

def load_warehouse():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {DATA_FILE} not found. Please run etl_pipeline.py first.")
        return None

def find_key(warehouse, dim_name, search_field, search_value, key_field):
    """Helper to find a surrogate key in a dimension table."""
    for item in warehouse.get(dim_name, []):
        if item.get(search_field) == search_value:
            return item.get(key_field)
    return None

def main():
    warehouse = load_warehouse()
    if not warehouse: return

    print("Data Warehouse Query Interface")
    print("==============================")
    
    # Check for available tables
    print("Available Tables:")
    for key in warehouse.keys():
        print(f" - {key} ({len(warehouse[key])} records)")
    print()

    # --- Query 1: Get Literacy Rate for Tunisia (Example of Join Logic) ---
    print("\n[Query 1] Fetching Value for 'Tunisia' - 'School enrollment, secondary (% gross)'")
    
    country_name = "Tunisia"
    target_indicator = "School enrollment, secondary (% gross)" # Ensure this matches CSV names exactly
    
    country_key = find_key(warehouse, 'dim_country', 'country_name', country_name, 'country_key')
    indicator_key = find_key(warehouse, 'dim_indicator', 'indicator_name', target_indicator, 'indicator_key')

    if country_key and indicator_key:
        print(f"  > Found Keys: Country={country_key}, Indicator={indicator_key}")
        
        results = [
            f for f in warehouse['fact_education_metrics'] 
            if f['country_key'] == country_key and f['indicator_key'] == indicator_key
        ]
        
        # Sort by year
        # Need to resolve time_key to year first to sort effectively, or just sort by time_key if it is the year
        results_with_year = []
        for res in results:
             year = next((t['year'] for t in warehouse['dim_time'] if t['time_key'] == res['time_key']), res['time_key'])
             results_with_year.append({'year': year, 'value': res['value']})
        
        results_with_year.sort(key=lambda x: x['year'])

        for res in results_with_year:
            print(f"    - Year: {res['year']}, Value: {res['value']}")
    else:
        print(f"  > Could not find keys for {country_name} or {target_indicator}. Check data.")


    # --- Query 2: Get Innovation Impact ---
    print("\n[Query 2] Fetching Innovation Impact (Patents) for Tunisia...")
    
    impact_name = "innovation"
    impact_key = find_key(warehouse, 'dim_impact_type', 'impact_name', impact_name, 'impact_type_key')

    if country_key and impact_key:
         results = [
            f for f in warehouse['fact_education_impacts']
            if f['country_key'] == country_key and f['impact_type_key'] == impact_key
        ]
         
         # Sort by time
         results.sort(key=lambda x: x['time_key'])
         
         for res in results:
             print(f"    - Year: {res['time_key']}, Value: {res['value']}")
    else:
         print("  > Could not find keys for Impact query.")

if __name__ == "__main__":
    main()
