import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import re

# === CONFIG ===
EXCEL_FILE = "Unsafe Event - EI Tech App - Filled 1.xlsx"
SHEET_NAME = "2025"

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
    "event_id", "reporter_name", "manager_name", "branch", "reported_date",
    "reporter_id", "date_of_unsafe_event", "time", "time_of_unsafe_event",
    "unsafe_event_type", "business_details", "site_reference", "unsafe_event_location",
    "product_type", "employee_id", "employee_name", "subcontractor_company_name",
    "subcontractor_id", "subcontractor_city", "subcontractor_name", "kg_name",
    "country_name", "division", "department", "city", "sub_area", "district", "zone",
    "serious_near_miss", "unsafe_act", "unsafe_act_other", "unsafe_condition",
    "unsafe_condition_other", "work_stopped", "stop_work_nogo_violation",
    "nogo_violation_detail", "stop_work_duration", "other_safety_issues",
    "comments_remarks", "event_requires_sanction", "action_description_1",
    "action_description_2", "action_description_3", "action_description_4",
    "action_description_5", "image", "status", "region"
]

# Add missing columns as empty
missing_in_excel = [col for col in sql_columns if col not in df.columns]
if missing_in_excel:
    print("⚠ Missing columns in Excel (added as empty):", missing_in_excel)
    for col in missing_in_excel:
        df[col] = ""

# Keep only SQL columns (in correct order)
df = df[sql_columns]

# === CLEANING ===
def parse_date(val):
    if pd.isna(val) or val == "":
        return None  # NULL in DB
    if isinstance(val, datetime):
        return val.date()
    try:
        return pd.to_datetime(val).date()
    except:
        return None

# Date columns get None, text gets ""
date_cols = ["reported_date", "date_of_unsafe_event"]
for col in df.columns:
    if col in date_cols:
        df[col] = df[col].apply(parse_date)
    else:
        df[col] = df[col].fillna("")

# === INSERT INTO DATABASE ===
insert_query = f"""
INSERT INTO unsafe_events_ei_tech_enriched ({", ".join(sql_columns)})
VALUES %s
"""

values = [tuple(row) for row in df.to_numpy()]

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

execute_values(cur, insert_query, values)

conn.commit()
cur.close()
conn.close()

print(f"✅ Inserted {len(values)} rows into unsafe_events_ei_tech.")
