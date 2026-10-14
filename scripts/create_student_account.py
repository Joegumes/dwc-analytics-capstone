import pyodbc
from getpass import getpass

admin_password = getpass("SQL admin password: ")
student_password = getpass("Create a student SQL password: ")
confirmation = getpass("Confirm student SQL password: ")

if student_password != confirmation:
    raise ValueError("Student passwords do not match.")

def odbc_value(value):
    return "{" + value.replace("}", "}}") + "}"

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=tcp:dwc-capstone.database.windows.net,1433;"
    "DATABASE=dwc-capstone;"
    "UID=dwc_sql_admin;"
    f"PWD={odbc_value(admin_password)};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=60;"
)

sql_password = student_password.replace("'", "''")
connection = None

try:
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    cursor.execute(
        "CREATE USER [dwc_student_readonly] "
        f"WITH PASSWORD = '{sql_password}';"
    )
    cursor.execute("GRANT CONNECT TO [dwc_student_readonly];")
    cursor.execute(
        "GRANT SELECT ON OBJECT::dbo.megalithic_sites "
        "TO [dwc_student_readonly];"
    )

    connection.commit()
    print("Student account created with read access.")
    cursor.close()

except:
    if connection is not None:
        connection.rollback()
    raise

finally:
    if connection is not None:
        connection.close()
    print("Database connection closed.")