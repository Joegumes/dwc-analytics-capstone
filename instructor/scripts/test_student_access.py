import pyodbc
from getpass import getpass

password = getpass("Student SQL password: ")
escaped_password = "{" + password.replace("}", "}}") + "}"

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=tcp:dwc-capstone.database.windows.net,1433;"
    "DATABASE=dwc-capstone;"
    "UID=dwc_student_readonly;"
    f"PWD={escaped_password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=60;"
)

connection = None

try:
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            USER_NAME(),
            HAS_PERMS_BY_NAME(
                'dbo.megalithic_sites', 'OBJECT', 'SELECT'
            ),
            HAS_PERMS_BY_NAME(
                'dbo.megalithic_sites', 'OBJECT', 'INSERT'
            ),
            HAS_PERMS_BY_NAME(
                'dbo.megalithic_sites', 'OBJECT', 'UPDATE'
            ),
            HAS_PERMS_BY_NAME(
                'dbo.megalithic_sites', 'OBJECT', 'DELETE'
            )
    """)

    permissions = tuple(cursor.fetchone())
    print("User, SELECT, INSERT, UPDATE, DELETE:", permissions)

    cursor.execute("SELECT COUNT(*) FROM dbo.megalithic_sites")
    print("Rows accessible:", cursor.fetchone()[0])

    if permissions == ("dwc_student_readonly", 1, 0, 0, 0):
        print("PASS: Student can read the table but cannot modify its data.")
    else:
        print("CHECK: Permissions differ from the expected read-only setup.")

    cursor.close()

finally:
    if connection is not None:
        connection.close()
        print("Database connection closed.")
