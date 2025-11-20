📈 Project Overview:

Data Warehouse for Education Analysis
This repository hosts a sophisticated Extract, Transform, Load (ETL) pipeline designed to build a consolidated data warehouse for analyzing global education metrics, with a specialized focus on Tunisia.

The project demonstrates end-to-end Data Engineering proficiency, from multi-source data acquisition to the final modeling of a structured Star Schema for analytical querying.

 Key Features
Multi-Source Data Ingestion: Automated data collection from Kaggle APIs (World Bank datasets) and External APIs (World Bank, UNESCO, OECD).

Categorized Extraction: Data is systematically categorized into Global, Tunisia-Specific, Influencing Factors, and Impacts (e.g., employment, innovation).

Data Warehouse Modeling: Implementation of a Star Schema with two main Fact Tables (education_metrics, impacts) and several dimensions.

Robust Data Handling: Includes custom error handling and filtering logic to process large, raw CSVs and structure nested API responses.

 Technology Stack
Component	Tool / Language	Purpose
Language	Python 3.x	Core language for ETL scripts.
Processing	Pandas	Data cleaning, transformation, and structural mapping.
Data Sources	Kaggle API, World Bank API, requests	Automated data extraction.
Web Scraping	BeautifulSoup	Unstructured text data extraction from web pages (e.g., Ministry sites).
Output	JSON	Intermediate and final data warehouse storage format.

 Data Sources and Extraction (scraper.py & data.py)
The pipeline pulls data from the following diverse sources:

1. APIs and Structured Sources
Source	Datasets	Target Data
Kaggle	World Bank EdStats, World Development Indicators (WDI)	Historical global education metrics (literacy, enrollment).
World Bank API	Specific indicators (via scraper.py)	Real-time data for Tunisia and global comparison countries (USA, FRA, etc.).
External URLs	UNESCO, OECD, Tunisian Ministry of Education	Unstructured textual data on policy and context.

2. Extraction Logic
data.py: Handles bulk download and unzipping of large Kaggle datasets, followed by basic filtering based on indicator name keywords (literacy, enrollment).

scraper.py: Fetches specific, current indicators via the World Bank API, organizing data into four main categories: global, tunisia, factors, and impacts.

 Data Warehouse Architecture and Model
The integrated data is modeled into a Star Schema, focusing on analytical efficiency:

Fact Tables
Table Name	Granularity / Purpose	Keys/Fields
fact_education_metrics	Education indicators by Country and Year.	country, year, indicator, value
fact_impacts	Metrics related to educational outcomes.	country, year, indicator (innovation, employment), value

Dimensions
countries: List of all countries included (e.g., TUN, USA, CHN, IND).

years: Time dimension from 2000 to 2024.

indicator_types: Detailed list of all measured metrics.

 How to Run the ETL Pipeline
These instructions assume you have Python 3.x and a Virtual Environment set up.

1. Setup
Clone the repository:

Bash

git clone https://github.com/YourUsername/Education-ETL-Pipeline.git
cd Education-ETL-Pipeline
Install Dependencies: (Ensure you have a requirements.txt file with pandas, requests, kaggle, beautifulsoup4, lxml)

Bash

pip install -r requirements.txt
Kaggle Credentials: Place your kaggle.json file in the root directory for API authentication.

2. Execution
Run the scripts in sequence to build the warehouse:

Download Kaggle Data:

Bash

python data.py
Scrape World Bank/APIs:

Bash

python scraper.py
Integrate and Model: This step merges all scraped data, Kaggle data, and transforms it into the final warehouse structure (data_warehouse.json).

Bash

python integrate_data.py
The final, structured output will be saved as data_warehouse.json.
