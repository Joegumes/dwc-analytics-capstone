# dwc-analytics-capstone
# DWC Analytics Capstone

A class project connecting Python, Azure SQL, and Power BI to explore ancient sites around the world.

## Dataset

Source: [Strange Places on Kaggle](https://www.kaggle.com/datasets/lucassteuber/strange-places-mysterious-phenomena).

The initial load used dataset version 13, file `strange_places_v5.2.json`.

We selected the `megalithic_portal` category and removed three exact duplicate records, leaving 60,025 rows.

Fields: latitude, longitude, name, description, category, source.

Records include different archaeological site types, not exclusively megalithic structures. Source descriptions may be truncated. Dataset files are not included in this repository; consult the source's licensing and attribution terms before redistribution.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/load_strange_places.py` | Download, inspect, clean, and upload data. Instructor only; requires SQL admin credentials. |
| `scripts/test_sql_connection.py` | Test the administrator connection. Instructor only. |
| `scripts/create_student_account.py` | Create the read-only student account. Instructor only; run once. |
| `scripts/test_student_access.py` | Verify student access and table permissions. |

The loader downloads the latest dataset version, so future results may differ. It stops if the destination table already exists.

## Python setup on macOS

From the repository folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Install Microsoft ODBC Driver 18 for SQL Server separately. It requires unixODBC and OpenSSL.

On the instructor's Apple Silicon Mac, SQL scripts require this library path:

```bash
DYLD_LIBRARY_PATH="/opt/homebrew/opt/openssl@3/lib" python -u scripts/test_student_access.py
```

This path is machine-specific and may differ on other computers.

## Student database access

- Server: `dwc-capstone.database.windows.net`
- Port: `1433`
- Database: `dwc-capstone`
- Username: `dwc_student_readonly`
- Table: `dbo.megalithic_sites`

Obtain the student password from the instructor. Your public IPv4 address must be added to the server firewall before connecting.

In DBeaver, use SQL Server Authentication and specify the database explicitly.

```sql
SELECT TOP (5) name, latitude, longitude
FROM dbo.megalithic_sites;
```

Student SELECT access was verified; INSERT, UPDATE, and DELETE permissions on the table were absent.

## Compute and cost controls

- Free-limit behavior: auto-pause until next month.
- Microsoft Defender for SQL: not enabled.
- Power BI uses Import mode.
- Scheduled refresh remains off for the static dataset.
- Refresh manually when source data changes or for a planned demonstration.
- Disconnect SQL tools after use so the database can become idle.

## Credentials

Passwords are entered locally through prompts. Do not commit passwords, credential notes, API tokens, or `.env` files.