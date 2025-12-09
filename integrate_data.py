import json
import pandas as pd
import os

# --- Helper Functions for Keys ---
def get_or_create_key(dim_list, key_name, value_field, value, other_fields=None):
    for item in dim_list:
        if item[value_field] == value:
            # Update existing item with new details if provided (e.g. better name)
            if other_fields:
                item.update(other_fields)
            return item[key_name]
    
    # Create new key
    new_key = len(dim_list) + 1
    new_item = {key_name: new_key, value_field: value}
    if other_fields:
        new_item.update(other_fields)
    dim_list.append(new_item)
    return new_key

def get_time_key(dim_time, year):
    # Year is the unique identifier for now
    for item in dim_time:
        if item["year"] == year:
            return item["time_key"]
    return None

# --- Main ETL Process ---
def main():
    print("Starting ETL Process...")

    # 1. Load Scraped Data
    try:
        with open('scraped_data.json', 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
    except FileNotFoundError:
        print("Error: scraped_data.json not found. Run scraper.py first.")
        return

    # 2. Initialize Warehouse Structure (4 Dims, 2 Facts)
    warehouse = {
        "dim_country": [], # {country_key, country_code, country_name, ...}
        "dim_time": [],    # {time_key, year, quarter, ...}
        "dim_indicator": [], # {indicator_key, indicator_name, ...}
        "dim_impact_type": [], # {impact_type_key, impact_name, ...}
        "fact_education_metrics": [], # {metric_id, country_key, time_key, indicator_key, value}
        "fact_education_impacts": []  # {impact_id, country_key, time_key, impact_type_key, value}
    }

    # 3. Populate DIM_TIME (Pre-populate years 2000-2024 as per previous logic)
    print("Populating dim_time...")
    for year in range(2000, 2025):
        warehouse["dim_time"].append({
            "time_key": year, # Simple key using year itself or auto-inc
            "year": year,
            "quarter": 1, # Placeholder
            "semester": 1, # Placeholder
            "decade": (year // 10) * 10,
            "is_current_year": 1 if year == 2024 else 0, # Example logic
            "fiscal_year": year
        })
    
    # 4. Process Data
    print("Processing Scraped Data...")

    # --- CATEGORY: GLOBAL & TUNISIA (Fact: Education Metrics) ---
    education_categories = ['global', 'tunisia']
    
    # Pre-define some indicators metadata if available, otherwise build dynamically
    indicators_meta = {
        "literacy_rate": {"category": "Education", "unit": "%"},
        "enrollment_primary": {"category": "Education", "unit": "%"},
        # Add others as needed, defaults will be used
    }

    metric_id_counter = 1
    
    for category in education_categories:
        if category not in scraped_data: continue
        
        data_block = scraped_data[category]
        # data_block structure varies: 
        # global: { "USA": { "literacy_rate": [...], ... } }
        # tunisia: { "infrastructure": [...], ... } (Implied country: Tunisia)

        if category == 'global':
            for country_code, indicators in data_block.items():
                # Ensure Country in Dim
                country_key = get_or_create_key(
                    warehouse["dim_country"], "country_key", "country_code", country_code, 
                    {"country_name": country_code, "region": "Global"}
                )

                for ind_name, values in indicators.items():
                    # Ensure Indicator in Dim
                    ind_key = get_or_create_key(
                        warehouse["dim_indicator"], "indicator_key", "indicator_name", ind_name,
                        {"indicator_category": "Education", "indicator_code": ind_name.upper()}
                    )

                    if isinstance(values, list):
                        for item in values:
                            if 'year' in item and 'value' in item and item['value'] is not None:
                                year_val = int(item['year'])
                                time_key = get_time_key(warehouse["dim_time"], year_val)
                                
                                # Add to Fact
                                if time_key:
                                    warehouse["fact_education_metrics"].append({
                                        "metric_id": metric_id_counter,
                                        "country_key": country_key,
                                        "time_key": time_key,
                                        "indicator_key": ind_key,
                                        "value": float(item['value'])
                                    })
                                    metric_id_counter += 1

        elif category == 'tunisia':
            # Implied Country: Tunisia
            tunisia_key = get_or_create_key(
                warehouse["dim_country"], "country_key", "country_code", "TUN", 
                {"country_name": "Tunisia", "region": "North Africa"}
            )
            
            for ind_name, values in data_block.items():
                ind_key = get_or_create_key(
                    warehouse["dim_indicator"], "indicator_key", "indicator_name", ind_name,
                    {"indicator_category": "Education", "indicator_code": ind_name.upper()}
                )

                if isinstance(values, list):
                    for item in values:
                        if 'year' in item and 'value' in item:
                             year_val = int(item['year'])
                             time_key = get_time_key(warehouse["dim_time"], year_val)
                             if time_key:
                                 warehouse["fact_education_metrics"].append({
                                    "metric_id": metric_id_counter,
                                    "country_key": tunisia_key,
                                    "time_key": time_key,
                                    "indicator_key": ind_key,
                                    "value": float(item['value'])
                                 })
                                 metric_id_counter += 1

    # --- CATEGORY: IMPACTS (Fact: Education Impacts) ---
    impact_id_counter = 1
    if 'impacts' in scraped_data:
        # Assuming Tunisia for these impacts based on earlier script context
        tunisia_key = get_or_create_key(
                warehouse["dim_country"], "country_key", "country_code", "TUN", 
                {"country_name": "Tunisia", "region": "North Africa"}
        )

        for impact_name, values in scraped_data['impacts'].items():
            # Ensure Impact Type in Dim
            impact_key = get_or_create_key(
                warehouse["dim_impact_type"], "impact_type_key", "impact_name", impact_name,
                {"impact_category": "Socio-Economic", "impact_code": impact_name.upper()}
            )

            if isinstance(values, list):
                for item in values:
                    if 'year' in item and 'value' in item:
                        year_val = int(item['year'])
                        time_key = get_time_key(warehouse["dim_time"], year_val)
                        if time_key:
                            warehouse["fact_education_impacts"].append({
                                "impact_id": impact_id_counter,
                                "country_key": tunisia_key,
                                "time_key": time_key,
                                "impact_type_key": impact_key,
                                "value": float(item['value'])
                            })
                            impact_id_counter += 1

    # 5. Save Warehouse
    print("Saving Data Warehouse...")
    with open('data_warehouse.json', 'w', encoding='utf-8') as f:
        json.dump(warehouse, f, indent=4, ensure_ascii=False)

    print("ETL Complete. Warehouse stats:")
    print(f"Dim Country: {len(warehouse['dim_country'])}")
    print(f"Dim Time: {len(warehouse['dim_time'])}")
    print(f"Dim Indicator: {len(warehouse['dim_indicator'])}")
    print(f"Dim Impact Type: {len(warehouse['dim_impact_type'])}")
    print(f"Fact Metrics: {len(warehouse['fact_education_metrics'])}")
    print(f"Fact Impacts: {len(warehouse['fact_education_impacts'])}")

if __name__ == "__main__":
    main()
