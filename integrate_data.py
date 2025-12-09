import json
import pandas as pd
import os

# Load scraped data
with open('scraped_data.json', 'r', encoding='utf-8') as f:
    scraped_data = json.load(f)

# Load Kaggle data (assuming CSV files in data/global_perf)
kaggle_files = [f for f in os.listdir('data/global_perf') if f.endswith('.csv')]
kaggle_data = {}
for file in kaggle_files:
    df = pd.read_csv(f'data/global_perf/{file}')
    kaggle_data[file] = df.to_dict(orient='records')

# Merge data into warehouse structure
warehouse = {
    "fact_tables": {
        "education_metrics": [],  # List of dicts with country, year, indicator, value
        "impacts": []  # Innovation, civic awareness, employment
    },
    "dimensions": {
        "countries": list(scraped_data.get('global', {}).keys()),
        "years": list(range(2000, 2024)),
        "indicator_types": ["literacy", "enrollment", "graduation", "dropout", "infrastructure", "teachers", "budget", "mental_health", "innovation", "civic_engagement", "employment"]
    },
    "scraped_data": scraped_data,
    "kaggle_data": kaggle_data
}

# Populate fact table from scraped data
for category, data in scraped_data.items():
    if category == 'global':
        for country, indicators in data.items():
            for indicator, values in indicators.items():
                if isinstance(values, list):
                    for item in values:
                        if isinstance(item, dict) and 'year' in item and 'value' in item:
                            warehouse["fact_tables"]["education_metrics"].append({
                                "country": country,
                                "year": item['year'],
                                "indicator": indicator,
                                "value": item['value']
                            })
    elif category == 'tunisia':
        for indicator, values in data.items():
            if isinstance(values, list):
                for item in values:
                    if isinstance(item, dict) and 'year' in item and 'value' in item:
                        warehouse["fact_tables"]["education_metrics"].append({
                            "country": "Tunisia",
                            "year": item['year'],
                            "indicator": indicator,
                            "value": item['value']
                        })
    elif category == 'impacts':
        for impact_type, values in data.items():
            if isinstance(values, list):
                for item in values:
                    if isinstance(item, dict) and 'year' in item and 'value' in item:
                        warehouse["fact_tables"]["impacts"].append({
                            "country": "Tunisia",  # Assuming Tunisia-specific
                            "year": item['year'],
                            "indicator": impact_type,
                            "value": item['value']
                        })

# Save integrated data
with open('data_warehouse.json', 'w', encoding='utf-8') as f:
    json.dump(warehouse, f, indent=4, ensure_ascii=False)

print("Data integration completed. Saved to data_warehouse.json")
