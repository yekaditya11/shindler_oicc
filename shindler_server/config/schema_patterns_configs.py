    # Expected column patterns for each file type - using exact column names from Excel files
SCHEMA_PATTERNS = {
        "ei_tech": [
            "Event ID", "Reporter Name", "Manager Name", "branch", "Reported Date",
            "Reporter ID", "Date Of Unsafe Event", "Time", "Time of unsafe event",
            "Unsafe Event Type", "Business Details", "Site Reference", "Unsafe Event location",
            "Product Type", "Employee ID", "Employee Name", "Subcontractor Company Name",
            "SubcontractorID", "Subcontractor CITY", "Subcontractor Name", "KG Name",
            "Country Name", "Division", "Department", "City", "Sub-Area", "District",
            "Zone", "Serious Near Miss", "Unsafe Act", "Unsafe Act other",
            "Unsafe Condition", "Unsafe Condition other", "Work Stopped",
            "Stop Work NOGO Violation", "NOGO Violation detail", "Stop Work Duration",
            "Other Safety Issues", "Comments/Remarks", "Event requires sanction",
            "Action Description 1", "Action Description 2", "Action Description 3",
            "Action Description 4", "Action Description 5", "Image", "Status", "Region"
        ],
        "srs": [
            "Event Id", "Reporter Name", "Reported Date", "Reporter ID",
            "Date Of Unsafe Event", "Time of unsafe event", "Unsafe Event Type",
            "Business Details", "Site Reference", "Unsafe Event location", "Product Type",
            "Employee ID", "Employee Name", "Subcontractor Company Name", "SubcontractorID",
            "Subcontractor CITY", "Subcontractor Name", "KG Name", "Country Name",
            "Division", "Department", "City", "Sub-Area", "District", "Zone",
            "Serious Near Miss", "Unsafe Act", "Unsafe Act other", "Unsafe Condition",
            "Unsafe Condition other", "Work Stopped", "Stop Work NOGO Violation",
            "NOGO Violation detail", "Stop Work Duration", "Other Safety Issues",
            "Comments/Remarks", "Event requires sanction", "Action Description 1",
            "Action Description 2", "Action Description 3", "Action Description 4",
            "Action Description 5", "Branch", "Region"
        ],
        "ni_tct": [
            "Reporting ID", "Status_Key", "Status", "Location_Key", "Location",
            "Branch_Key", "No", "Branch Name", "Region_Key", "Region",
            "Reporter SAP ID", "Reporter Name", "Designation_Key", "Designation",
            "GL ID_Key", "GL ID", "PE ID_Key", "PE ID", "Created On",
            "Date and Time of Unsafe Event", "Type Of Unsafe Event_Key",
            "Type Of Unsafe Event", "Unsafe Event Details_Key", "Unsafe Event Details",
            "Action Related to High Risk Situation_Key", "Action Related to High Risk Situation",
            "Business Details_Key", "Business Details", "Site Name", "Site Reference_Key",
            "Site Reference", "Product Type_Key", "Product Type", "Persons Involved",
            "Work Was Stopped_Key", "Work Was Stopped", "Work Stopped Hours",
            "No Go Violation_Key", "No Go Violation", "Job No", "Additional Comments",
            "Has Attachment", "Attachment"
        ],
        "ni_tct_augmented": [
            # Original NI TCT columns (43)
            "Reporting ID", "Status_Key", "Status", "Location_Key", "Location",
            "Branch_Key", "No", "Branch Name", "Region_Key", "Region",
            "Reporter SAP ID", "Reporter Name", "Designation_Key", "Designation",
            "GL ID_Key", "GL ID", "PE ID_Key", "PE ID", "Created On",
            "Date and Time of Unsafe Event", "Type Of Unsafe Event_Key",
            "Type Of Unsafe Event", "Unsafe Event Details_Key", "Unsafe Event Details",
            "Action Related to High Risk Situation_Key", "Action Related to High Risk Situation",
            "Business Details_Key", "Business Details", "Site Name", "Site Reference_Key",
            "Site Reference", "Product Type_Key", "Product Type", "Persons Involved",
            "Work Was Stopped_Key", "Work Was Stopped", "Work Stopped Hours",
            "No Go Violation_Key", "No Go Violation", "Job No", "Additional Comments",
            "Has Attachment", "Attachment",
            # Augmented columns (15)
            # Weather data (4 columns)
            "weather_weather_condition", "weather_temperature_celsius",
            "weather_humidity_percent", "weather_weather_severity_score",
            # Employee data (6 columns)
            "employee_employee_age", "employee_experience_level", "employee_years_of_experience",
            "employee_safety_training_hours", "employee_last_training_date", "employee_shift_type",
            # Site risk data (2 columns)
            "site_site_risk_category", "site_last_safety_audit_days",
            # Workload metrics (3 columns)
            "workload_workload_category", "workload_team_size", "workload_work_duration_hours"
        ]
    }
    