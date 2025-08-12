import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import re

# === CONFIG ===
EXCEL_FILE = "Unsafe Event- NI TCT App - Filled 1.xlsx"  # Update with your actual file name
SHEET_NAME = "Sheet1"  # Update with your actual sheet name

DB_CONFIG = {
    "host": "schindler-safetyconnect.ccgjylc7uxqb.us-east-1.rds.amazonaws.com",
    "port": "5432",
    "dbname": "postgres",
    "user": "postgres",
    "password": "IxIKjgGrN46KOKLne06m"
}

# === NORMALIZATION FUNCTION ===
def normalize_col(col):
    """Convert column name to lowercase with underscores, remove special chars."""
    return re.sub(r'[^a-z0-9_]', '_', col.strip().lower().replace(" ", "_"))

# === LOAD SHEET ===
df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

# Normalize column names
df.columns = [normalize_col(c) for c in df.columns]

# === SQL TABLE COLUMN LIST ===
sql_columns = [
    "reporting_id", "status_key", "status", "location_key", "location", "branch_key", "no",
    "branch_name", "region_key", "region", "reporter_sap_id", "reporter_name", "designation_key",
    "designation", "gl_id_key", "gl_id", "pe_id_key", "pe_id", "created_on", "date_and_time_of_unsafe_event",
    "type_of_unsafe_event_key", "type_of_unsafe_event", "unsafe_event_details_key", "unsafe_event_details",
    "action_related_to_high_risk_situation_key", "action_related_to_high_risk_situation", "business_details_key",
    "business_details", "site_name", "site_reference_key", "site_reference", "product_type_key", "product_type",
    "persons_involved", "work_was_stopped_key", "work_was_stopped", "work_stopped_hours", "no_go_violation_key",
    "no_go_violation", "job_no", "additional_comments", "has_attachment", "attachment", "db_uploaded_date"
]

# Add missing columns as empty
missing_in_excel = [col for col in sql_columns if col not in df.columns]
if missing_in_excel:
    print("⚠ Missing columns in Excel (added as empty):", missing_in_excel)
    for col in missing_in_excel:
        if col == 'db_uploaded_date':
            # Set db_uploaded_date to current timestamp
            df[col] = datetime.now()
        else:
            df[col] = ""

# Keep only SQL columns (in correct order)
df = df[sql_columns]

# === CLEANING ===
def parse_date(val):
    if pd.isna(val) or val == "":
        return None  # NULL in DB
    if isinstance(val, datetime):
        return val
    try:
        return pd.to_datetime(val)
    except:
        return None

# Date columns get None, text gets ""
date_cols = ["created_on", "date_and_time_of_unsafe_event"]
for col in df.columns:
    if col in date_cols:
        # For date columns, convert empty string to None (NULL in DB)
        df[col] = df[col].apply(lambda x: parse_date(x) if x != "" else None)
    else:
        df[col] = df[col].fillna("")

# === INSERT INTO DATABASE ===
insert_query = f"""
INSERT INTO unsafe_events_ni_tct_enriched ({", ".join(sql_columns)})
VALUES %s
"""

values = [tuple(row) for row in df.to_numpy()]

# Establish database connection
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Execute batch insert using execute_values for efficiency
execute_values(cur, insert_query, values)

# Commit and close connection
conn.commit()
cur.close()
conn.close()

print(f"✅ Inserted {len(values)} rows into unsafe_events_ni_tct.")
