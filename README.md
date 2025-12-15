# Education Data Warehouse & ETL Pipeline

## Overview
This project is a comprehensive data engineering solution designed to aggregate, transform, and analyze global and regional education statistics. It utilizes a unified **ETL (Extract, Transform, Load)** pipeline to integrate data from CSV sources and the **World Bank API** into a **Star Schema Data Warehouse**.

The primary goal is to enable multi-dimensional analysis of educational metrics (literacy, enrollment, graduation rates) against socio-economic impacts (innovation, employment) across different countries and time periods.

## Architecture

The project follows a simplified, unified workflow:

1.  **ETL Pipeline (`etl_pipeline.py`)**: 
    *   **Extract**: Reads education data from `education_data_final.csv` and fetches impact data live from the World Bank API.
    *   **Transform**: Normalizes data into Dimension and Fact tables. Standardizes country codes and impact types.
    *   **Load**: Saves the structured data into `data_warehouse.json`.

2.  **Analysis Interface (`query_data.py`)**:
    *   Provides a Python-based interface to query the JSON-based warehouse.
    *   Demonstrates complex joining logic between Facts (Metrics, Impacts) and Dimensions (Country, Time, Indicator).

## Data Warehouse Schema

The data warehouse is designed as a **Star Schema** to optimize query performance and analytic simplicity.

### Fact Tables (Measurements)
*   **`fact_education_metrics`**: Scores from the CSV dataset.
    *   `metric_id`, `country_key`, `time_key`, `indicator_key`, `value`
*   **`fact_education_impacts`**: Scores fetched of World Bank API.
    *   `impact_id`, `country_key`, `time_key`, `impact_type_key`, `value`

### Dimension Tables (Context)
*   **`dim_country`**: Geographic context (`country_code`, `country_name`).
*   **`dim_time`**: Temporal context (Year).
*   **`dim_indicator`**: Metadata for educational metrics (e.g., "School enrollment").
*   **`dim_impact_type`**: Metadata for impacts (e.g., "Innovation", "Youth Unemployment").

## Setup & Installation

### Prerequisites
*   Python 3.8+
*   pip package manager

### Installation
1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd DataWarehouse
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage Instructions

### 1. Run the ETL Pipeline
This single command builds the entire warehouse from scratch.
```bash
cd src
python etl_pipeline.py
```
*   *Action*: Reads CSV from `../data/`, queries World Bank API, and saves to `../data/data_warehouse.json`.

### 2. Query the Data
Run the analysis script to see example queries on the warehouse.
```bash
python query_data.py
```
*   *Output*: Will show data availability and example insights (e.g., "School Enrollment in Tunisia", "Innovation Trends").

## Troubleshooting

*   **`data_warehouse.json` not found**: Run `etl_pipeline.py` first.
*   **API Timeouts**: `etl_pipeline.py` queries the World Bank API. If it fails, check your internet connection and try again. It tracks progress and handles batches.

