# Education ETL Pipeline / Data Warehouse

This project implements an ETL (Extract, Transform, Load) pipeline to aggregate education data from multiple sources (World Bank API, Web Scraping, Kaggle) into a Star Schema Data Warehouse.

## Project Structure

### 1. Source Data & Extraction (`scraper.py`)
- Fetches global education data (Literacy, Enrollment, etc.) using the World Bank API.
- Scrapes Tunisia-specific data (Infrastructure, Budget, Suicide Rates) using proxy indicators.
- Scrapes unstructured text data from educational websites (UNESCO, OECD).
- Outputs raw data to `scraped_data.json`.

### 2. Integration & Transformation (`integrate_data.py`)
- Reads raw `scraped_data.json` and local CSVs.
- Transforms data into a Star Schema with **2 Fact Tables** and **4 Dimension Tables**.
- Generates Surrogate Keys for referential integrity.
- Outputs the structured data to `data_warehouse.json`.

### 3. Analysis (`query_data.py`)
- Provides a Python interface to query the Data Warehouse.
- Demonstrates how to join Fact and Dimension tables using keys to retrieve meaningful insights.

## Data Warehouse Schema

### Fact Tables
1.  **`fact_education_metrics`**: Core education statistics.
    *   Columns: `metric_id`, `country_key`, `time_key`, `indicator_key`, `value`
2.  **`fact_education_impacts`**: Socio-economic impacts.
    *   Columns: `impact_id`, `country_key`, `time_key`, `impact_type_key`, `value`

### Dimension Tables
1.  **`dim_country`**: `country_key`, `country_code`, `country_name`, `region`
2.  **`dim_time`**: `time_key` (Year), `year`, `decade`
3.  **`dim_indicator`**: `indicator_key`, `indicator_name`, `category`
4.  **`dim_impact_type`**: `impact_type_key`, `impact_name`, `category`

## Setup & Usage

1.  **Install Dependencies**:
    ```bash
    pip install pandas requests beautifulsoup4 lxml
    ```

2.  **Run the Pipeline**:
    ```bash
    # Step 1: Scrape Data
    python scraper.py
    
    # Step 2: Build Warehouse
    python integrate_data.py
    ```

3.  **Query Data**:
    ```bash
    python query_data.py
    ```
