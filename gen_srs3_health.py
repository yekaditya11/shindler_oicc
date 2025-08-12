import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

EXCEL_PATH = os.path.join('shindler_server', 'sanitize_SRS - Augmented (Employee Details)[39] 1.xlsx')
OUTPUT_PATH = 'srs3.health.json'

if not os.path.exists(EXCEL_PATH):
    raise SystemExit(f"Excel file not found: {EXCEL_PATH}")

# Load and normalize
try:
    df = pd.read_excel(EXCEL_PATH)
except Exception as e:
    raise SystemExit(f"Failed to read Excel: {e}")

# Treat empty strings as NaN
df = df.replace({None: np.nan})
df = df.applymap(lambda v: (np.nan if isinstance(v, str) and v.strip() == '' else v))

columns = list(df.columns)

# Completeness per column
completeness_pct = {c: round(float(df[c].notna().mean() * 100.0), 2) for c in columns}
missing_counts = {c: int(df[c].isna().sum()) for c in columns}

# Priority rules
critical_columns = {
    'event_id', 'reported_date', 'date_of_unsafe_event',
    'employee_id', 'serious_near_miss'
}

def priority_from_score(col_name: str, score: float) -> str:
    if col_name in critical_columns:
        return 'critical'
    if score >= 95:
        return 'high'
    if score >= 85:
        return 'medium'
    if score >= 70:
        return 'low'
    return 'low'

column_analysis = {}
for col in columns:
    score = int(round(completeness_pct[col])) if not np.isnan(completeness_pct[col]) else 0
    column_analysis[col] = {
        'overall_column_score': score,
        'priority': priority_from_score(col, score),
        'dimensions_checked': ['completeness'],
        'dimensions_skipped': ['uniqueness', 'consistency', 'validity', 'timeliness'],
        'issues': [f"{missing_counts[col]} missing values"]
    }

# Overall/Dimensions
avg_completeness = round(float(np.nanmean(list(completeness_pct.values()))), 2) if len(completeness_pct) > 0 else 0.0
overall_score = int(round(avg_completeness))
if overall_score >= 90:
    grade = 'Excellent'
elif overall_score >= 75:
    grade = 'Good'
elif overall_score >= 60:
    grade = 'Fair'
else:
    grade = 'Poor'

health = {
    'overall_health': {
        'score': overall_score,
        'grade': grade,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    },
    'dimensions': {
        'completeness': {
            'score': overall_score,
            'columns_assessed': len(columns)
        },
        'uniqueness': {
            'score': 0,
            'columns_assessed': 0
        },
        'consistency': {
            'score': 0,
            'columns_assessed': 0
        },
        'validity': {
            'score': 0,
            'columns_assessed': 0
        },
        'timeliness': {
            'score': 0,
            'columns_assessed': 0
        }
    },
    'column_analysis': column_analysis
}

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(health, f, indent=2, ensure_ascii=False)

print(f"{OUTPUT_PATH} written")


