# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

# Categorized data structure
data_output = {
    "global": {},
    "tunisia": {},
    "factors": {},
    "impacts": {}
}

# World Bank API base URL
WB_API_BASE = "http://api.worldbank.org/v2/country/{}/indicator/{}?format=json&per_page=1000"

# Indicators for global education
global_indicators = {
    "literacy_rate": "SE.ADT.LITR.ZS",  # Literacy rate, adult total (% of people ages 15 and above)
    "enrollment_primary": "SE.PRM.ENRR",  # School enrollment, primary (% gross)
    "enrollment_secondary": "SE.SEC.ENRR",  # School enrollment, secondary (% gross)
    "graduation_rate": "SE.SEC.CMPT.LO.ZS",  # Lower secondary completion rate, total (% of relevant age group)
    "dropout_rate": "SE.PRM.UNER.ZS"  # Children out of school, primary
}

# Countries for comparison
countries = ["USA", "CHN", "IND", "TUN", "FRA", "DEU"]

# Tunisia-specific indicators
tunisia_indicators = {
    "infrastructure": "SE.PRM.TCHR",  # Pupil-teacher ratio in primary education
    "teacher_quality": "SE.PRM.TCHR.FE.ZS",  # Female teachers in primary education (% of total)
    "budget": "SE.XPD.TOTL.GD.ZS",  # Government expenditure on education, total (% of GDP)
    "mental_health": "SH.STA.SUIC.P5"  # Suicide mortality rate (per 100,000 population) - proxy for mental health
}

# Influencing factors indicators
factors_indicators = {
    "curriculum": "SE.PRM.CUAT.ZS",  # Education time (years)
    "school_environment": "SE.PRM.UNER.ZS",  # Out-of-school children
    "socio_economic": "SI.POV.GINI"  # GINI index (World Bank estimate)
}

# Impacts indicators
impacts_indicators = {
    "innovation": "IP.PAT.RESD",  # Patent applications, residents
    "civic_awareness": "EG.ELC.ACCS.ZS",  # Access to electricity (% of population) - proxy for development
    "employment": "SL.UEM.TOTL.ZS"  # Unemployment, total (% of total labor force)
}

def scrape_wb_api(country, indicator):
    """Scrape data from World Bank API."""
    url = WB_API_BASE.format(country, indicator)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if len(data) > 1 and data[1]:
            return [{"year": item["date"], "value": item["value"]} for item in data[1] if item["value"] is not None]
        return []
    except Exception as e:
        print(f"Error fetching {indicator} for {country}: {e}")
        return []

def scrape_web_text(url):
    """Scrape text from web pages."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        text = soup.get_text(separator="\n", strip=True)
        return text[:5000]
    except Exception as e:
        return f"Error: {e}"

# Scrape global education data
print("Scraping global education data...")
for country in countries:
    data_output["global"][country] = {}
    for key, indicator in global_indicators.items():
        print(f"Fetching {key} for {country}...")
        data_output["global"][country][key] = scrape_wb_api(country, indicator)

# Scrape Tunisia-specific data
print("Scraping Tunisia-specific data...")
for key, indicator in tunisia_indicators.items():
    print(f"Fetching {key} for Tunisia...")
    data_output["tunisia"][key] = scrape_wb_api("TUN", indicator)

# Scrape influencing factors
print("Scraping influencing factors...")
for key, indicator in factors_indicators.items():
    print(f"Fetching {key}...")
    data_output["factors"][key] = scrape_wb_api("TUN", indicator)  # Focus on Tunisia for factors

# Scrape impacts
print("Scraping impacts...")
for key, indicator in impacts_indicators.items():
    print(f"Fetching {key}...")
    data_output["impacts"][key] = scrape_wb_api("TUN", indicator)  # Focus on Tunisia for impacts

# Additional web scraping for unstructured data
web_urls = {
    "tunisia_ministry": "https://www.education.gov.tn/",  # Tunisian Ministry of Education (example URL)
    "unesco_global": "https://en.unesco.org/themes/education",
    "oecd_education": "https://www.oecd.org/education/"
}

print("Scraping additional web data...")
for key, url in web_urls.items():
    print(f"Scraping {key}...")
    data_output["web_data"] = data_output.get("web_data", {})
    data_output["web_data"][key] = scrape_web_text(url)

# Save to JSON
with open("scraped_data.json", "w", encoding="utf-8") as f:
    json.dump(data_output, f, indent=4, ensure_ascii=False)

print("Scraping completed. File saved as scraped_data.json")

