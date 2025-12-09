import json

def load_warehouse():
    try:
        with open('data_warehouse.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: data_warehouse.json not found.")
        return None

def main():
    warehouse = load_warehouse()
    if not warehouse: return

    print("Data Warehouse Query Interface")
    print("------------------------------")
    
    # Check for available tables
    print("Available Tables:")
    for key in warehouse.keys():
        print(f" - {key} ({len(warehouse[key])} records)")
    print()

    # --- Query 1: Get Literacy Rate for Tunisia (Example of Join Logic) ---
    print("\n[Query 1] Fetching Literacy Rate for Tunisia (Combining Facts & Dims)...")
    
    # 1. Find Tunisia Key
    tun_key = next((item['country_key'] for item in warehouse['dim_country'] if item['country_name'] == 'Tunisia'), None)
    if not tun_key:
        print("Tunisia not found.")
        return

    # 2. Find Indicator Key for "literacy_rate"
    lit_key = next((item['indicator_key'] for item in warehouse['dim_indicator'] if item['indicator_name'] == 'literacy_rate'), None)
    
    # 3. Query Fact Table
    if tun_key and lit_key:
        results = [
            f for f in warehouse['fact_education_metrics'] 
            if f['country_key'] == tun_key and f['indicator_key'] == lit_key
        ]
        
        # 4. Resolve Time Key to Year
        for res in results:
            year = next((t['year'] for t in warehouse['dim_time'] if t['time_key'] == res['time_key']), "Unknown")
            print(f" - Year: {year}, Value: {res['value']}%")
    else:
        print("Could not resolve keys for query.")

    # --- Query 2: Get Innovation Impact for Tunisia ---
    print("\n[Query 2] Fetching Innovation Impact for Tunisia...")
    
    # Find Impact Type Key
    inn_key = next((item['impact_type_key'] for item in warehouse['dim_impact_type'] if item['impact_name'] == 'innovation'), None)

    if tun_key and inn_key:
        results = [
            f for f in warehouse['fact_education_impacts']
            if f['country_key'] == tun_key and f['impact_type_key'] == inn_key
        ]
        
        for res in results:
             year = next((t['year'] for t in warehouse['dim_time'] if t['time_key'] == res['time_key']), "Unknown")
             print(f" - Year: {year}, Value: {res['value']}")

if __name__ == "__main__":
    main()
