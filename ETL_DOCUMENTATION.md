# Education ETL Pipeline - Detailed Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Data Flow](#architecture--data-flow)
3. [Detailed Code Description](#detailed-code-description)
4. [Data Sources](#data-sources)
5. [Data Warehouse Schema](#data-warehouse-schema)
6. [Execution Workflow](#execution-workflow)

---

## Project Overview

This project implements a comprehensive **ETL (Extract, Transform, Load) pipeline** designed to aggregate education-related data from multiple heterogeneous sources into a **Star Schema Data Warehouse**. The pipeline focuses on global education metrics, with special emphasis on Tunisia, and tracks both educational performance indicators and their socio-economic impacts.

### Key Objectives
- Extract education data from multiple APIs and web sources
- Transform unstructured and semi-structured data into a normalized star schema
- Load data into a JSON-based data warehouse for analysis
- Enable querying and analysis of education metrics and their impacts

---

## Architecture & Data Flow

```
┌─────────────────┐
│  Data Sources   │
│  (APIs, CSV,    │
│   Web Scraping) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extraction     │
│  (scraper.py,   │
│   data.py)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Raw Data       │
│  (scraped_data. │
│   json, CSV)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Transformation │
│  (integrate_    │
│   data.py,      │
│   create_dw_    │
│   full.py)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Warehouse │
│  (Star Schema)  │
│  JSON Format    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Query &        │
│  Analysis       │
│  (query_data.py)│
└─────────────────┘
```

---

## Detailed Code Description

### 1. **scraper.py** - Primary Data Extraction Script

**Purpose**: Extracts education data from the World Bank API and web sources.

**Key Components**:

#### Data Categories
- **Global Education Data**: Literacy rates, enrollment rates (primary/secondary), graduation rates, dropout rates
- **Tunisia-Specific Data**: Infrastructure metrics, teacher quality, budget allocation, mental health indicators
- **Influencing Factors**: Curriculum quality, school environment, socio-economic factors (GINI index)
- **Impacts**: Innovation (patents), civic awareness, employment rates

#### Functions

**`scrape_wb_api(country, indicator)`**
- Fetches data from World Bank API v2
- URL Format: `http://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&per_page=1000`
- Returns list of `{year, value}` dictionaries
- Handles errors gracefully with timeout protection

**`scrape_web_text(url)`**
- Scrapes unstructured text from educational websites
- Uses BeautifulSoup with lxml parser
- Extracts up to 5000 characters of text content
- Targets: UNESCO, OECD, Tunisian Ministry of Education websites

#### Data Structure Output
```json
{
  "global": {
    "USA": {"literacy_rate": [...], "enrollment_primary": [...]},
    "CHN": {...},
    ...
  },
  "tunisia": {
    "infrastructure": [...],
    "budget": [...]
  },
  "factors": {...},
  "impacts": {...},
  "web_data": {...}
}
```

**Output**: `scraped_data.json`

---

### 2. **data.py** - Kaggle Dataset Downloader

**Purpose**: Downloads education datasets from Kaggle platform.

**Functionality**:
- Uses Kaggle API (`kaggle.api.kaggle_api_extended.KaggleApi`)
- Requires Kaggle API credentials (username and API key)
- Downloads two datasets:
  1. `theworldbank/education-statistics` → `data/global_perf/`
  2. `theworldbank/world-development-indicators` → `data/wdi_2021/`
- Automatically unzips downloaded files

**Note**: This script requires Kaggle API authentication setup.

---

### 3. **create_dw_full.py** - CSV to Data Warehouse Converter

**Purpose**: Transforms CSV data (`education_data_final.csv`) into the full data warehouse structure.

**Process**:

1. **Read CSV File**
   - Expected columns: `Country Code`, `Country Name`, `Year`, `Indicator Code`, `Indicator Name`, `Value`
   - Reads all rows into memory

2. **Build Dimension Tables**

   **dim_country**:
   - Extracts unique countries from CSV
   - Creates surrogate keys (auto-incrementing integers)
   - Fields: `country_key`, `country_code`, `country_name`, `region`, `continent`, `income_level`, `population`, `gdp_per_capita`

   **dim_time**:
   - Extracts unique years from CSV
   - Calculates derived attributes: `decade`, `is_current_year`, `fiscal_year`
   - Fields: `time_key` (year), `year`, `quarter`, `semester`, `decade`, `is_current_year`, `fiscal_year`

   **dim_indicator**:
   - Extracts unique indicators from CSV
   - Maps indicator codes to names
   - Fields: `indicator_key`, `indicator_code`, `indicator_name`, `indicator_category`, `indicator_subcategory`, `measurement_unit`, `calculation_method`, `data_source`

3. **Build Fact Table**

   **fact_education_metrics**:
   - One row per metric observation
   - Links to dimension tables via foreign keys
   - Fields: `metric_id`, `country_key`, `time_key`, `indicator_key`, `value`

**Output**: `data_warehouse_full.json`

---

### 4. **integrate_data.py** - Star Schema Builder

**Purpose**: Transforms scraped JSON data into a normalized star schema data warehouse.

**Key Functions**:

**`get_or_create_key(dim_list, key_name, value_field, value, other_fields=None)`**
- Implements surrogate key generation pattern
- Checks if dimension entry exists, returns existing key
- Creates new dimension entry if not found
- Updates existing entries with new metadata if provided

**`get_time_key(dim_time, year)`**
- Resolves year to time_key for fact table joins
- Returns `None` if year not in dimension

**Main ETL Process**:

1. **Load Raw Data**: Reads `scraped_data.json`

2. **Initialize Warehouse Structure**:
   ```python
   {
     "dim_country": [],
     "dim_time": [],
     "dim_indicator": [],
     "dim_impact_type": [],
     "fact_education_metrics": [],
     "fact_education_impacts": []
   }
   ```

3. **Populate dim_time**: Pre-populates years 2000-2024

4. **Process Global Education Data**:
   - Iterates through countries (USA, CHN, IND, TUN, FRA, DEU)
   - For each indicator (literacy_rate, enrollment_primary, etc.):
     - Ensures country exists in `dim_country`
     - Ensures indicator exists in `dim_indicator`
     - Creates fact records in `fact_education_metrics`

5. **Process Tunisia-Specific Data**:
   - Similar process but for Tunisia only
   - Handles infrastructure, budget, teacher quality metrics

6. **Process Impact Data**:
   - Creates entries in `dim_impact_type`
   - Populates `fact_education_impacts` with innovation, civic awareness, employment data

**Output**: `data_warehouse.json`

---

### 5. **fetch_innovation.py** - Innovation Data Enrichment

**Purpose**: Fetches patent application data from World Bank API and adds it to the existing data warehouse.

**Process**:

1. **Load Existing Warehouse**: Reads `data_warehouse_full.json`

2. **Batch Processing**:
   - Processes countries in batches of 10 (to avoid API rate limits)
   - Fetches indicator `IP.PAT.RESD` (Patent applications, residents)
   - Date range: 1990-2023

3. **Data Integration**:
   - Maps country codes to country keys
   - Creates new impact records in `fact_education_impacts`
   - Sets `impact_type_key = 1` (innovation)
   - Auto-increments `impact_id`

4. **Error Handling**:
   - SSL verification disabled (for compatibility)
   - Timeout set to 60 seconds
   - Continues processing even if batch fails

**Output**: Updates `data_warehouse_full.json` in-place

---

### 6. **scrape_impacts.py** - Comprehensive Impact Data Scraper

**Purpose**: Fetches multiple impact indicators from World Bank API and builds/updates the impact dimension and fact tables.

**Indicators Fetched**:

1. **Innovation** (`IP.PAT.RESD`):
   - Patent applications by residents
   - Measures innovation capacity

2. **Employment** (`SL.UEM.1524.ZS`):
   - Youth unemployment rate (% ages 15-24)
   - Proxy for education's impact on employment

3. **Civic Awareness** (`SE.ADT.LITR.ZS`):
   - Adult literacy rate (used as proxy for civic awareness)
   - Correlated with civic participation

**Process**:

1. **Load Warehouse**: Reads `data_warehouse_full.json`

2. **Fetch Data**:
   - Uses `fetch_wb_data()` function
   - Fetches data for all countries in the warehouse
   - Date range: 1990-2024
   - Handles up to 10,000 records per request

3. **Build Dimension**:
   - Creates/updates `dim_impact_type` with three impact types:
     - `impact_type_key: 1` - innovation
     - `impact_type_key: 2` - civic_awareness
     - `impact_type_key: 3` - employment

4. **Build Fact Table**:
   - Creates records in `fact_education_impacts`
   - Links to countries and time dimensions
   - Stores numeric values

**Output**: Updates `data_warehouse_full.json` with impact data

---

### 7. **query_data.py** - Data Warehouse Query Interface

**Purpose**: Provides a Python interface to query the data warehouse and demonstrates join operations.

**Functions**:

**`load_warehouse()`**
- Loads `data_warehouse.json` into memory
- Returns warehouse dictionary or `None` if file not found

**Query Examples**:

1. **Query 1: Literacy Rate for Tunisia**
   - Finds Tunisia's `country_key` from `dim_country`
   - Finds "literacy_rate" `indicator_key` from `dim_indicator`
   - Joins `fact_education_metrics` with `dim_time` to get year values
   - Returns time series of literacy rates

2. **Query 2: Innovation Impact for Tunisia**
   - Finds innovation `impact_type_key` from `dim_impact_type`
   - Queries `fact_education_impacts` filtered by country and impact type
   - Joins with `dim_time` to resolve years

**Demonstrates**:
- Star schema join patterns
- Key resolution (natural keys → surrogate keys)
- Fact table filtering
- Dimension table lookups

---

## Data Sources

### 1. **World Bank API** (Primary Source)

**Base URL**: `http://api.worldbank.org/v2/`

**Endpoint Format**: `/country/{country}/indicator/{indicator}?format=json&per_page={limit}`

#### Education Indicators Used:

| Indicator Code | Indicator Name | Category | Used In |
|---------------|----------------|----------|---------|
| `SE.ADT.LITR.ZS` | Literacy rate, adult total (% of people ages 15 and above) | Education | `scraper.py`, `scrape_impacts.py` |
| `SE.PRM.ENRR` | School enrollment, primary (% gross) | Education | `scraper.py` |
| `SE.SEC.ENRR` | School enrollment, secondary (% gross) | Education | `scraper.py` |
| `SE.SEC.CMPT.LO.ZS` | Lower secondary completion rate, total (% of relevant age group) | Education | `scraper.py` |
| `SE.PRM.UNER.ZS` | Children out of school, primary | Education | `scraper.py` |
| `SE.PRM.TCHR` | Pupil-teacher ratio in primary education | Infrastructure | `scraper.py` |
| `SE.PRM.TCHR.FE.ZS` | Female teachers in primary education (% of total) | Teacher Quality | `scraper.py` |
| `SE.XPD.TOTL.GD.ZS` | Government expenditure on education, total (% of GDP) | Budget | `scraper.py` |
| `SE.PRM.CUAT.ZS` | Education time (years) | Curriculum | `scraper.py` |

#### Impact Indicators Used:

| Indicator Code | Indicator Name | Category | Used In |
|---------------|----------------|----------|---------|
| `IP.PAT.RESD` | Patent applications, residents | Innovation | `scraper.py`, `fetch_innovation.py`, `scrape_impacts.py` |
| `SL.UEM.TOTL.ZS` | Unemployment, total (% of total labor force) | Employment | `scraper.py` |
| `SL.UEM.1524.ZS` | Unemployment, youth total (% of total labor force ages 15-24) | Employment | `scrape_impacts.py` |
| `EG.ELC.ACCS.ZS` | Access to electricity (% of population) | Development (Proxy) | `scraper.py` |

#### Socio-Economic Indicators:

| Indicator Code | Indicator Name | Category | Used In |
|---------------|----------------|----------|---------|
| `SI.POV.GINI` | GINI index (World Bank estimate) | Inequality | `scraper.py` |
| `SH.STA.SUIC.P5` | Suicide mortality rate (per 100,000 population) | Mental Health (Proxy) | `scraper.py` |

**Countries Tracked**:
- USA (United States)
- CHN (China)
- IND (India)
- TUN (Tunisia) - Primary focus
- FRA (France)
- DEU (Germany)
- Plus all countries from `education_data_final.csv`

**API Documentation**: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392

---

### 2. **Kaggle Datasets**

**Platform**: https://www.kaggle.com/

**Datasets Downloaded**:

1. **Education Statistics** (`theworldbank/education-statistics`)
   - Comprehensive education metrics from World Bank
   - Saved to: `data/global_perf/`
   - Used for: Global education performance analysis

2. **World Development Indicators** (`theworldbank/world-development-indicators`)
   - Broad development indicators including education
   - Saved to: `data/wdi_2021/`
   - Used for: Cross-sectoral analysis

**Access**: Requires Kaggle API credentials (username and API key)

**Script**: `data.py`

---

### 3. **CSV File: education_data_final.csv**

**Format**: CSV with columns:
- `Country Code` (ISO 3-letter code)
- `Country Name`
- `Year`
- `Indicator Code` (World Bank indicator codes)
- `Indicator Name`
- `Value` (numeric)

**Usage**: 
- Primary source for `create_dw_full.py`
- Contains historical education data for multiple countries
- Populates the initial `data_warehouse_full.json`

**Processing**: `create_dw_full.py`

---

### 4. **Web Scraping Sources**

**Technology**: BeautifulSoup4 with lxml parser

**Target Websites**:

1. **UNESCO Education Portal**
   - URL: `https://en.unesco.org/themes/education`
   - Purpose: Unstructured text data on global education policies
   - Extraction: First 5000 characters of text content

2. **OECD Education**
   - URL: `https://www.oecd.org/education/`
   - Purpose: Education policy and research information
   - Extraction: First 5000 characters of text content

3. **Tunisian Ministry of Education** (Example)
   - URL: `https://www.education.gov.tn/`
   - Purpose: Tunisia-specific education information
   - Extraction: First 5000 characters of text content

**Note**: Web scraping extracts unstructured text data, which may be used for qualitative analysis or metadata enrichment.

**Script**: `scraper.py` (function: `scrape_web_text()`)

---

## Data Warehouse Schema

### Star Schema Design

The data warehouse follows a **Star Schema** pattern with:
- **2 Fact Tables** (measures/metrics)
- **4 Dimension Tables** (descriptive attributes)

### Dimension Tables

#### 1. **dim_country**
Stores country information.

| Field | Type | Description |
|-------|------|-------------|
| `country_key` | INTEGER (PK) | Surrogate key |
| `country_code` | VARCHAR(3) | ISO 3-letter country code |
| `country_name` | VARCHAR(255) | Full country name |
| `region` | VARCHAR(255) | Geographic region |
| `continent` | VARCHAR(255) | Continent (nullable) |
| `income_level` | VARCHAR(255) | Income classification (nullable) |
| `population` | BIGINT | Population count (nullable) |
| `gdp_per_capita` | FLOAT | GDP per capita (nullable) |

#### 2. **dim_time**
Stores temporal information.

| Field | Type | Description |
|-------|------|-------------|
| `time_key` | INTEGER (PK) | Surrogate key (year value) |
| `year` | INTEGER | Calendar year |
| `quarter` | INTEGER | Quarter (1-4, placeholder) |
| `semester` | INTEGER | Semester (1-2, placeholder) |
| `decade` | INTEGER | Decade (e.g., 2000, 2010) |
| `is_current_year` | BOOLEAN | Flag for current year |
| `fiscal_year` | INTEGER | Fiscal year |

#### 3. **dim_indicator**
Stores education indicator metadata.

| Field | Type | Description |
|-------|------|-------------|
| `indicator_key` | INTEGER (PK) | Surrogate key |
| `indicator_code` | VARCHAR(50) | World Bank indicator code |
| `indicator_name` | VARCHAR(255) | Human-readable name |
| `indicator_category` | VARCHAR(255) | Category (e.g., "Education") |
| `indicator_subcategory` | VARCHAR(255) | Subcategory (nullable) |
| `measurement_unit` | VARCHAR(50) | Unit (e.g., "Percentage") |
| `calculation_method` | VARCHAR(255) | Calculation method (nullable) |
| `data_source` | VARCHAR(255) | Source (e.g., "World Bank") |

#### 4. **dim_impact_type**
Stores impact type metadata.

| Field | Type | Description |
|-------|------|-------------|
| `impact_type_key` | INTEGER (PK) | Surrogate key |
| `impact_code` | VARCHAR(50) | Impact code (e.g., "PATENT_APPLICATIONS") |
| `impact_name` | VARCHAR(255) | Impact name (e.g., "innovation") |
| `impact_category` | VARCHAR(255) | Category (e.g., "Socio-Economic") |

### Fact Tables

#### 1. **fact_education_metrics**
Stores core education metrics/measurements.

| Field | Type | Description |
|-------|------|-------------|
| `metric_id` | INTEGER (PK) | Surrogate key |
| `country_key` | INTEGER (FK) | Foreign key to `dim_country` |
| `time_key` | INTEGER (FK) | Foreign key to `dim_time` |
| `indicator_key` | INTEGER (FK) | Foreign key to `dim_indicator` |
| `value` | FLOAT | Metric value |

**Index**: Composite index on `(country_key, time_key, indicator_key)`

#### 2. **fact_education_impacts**
Stores socio-economic impacts of education.

| Field | Type | Description |
|-------|------|-------------|
| `impact_id` | INTEGER (PK) | Surrogate key |
| `country_key` | INTEGER (FK) | Foreign key to `dim_country` |
| `time_key` | INTEGER (FK) | Foreign key to `dim_time` |
| `impact_type_key` | INTEGER (FK) | Foreign key to `dim_impact_type` |
| `value` | FLOAT | Impact value |

---

## Execution Workflow

### Option 1: Full Pipeline (Scraping + Integration)

```bash
# Step 1: Extract data from APIs and web
python scraper.py
# Output: scraped_data.json

# Step 2: Transform and build warehouse
python integrate_data.py
# Output: data_warehouse.json

# Step 3: (Optional) Enrich with innovation data
python fetch_innovation.py
# Updates: data_warehouse_full.json

# Step 4: (Optional) Add comprehensive impact data
python scrape_impacts.py
# Updates: data_warehouse_full.json
```

### Option 2: CSV-Based Pipeline

```bash
# Step 1: Convert CSV to warehouse structure
python create_dw_full.py
# Output: data_warehouse_full.json

# Step 2: (Optional) Enrich with additional data
python fetch_innovation.py
python scrape_impacts.py
```

### Option 3: Kaggle Dataset Download

```bash
# Download datasets from Kaggle
python data.py
# Output: data/global_perf/, data/wdi_2021/
```

### Querying the Warehouse

```bash
# Run query examples
python query_data.py
```

---

## Technical Stack

### Python Libraries
- **requests**: HTTP API calls
- **beautifulsoup4**: Web scraping
- **lxml**: HTML/XML parsing
- **pandas**: Data manipulation (imported but minimal use)
- **json**: JSON file I/O
- **csv**: CSV file reading
- **kaggle**: Kaggle API client
- **urllib**: URL handling
- **ssl**: SSL context management

### Data Formats
- **JSON**: Primary storage format for data warehouse
- **CSV**: Input format for education data
- **API JSON**: World Bank API response format

---

## File Structure

```
Education_ETL_Pipeline/
├── scraper.py                    # Main data extraction script
├── data.py                       # Kaggle dataset downloader
├── create_dw_full.py            # CSV to warehouse converter
├── integrate_data.py            # Star schema builder
├── fetch_innovation.py          # Innovation data enrichment
├── scrape_impacts.py            # Impact data scraper
├── query_data.py                # Query interface
├── README.md                    # Project overview
├── ETL_DOCUMENTATION.md         # This file
├── education_data_final.csv     # Input CSV data
├── scraped_data.json           # Raw scraped data
├── data_warehouse.json         # Basic warehouse (from scraper)
├── data_warehouse_full.json    # Complete warehouse (from CSV + enrichment)
├── DataWarehouse.MultidimensionalSchema.json  # Schema definition
└── tables/                      # Individual table JSON files
    ├── dim_country.json
    ├── dim_time.json
    ├── dim_indicator.json
    ├── dim_impact_type.json
    ├── fact_education_metrics.json
    └── fact_education_impacts.json
```

---

## Data Quality & Limitations

### Data Quality Measures
- **Null Handling**: Filters out null values during extraction
- **Error Handling**: Try-catch blocks prevent pipeline failures
- **Key Integrity**: Surrogate keys ensure referential integrity
- **Data Validation**: Type checking (int, float) during transformation

### Known Limitations
- **Web Scraping**: Limited to 5000 characters per page
- **API Rate Limits**: Batch processing used to avoid limits
- **SSL Verification**: Disabled in `fetch_innovation.py` (may need adjustment)
- **Date Range**: Some scripts hardcode date ranges (1990-2024)
- **Country Coverage**: Initial scraping limited to 6 countries, expanded via CSV

---

## Future Enhancements

1. **Automated Scheduling**: Add cron jobs or task scheduler for regular updates
2. **Database Backend**: Migrate from JSON to SQL database (PostgreSQL, MySQL)
3. **Data Validation**: Add schema validation (JSON Schema, Pydantic)
4. **Incremental Updates**: Support delta loads instead of full reloads
5. **Error Logging**: Implement comprehensive logging system
6. **Data Quality Metrics**: Add data quality scoring and reporting
7. **API Rate Limiting**: Implement proper rate limiting and retry logic
8. **Parallel Processing**: Use multiprocessing for faster data extraction

---

## Summary

This ETL pipeline successfully aggregates education data from **World Bank API**, **Kaggle datasets**, **CSV files**, and **web scraping** into a normalized star schema data warehouse. The system supports both global and country-specific (Tunisia) analysis, tracking education metrics and their socio-economic impacts over time.

**Total Data Sources**: 4 primary sources
- World Bank API (20+ indicators)
- Kaggle (2 datasets)
- CSV file (comprehensive historical data)
- Web scraping (3 websites)

**Data Warehouse**: 2 fact tables, 4 dimension tables, JSON-based storage

**Languages**: Python 3.x

**Dependencies**: requests, beautifulsoup4, lxml, pandas, kaggle

