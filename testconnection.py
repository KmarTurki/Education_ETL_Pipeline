
import pyodbc

# 1. Fill in your details securely
server = 'kmaryesmineetl2025.database.windows.net'
database = 'EDUDW'
username = 'kmarturki'
password = 'NeV<R2Mmj04S'

# 2. Build the connection string
cnxn_str = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
)

# 3. Establish connection
try:
    cnxn = pyodbc.connect(cnxn_str)
    cursor = cnxn.cursor()
    print("Connection Successful!")



except Exception as e:
    print(f"Connection Failed: {e}")