import pyodbc
from getpass import getpass

# Escape special characters for the ODBC connection string
def odbc_value(value):
    return "{" + value.replace("}", "}}") + "}"

password = getpass("SQL admin password: ")

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=tcp:dwc-capstone.database.windows.net,1433;"
    "DATABASE=dwc-capstone;"
    "UID=dwc_sql_admin;"
    f"PWD={odbc_value(password)};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=60;"
)

connection = None

try:
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    cursor.execute("SELECT DB_NAME()")
    print("Connected successfully to:", cursor.fetchone()[0])
    cursor.close()
finally:
    if connection is not None:
        connection.close()
        
print("This file is running!")

from getpass import getpass
password = getpass("SQL admin password: ")
print("Password received.")
