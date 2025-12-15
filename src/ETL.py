import pyodbc
import json
import os

# Database Connection Details
SERVER = 'kmaryesmineetl2025.database.windows.net'
DATABASE = 'EDUDW'
USERNAME = 'kmarturki'
PASSWORD = 'NeV<R2Mmj04S'

connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

def create_tables(cursor):
    """Creates the dimension and fact tables if they do not exist."""
    print("Creating tables...")
    
    # Dimensions
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.dim_country') AND type in (N'U'))
    CREATE TABLE dbo.dim_country (
      country_key INT PRIMARY KEY,
      country_code NVARCHAR(50),
      country_name NVARCHAR(255),
      region NVARCHAR(255)
    );
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.dim_time') AND type in (N'U'))
    CREATE TABLE dbo.dim_time (
      time_key INT PRIMARY KEY,
      year INT NULL,
      quarter INT NULL,
      semester INT NULL,
      decade INT NULL,
      is_current_year BIT NULL,
      fiscal_year INT NULL
    );
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.dim_indicator') AND type in (N'U'))
    CREATE TABLE dbo.dim_indicator (
      indicator_key INT PRIMARY KEY,
      indicator_name NVARCHAR(255),
      indicator_category NVARCHAR(255),
      indicator_code NVARCHAR(100)
    );
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.dim_impact_type') AND type in (N'U'))
    CREATE TABLE dbo.dim_impact_type (
      impact_type_key INT PRIMARY KEY,
      impact_name NVARCHAR(255),
      impact_category NVARCHAR(255),
      impact_code NVARCHAR(100)
    );
    """)

    # Facts
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.fact_education_metrics') AND type in (N'U'))
    CREATE TABLE dbo.fact_education_metrics (
      metric_id INT PRIMARY KEY,
      country_key INT,
      time_key INT,
      indicator_key INT,
      value FLOAT,
      CONSTRAINT FK_metrics_country FOREIGN KEY (country_key) REFERENCES dbo.dim_country(country_key),
      CONSTRAINT FK_metrics_time FOREIGN KEY (time_key) REFERENCES dbo.dim_time(time_key),
      CONSTRAINT FK_metrics_indicator FOREIGN KEY (indicator_key) REFERENCES dbo.dim_indicator(indicator_key)
    );
    """)

    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.fact_education_impacts') AND type in (N'U'))
    CREATE TABLE dbo.fact_education_impacts (
      impact_id INT PRIMARY KEY,
      country_key INT,
      time_key INT,
      impact_type_key INT,
      value FLOAT,
      CONSTRAINT FK_impacts_country FOREIGN KEY (country_key) REFERENCES dbo.dim_country(country_key),
      CONSTRAINT FK_impacts_time FOREIGN KEY (time_key) REFERENCES dbo.dim_time(time_key),
      CONSTRAINT FK_impacts_type FOREIGN KEY (impact_type_key) REFERENCES dbo.dim_impact_type(impact_type_key)
    );
    """)
    print("Tables created (if not existed).")

def load_data(cursor, json_file_path):
    """Loads data from the JSON file into the tables."""
    print(f"Loading data from {json_file_path}...")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. dim_country
    if 'dim_country' in data:
        print("Inserting dim_country...")
        rows = []
        for item in data['dim_country']:
            rows.append((item['country_key'], item['country_code'], item['country_name'], item['region']))
        
        cursor.fast_executemany = True
        try:
            cursor.executemany("INSERT INTO dbo.dim_country (country_key, country_code, country_name, region) VALUES (?, ?, ?, ?)", rows)
        except pyodbc.IntegrityError:
            print("Skipping dim_country (PK violation similar). Assuming loaded.")

    # 2. dim_time
    if 'dim_time' in data:
        print("Inserting dim_time...")
        rows = []
        for item in data['dim_time']:
            rows.append((item['time_key'], item['year'], item['quarter'], item['semester'], item['decade'], item['is_current_year'], item['fiscal_year']))
        try:
            cursor.executemany("INSERT INTO dbo.dim_time (time_key, year, quarter, semester, decade, is_current_year, fiscal_year) VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
        except pyodbc.IntegrityError:
            print("Skipping dim_time.")

    # 3. dim_indicator
    if 'dim_indicator' in data:
        print("Inserting dim_indicator...")
        rows = []
        for item in data['dim_indicator']:
            rows.append((item['indicator_key'], item['indicator_name'], item['indicator_category'], item['indicator_code']))
        try:
            cursor.executemany("INSERT INTO dbo.dim_indicator (indicator_key, indicator_name, indicator_category, indicator_code) VALUES (?, ?, ?, ?)", rows)
        except pyodbc.IntegrityError:
            print("Skipping dim_indicator.")

    # 4. dim_impact_type
    if 'dim_impact_type' in data:
        print("Inserting dim_impact_type...")
        rows = []
        for item in data['dim_impact_type']:
            rows.append((item['impact_type_key'], item['impact_name'], item['impact_category'], item['impact_code']))
        try:
            cursor.executemany("INSERT INTO dbo.dim_impact_type (impact_type_key, impact_name, impact_category, impact_code) VALUES (?, ?, ?, ?)", rows)
        except pyodbc.IntegrityError:
            print("Skipping dim_impact_type.")

    # 5. fact_education_metrics
    if 'fact_education_metrics' in data:
        print("Inserting fact_education_metrics...")
        rows = []
        for item in data['fact_education_metrics']:
            rows.append((item['metric_id'], item['country_key'], item['time_key'], item['indicator_key'], item['value']))
        try:
            cursor.executemany("INSERT INTO dbo.fact_education_metrics (metric_id, country_key, time_key, indicator_key, value) VALUES (?, ?, ?, ?, ?)", rows)
        except pyodbc.IntegrityError:
            print("Skipping fact_education_metrics.")

    # 6. fact_education_impacts
    if 'fact_education_impacts' in data:
        print("Inserting fact_education_impacts...")
        rows = []
        for item in data['fact_education_impacts']:
            rows.append((item['impact_id'], item['country_key'], item['time_key'], item['impact_type_key'], item['value']))
        try:
            cursor.executemany("INSERT INTO dbo.fact_education_impacts (impact_id, country_key, time_key, impact_type_key, value) VALUES (?, ?, ?, ?, ?)", rows)
        except pyodbc.IntegrityError:
            print("Skipping fact_education_impacts.")

    print("Data insertion complete.")

def main():
    try:
        print("Connecting to database...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print("Connection successful.")

        create_tables(cursor)
        
        load_data(cursor, '../data/data_warehouse.json')
        
        conn.commit()
        print("Transaction committed.")
        
    except pyodbc.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
            print("Transaction rolled back.")
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    main()
