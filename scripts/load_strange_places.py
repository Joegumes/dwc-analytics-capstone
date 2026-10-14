#Dataset import procedure for class

import kagglehub
from pathlib import Path

dataset_path = kagglehub.dataset_download(
    "lucassteuber/strange-places-mysterious-phenomena"
)

print("Downloaded to:", dataset_path)

#import the json file

for file in Path(dataset_path).rglob("*"):
    if file.is_file():
        print(file.relative_to(dataset_path))

        import json

json_file = Path(dataset_path) / "strange_places_v5.2.json"

with json_file.open(encoding="utf-8") as file:
    data = json.load(file)

print("\nTop-level type:", type(data).__name__)

if isinstance(data, dict):
    print("Top-level keys:", list(data.keys())[:20])
    for key, value in list(data.items())[:10]:
        print(key, type(value).__name__)
elif isinstance(data, list):
    print("Number of records:", len(data))
    print("First record:", data[0] if data else "Empty")

#Import the dataset as a dataframe

    import pandas as pd

df = pd.DataFrame(data)

print("\nRows and columns:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nCategories:")
print(df["category"].value_counts().to_string())
print("\nFirst five records:")
print(df.head().to_string(index=False))

#isolate megalithic portals and see which fields are populated

megaliths = df.loc[
    df["category"] == "megalithic_portal"
].copy()

# Remove columns that are empty for every record in this subset
megaliths = megaliths.dropna(axis=1, how="all")

print("\nMegalithic records:", len(megaliths))
print("\nPopulated fields:")
print(megaliths.notna().sum().to_string())
print("\nSample records:")
print(megaliths.head(3).to_string(index=False))

#continued data quality check coordinate quality

# Check coordinates and duplicate records
print("\nCoordinate ranges:")
print(megaliths[["latitude", "longitude"]].agg(["min", "max"]))

invalid_coordinates = (
    ~megaliths["latitude"].between(-90, 90)
    | ~megaliths["longitude"].between(-180, 180)
)

print("\nInvalid coordinates:", invalid_coordinates.sum())
print("Exact duplicate rows:", megaliths.duplicated().sum())

# Check text lengths for SQL column sizing
print("\nMaximum text lengths:")
for column in ["name", "description", "category", "source"]:
    print(column, megaliths[column].astype(str).str.len().max())

print("\nThree sample records:")
print(megaliths.head(3).to_string(index=False))

#drop duplicate records

megaliths = megaliths.drop_duplicates().reset_index(drop=True)
print("Rows ready for upload:", len(megaliths))

from getpass import getpass
from sqlalchemy import create_engine, text, Numeric, Unicode
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

# Keep only the six fields we inspected
upload_df = megaliths[
    ["latitude", "longitude", "name", "description", "category", "source"]
].drop_duplicates().reset_index(drop=True)

password = getpass("SQL admin password: ")

# Safely handle special characters in the password
escaped_password = "{" + password.replace("}", "}}") + "}"

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=tcp:dwc-capstone.database.windows.net,1433;"
    "DATABASE=dwc-capstone;"
    "UID=dwc_sql_admin;"
    f"PWD={escaped_password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=60;"
)

engine = create_engine(
    URL.create(
        "mssql+pyodbc",
        query={"odbc_connect": connection_string},
    ),
    fast_executemany=True,
    poolclass=NullPool,
    hide_parameters=True,
)

try:
    print(f"Uploading {len(upload_df):,} records...", flush=True)

    with engine.begin() as connection:
        upload_df.to_sql(
            name="megalithic_sites",
            schema="dbo",
            con=connection,
            if_exists="fail",
            index=False,
            chunksize=1000,
            dtype={
                "latitude": Numeric(10, 7),
                "longitude": Numeric(10, 7),
                "name": Unicode(150),
                "description": Unicode(1000),
                "category": Unicode(50),
                "source": Unicode(100),
            },
        )

        count = connection.execute(
            text("SELECT COUNT(*) FROM dbo.megalithic_sites")
        ).scalar_one()

        if count != len(upload_df):
            raise ValueError(
                f"Row count mismatch: expected {len(upload_df)}, got {count}"
            )

    print(f"Success! Verified {count:,} rows in dbo.megalithic_sites.")

finally:
    engine.dispose()
    print("Database connection closed.")