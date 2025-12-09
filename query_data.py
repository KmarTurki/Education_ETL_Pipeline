import json

def load_data(file_path='data_warehouse.json'):
    """
    Load the education metrics data from the JSON file.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['fact_tables']['education_metrics']

def filter_data(records, country=None, year=None, indicator=None):
    """
    Filter the records based on country, year, and indicator.
    - country: string, e.g., 'USA'
    - year: string or int, e.g., '2022' or 2022
    - indicator: string, e.g., 'enrollment_primary'
    """
    filtered = records
    if country:
        filtered = [r for r in filtered if r['country'] == country]
    if year:
        year_str = str(year)
        filtered = [r for r in filtered if r['year'] == year_str]
    if indicator:
        filtered = [r for r in filtered if r['indicator'] == indicator]
    return filtered

def compute_aggregate(records, agg_func):
    """
    Compute aggregate on the 'value' field of the records.
    agg_func: 'average', 'sum', 'min', 'max'
    """
    if not records:
        return None
    values = [r['value'] for r in records]
    if agg_func == 'average':
        return sum(values) / len(values)
    elif agg_func == 'sum':
        return sum(values)
    elif agg_func == 'min':
        return min(values)
    elif agg_func == 'max':
        return max(values)
    else:
        raise ValueError("Invalid aggregate function. Choose from 'average', 'sum', 'min', 'max'")

def get_unique_values(records, field):
    """
    Get unique values for a given field (e.g., 'country', 'year', 'indicator').
    """
    return list(set(r[field] for r in records))

# Example usage
if __name__ == "__main__":
    # Load data
    records = load_data()

    # Example 1: Filter by country and indicator, compute average
    filtered = filter_data(records, country='USA', indicator='enrollment_primary')
    avg = compute_aggregate(filtered, 'average')
    print(f"Average enrollment_primary for USA: {avg}")

    # Example 2: Filter by year and indicator, compute sum
    filtered = filter_data(records, year=2022, indicator='dropout_rate')
    total = compute_aggregate(filtered, 'sum')
    print(f"Total dropout_rate in 2022: {total}")

    # Example 3: Get all unique countries
    countries = get_unique_values(records, 'country')
    print(f"Unique countries: {countries}")

    # Example 4: Filter by indicator, compute min and max
    filtered = filter_data(records, indicator='literacy_rate')
    min_val = compute_aggregate(filtered, 'min')
    max_val = compute_aggregate(filtered, 'max')
    print(f"Min literacy_rate: {min_val}, Max literacy_rate: {max_val}")
