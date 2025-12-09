# Education ETL Pipeline / Data Warehouse

This project implements an ETL (Extract, Transform, Load) pipeline to aggregate education data from multiple sources, including the World Bank API, web scraping, and local datasets. The goal is to build a data warehouse for analyzing education metrics, influencing factors, and their impacts.

## Project Structure

- **`scraper.py`**: A Python script that:
    - Fetches global education indicators (literacy, enrollment, etc.) from the World Bank API.
    - Scrapes specific data for Tunisia (infrastructure, teacher quality, budget).
    - Scrapes text data from educational organization websites.
    - Saves the raw data to `scraped_data.json`.

- **`integrate_data.py`**: A data integration script that:
    - Loads the raw `scraped_data.json`.
    - Ingests local CSV datasets from the `data/` directory (e.g., Kaggle datasets).
    - Transforms and merges data into a structured JSON Data Warehouse (`data_warehouse.json`) with Fact and Dimension tables.

- **`query_data.py`**: Provides an interface to query the `data_warehouse.json` for analysis, allowing users to retrieve specific metrics by country and year.

## Setup & Usage

1.  **Dependencies**: Ensure you have the required Python packages installed:
    ```bash
    pip install pandas requests beautifulsoup4 lxml
    ```

2.  **Run the Pipeline**:
    - **Step 1: Scrape Data**
      ```bash
      python scraper.py
      ```
    - **Step 2: Integrate Data**
      ```bash
      python integrate_data.py
      ```

3.  **Query Data**:
    - Use `query_data.py` to inspect the results.

## Data Sources

- **World Bank API**: For standardized global development indicators.
- **Web Scraping**: Extracted text from UNESCO, OECD, and Tunisian Ministry of Education.
- **Local Data**: CSV files located in `data/global_perf/`.
