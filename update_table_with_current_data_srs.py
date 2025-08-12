import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# === CONFIG ===
EXCEL_FILE ="Unsafe Event Dump - SRS - Unfilled 1.xlsx"
SHEET_NAME = 0  # Change to your sheet index or name
DB_CONFIG = {
    "host": "schindler-safetyconnect.ccgjylc7uxqb.us-east-1.rds.amazonaws.com",
    "port": "5432",
    "dbname": "postgres",
    "user": "postgres",
    "password": "IxIKjgGrN46KOKLne06m"
}
TABLE_NAME = "unsafe_events_srs"

# === STEP 1: Read Excel ===
df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

# === STEP 2: Normalize column names ===
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# === STEP 3: Match columns with database schema ===
db_columns = [
    "event_id", "reporter_name", "reported_date", "reporter_id", "date_of_unsafe_event",
    "time_of_unsafe_event", "unsafe_event_type", "business_details", "site_reference",
    "unsafe_event_location", "product_type", "employee_id", "employee_name",
    "subcontractor_company_name", "subcontractor_id", "subcontractor_city", "subcontractor_name",
    "kg_name", "country_name", "division", "department", "city", "sub_area", "district", "zone",
    "serious_near_miss", "unsafe_act", "unsafe_act_other", "unsafe_condition", "unsafe_condition_other",
    "work_stopped", "stop_work_nogo_violation", "nogo_violation_detail", "stop_work_duration",
    "other_safety_issues", "comments_remarks", "event_requires_sanction",
    "action_description_1", "action_description_2", "action_description_3",
    "action_description_4", "action_description_5", "branch", "region"
]

# Keep only matching columns
df = df[[col for col in db_columns if col in df.columns]]

# === STEP 4: Connect to PostgreSQL ===
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# === STEP 5: Insert data ===
cols_str = ",".join(df.columns)
placeholders = "%s"
insert_query = f"INSERT INTO {TABLE_NAME} ({cols_str}) VALUES %s"

# Convert DataFrame to list of tuples
data_tuples = [tuple(x) for x in df.to_numpy()]

# Bulk insert
execute_values(cur, insert_query, data_tuples)

# Commit & close
conn.commit()
cur.close()
conn.close()

print(f"✅ Inserted {len(df)} rows into {TABLE_NAME}")
