"""
Database models for unsafe event data from different Excel file types
Complete models matching ALL columns from Excel files
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Date
from models.base_models import BaseModel
from sqlalchemy.sql import func

class UnsafeEventEITech(BaseModel):
    """Model for EI Tech App unsafe events - ALL 54 columns"""
    __tablename__ = "unsafe_events_ei_tech"

    # Column 1-6: Core identification
    event_id = Column(Integer, nullable=True, index=True)  # Event ID
    reporter_name = Column(String(255), nullable=True)  # Reporter Name
    manager_name = Column(String(255), nullable=True)  # Manager Name
    branch = Column(String(255), nullable=True)  # branch
    reported_date = Column(Date, nullable=True)  # Reported Date
    reporter_id = Column(String(100), nullable=True)  # Reporter ID

    # Column 7-12: Event timing and details
    date_of_unsafe_event = Column(Date, nullable=True)  # Date Of Unsafe Event
    time = Column(String(50), nullable=True)  # Time
    time_of_unsafe_event = Column(String(50), nullable=True)  # Time of unsafe event
    unsafe_event_type = Column(String(255), nullable=True)  # Unsafe Event Type
    business_details = Column(String(255), nullable=True)  # Business Details
    site_reference = Column(Text, nullable=True)  # Site Reference

    # Column 13-20: Location and product
    unsafe_event_location = Column(String(255), nullable=True)  # Unsafe Event location
    product_type = Column(String(255), nullable=True)  # Product Type
    employee_id = Column(String(100), nullable=True)  # Employee ID
    employee_name = Column(String(255), nullable=True)  # Employee Name
    subcontractor_company_name = Column(String(255), nullable=True)  # Subcontractor Company Name
    subcontractor_id = Column(String(100), nullable=True)  # SubcontractorID
    subcontractor_city = Column(String(255), nullable=True)  # Subcontractor CITY
    subcontractor_name = Column(String(255), nullable=True)  # Subcontractor Name

    # Column 21-28: Location hierarchy
    kg_name = Column(String(100), nullable=True)  # KG Name
    country_name = Column(String(100), nullable=True)  # Country Name
    division = Column(String(255), nullable=True)  # Division
    department = Column(String(255), nullable=True)  # Department
    city = Column(String(255), nullable=True)  # City
    sub_area = Column(String(100), nullable=True)  # Sub-Area
    district = Column(String(255), nullable=True)  # District
    zone = Column(String(255), nullable=True)  # Zone

    # Column 29-33: Event classification
    serious_near_miss = Column(String(10), nullable=True)  # Serious Near Miss
    unsafe_act = Column(String(255), nullable=True)  # Unsafe Act
    unsafe_act_other = Column(Text, nullable=True)  # Unsafe Act other
    unsafe_condition = Column(Text, nullable=True)  # Unsafe Condition
    unsafe_condition_other = Column(Text, nullable=True)  # Unsafe Condition other

    # Column 34-37: Work stoppage
    work_stopped = Column(String(10), nullable=True)  # Work Stopped
    stop_work_nogo_violation = Column(String(255), nullable=True)  # Stop Work NOGO Violation
    nogo_violation_detail = Column(Text, nullable=True)  # NOGO Violation detail
    stop_work_duration = Column(String(255), nullable=True)  # Stop Work Duration

    # Column 38-40: Additional details
    other_safety_issues = Column(Text, nullable=True)  # Other Safety Issues
    comments_remarks = Column(Text, nullable=True)  # Comments/Remarks
    event_requires_sanction = Column(String(10), nullable=True)  # Event requires sanction

    # Column 41-45: Actions taken
    action_description_1 = Column(Text, nullable=True)  # Action Description 1
    action_description_2 = Column(Text, nullable=True)  # Action Description 2
    action_description_3 = Column(Text, nullable=True)  # Action Description 3
    action_description_4 = Column(Text, nullable=True)  # Action Description 4
    action_description_5 = Column(Text, nullable=True)  # Action Description 5

    # Column 46-48: Final details
    image = Column(String(500), nullable=True)  # Image
    status = Column(String(50), nullable=True)  # Status
    region = Column(String(100), nullable=True)  # Region

     # Automatic timestamp for when record is inserted
    db_uploaded_date = Column(DateTime, server_default=func.now(), nullable=False)


class UnsafeEventSRS(BaseModel):
    """Model for SRS unsafe events - ALL 47 columns"""
    __tablename__ = "unsafe_events_srs"

    # Column 1-6: Core identification
    event_id = Column(String(100), nullable=True, index=True)  # Event Id
    reporter_name = Column(String(255), nullable=True)  # Reporter Name
    reported_date = Column(Date, nullable=True)  # Reported Date
    reporter_id = Column(String(100), nullable=True)  # Reporter ID
    date_of_unsafe_event = Column(Date, nullable=True)  # Date Of Unsafe Event
    time_of_unsafe_event = Column(String(50), nullable=True)  # Time of unsafe event

    # Column 7-12: Event details
    unsafe_event_type = Column(String(255), nullable=True)  # Unsafe Event Type
    business_details = Column(String(255), nullable=True)  # Business Details
    site_reference = Column(Text, nullable=True)  # Site Reference
    unsafe_event_location = Column(String(255), nullable=True)  # Unsafe Event location
    product_type = Column(String(255), nullable=True)  # Product Type
    employee_id = Column(String(100), nullable=True)  # Employee ID

    # Column 13-18: Personnel involved
    employee_name = Column(String(255), nullable=True)  # Employee Name
    subcontractor_company_name = Column(String(255), nullable=True)  # Subcontractor Company Name
    subcontractor_id = Column(String(100), nullable=True)  # SubcontractorID
    subcontractor_city = Column(String(255), nullable=True)  # Subcontractor CITY
    subcontractor_name = Column(String(255), nullable=True)  # Subcontractor Name
    kg_name = Column(String(100), nullable=True)  # KG Name

    # Column 19-26: Location hierarchy
    country_name = Column(String(100), nullable=True)  # Country Name
    division = Column(String(255), nullable=True)  # Division
    department = Column(String(255), nullable=True)  # Department
    city = Column(String(255), nullable=True)  # City
    sub_area = Column(String(100), nullable=True)  # Sub-Area
    district = Column(String(255), nullable=True)  # District
    zone = Column(String(255), nullable=True)  # Zone
    serious_near_miss = Column(String(10), nullable=True)  # Serious Near Miss

    # Column 27-32: Event classification
    unsafe_act = Column(Text, nullable=True)  # Unsafe Act
    unsafe_act_other = Column(Text, nullable=True)  # Unsafe Act other
    unsafe_condition = Column(Text, nullable=True)  # Unsafe Condition
    unsafe_condition_other = Column(Text, nullable=True)  # Unsafe Condition other
    work_stopped = Column(String(10), nullable=True)  # Work Stopped
    stop_work_nogo_violation = Column(String(10), nullable=True)  # Stop Work NOGO Violation

    # Column 33-38: Work stoppage and safety
    nogo_violation_detail = Column(Text, nullable=True)  # NOGO Violation detail
    stop_work_duration = Column(String(255), nullable=True)  # Stop Work Duration
    other_safety_issues = Column(Text, nullable=True)  # Other Safety Issues
    comments_remarks = Column(Text, nullable=True)  # Comments/Remarks
    event_requires_sanction = Column(String(10), nullable=True)  # Event requires sanction
    action_description_1 = Column(Text, nullable=True)  # Action Description 1

    # Column 39-45: Actions and final details
    action_description_2 = Column(Text, nullable=True)  # Action Description 2
    action_description_3 = Column(Text, nullable=True)  # Action Description 3
    action_description_4 = Column(Text, nullable=True)  # Action Description 4
    action_description_5 = Column(Text, nullable=True)  # Action Description 5
    branch = Column(String(255), nullable=True)  # Branch
    region = Column(String(100), nullable=True)  # Region

     # Automatic timestamp for when record is inserted
    db_uploaded_date = Column(DateTime, server_default=func.now(), nullable=False)


class UnsafeEventNITCT(BaseModel):
    """Model for NI TCT App unsafe events - ALL 43 columns"""
    __tablename__ = "unsafe_events_ni_tct"

    # Column 1-10: Core identification and location
    reporting_id = Column(Integer, nullable=True, index=True)  # Reporting ID
    status_key = Column(String(50), nullable=True)  # Status_Key
    status = Column(String(50), nullable=True)  # Status
    location_key = Column(Integer, nullable=True)  # Location_Key
    location = Column(String(255), nullable=True)  # Location
    branch_key = Column(Integer, nullable=True)  # Branch_Key
    no = Column(Integer, nullable=True)  # No
    branch_name = Column(String(255), nullable=True)  # Branch Name
    region_key = Column(String(100), nullable=True)  # Region_Key
    region = Column(String(100), nullable=True)  # Region

    # Column 11-18: Reporter and hierarchy details
    reporter_sap_id = Column(String(100), nullable=True)  # Reporter SAP ID
    reporter_name = Column(String(255), nullable=True)  # Reporter Name
    designation_key = Column(String(50), nullable=True)  # Designation_Key
    designation = Column(String(255), nullable=True)  # Designation
    gl_id_key = Column(String(100), nullable=True)  # GL ID_Key
    gl_id = Column(String(255), nullable=True)  # GL ID
    pe_id_key = Column(String(100), nullable=True)  # PE ID_Key
    pe_id = Column(String(255), nullable=True)  # PE ID

    # Column 19-20: Event timing
    created_on = Column(DateTime, nullable=True)  # Created On
    date_and_time_of_unsafe_event = Column(DateTime, nullable=True)  # Date and Time of Unsafe Event

    # Column 21-28: Event classification
    type_of_unsafe_event_key = Column(String(50), nullable=True)  # Type Of Unsafe Event_Key
    type_of_unsafe_event = Column(String(255), nullable=True)  # Type Of Unsafe Event
    unsafe_event_details_key = Column(String(50), nullable=True)  # Unsafe Event Details_Key
    unsafe_event_details = Column(Text, nullable=True)  # Unsafe Event Details
    action_related_to_high_risk_situation_key = Column(String(10), nullable=True)  # Action Related to High Risk Situation_Key
    action_related_to_high_risk_situation = Column(String(10), nullable=True)  # Action Related to High Risk Situation
    business_details_key = Column(String(50), nullable=True)  # Business Details_Key
    business_details = Column(String(255), nullable=True)  # Business Details

    # Column 29-34: Site and product details
    site_name = Column(Text, nullable=True)  # Site Name
    site_reference_key = Column(String(50), nullable=True)  # Site Reference_Key
    site_reference = Column(String(255), nullable=True)  # Site Reference
    product_type_key = Column(String(50), nullable=True)  # Product Type_Key
    product_type = Column(String(255), nullable=True)  # Product Type
    persons_involved = Column(Text, nullable=True)  # Persons Involved

    # Column 35-40: Work stoppage details
    work_was_stopped_key = Column(String(10), nullable=True)  # Work Was Stopped_Key
    work_was_stopped = Column(String(10), nullable=True)  # Work Was Stopped
    work_stopped_hours = Column(String(50), nullable=True)  # Work Stopped Hours
    no_go_violation_key = Column(String(50), nullable=True)  # No Go Violation_Key
    no_go_violation = Column(String(255), nullable=True)  # No Go Violation
    job_no = Column(String(100), nullable=True)  # Job No

    # Column 41-43: Additional details
    additional_comments = Column(Text, nullable=True)  # Additional Comments
    has_attachment = Column(Boolean, nullable=True)  # Has Attachment
    attachment = Column(String(500), nullable=True)  # Attachment

    # Automatic timestamp for when record is inserted
    db_uploaded_date = Column(DateTime, server_default=func.now(), nullable=False)


class UnsafeEventNITCTAugmented(BaseModel):
    """Model for NI TCT Augmented unsafe events - ALL original 43 columns + 15 augmented columns"""
    __tablename__ = "unsafe_events_ni_tct_augmented"

    # ==================== ORIGINAL NI TCT COLUMNS (43) ====================
    # Column 1-10: Core identification and location
    reporting_id = Column(Integer, nullable=True, index=True)  # Reporting ID
    status_key = Column(String(50), nullable=True)  # Status_Key
    status = Column(String(50), nullable=True)  # Status
    location_key = Column(Integer, nullable=True)  # Location_Key
    location = Column(String(255), nullable=True)  # Location
    branch_key = Column(Integer, nullable=True)  # Branch_Key
    no = Column(Integer, nullable=True)  # No
    branch_name = Column(String(255), nullable=True)  # Branch Name
    region_key = Column(String(100), nullable=True)  # Region_Key
    region = Column(String(100), nullable=True)  # Region

    # Column 11-18: Reporter and hierarchy details
    reporter_sap_id = Column(String(100), nullable=True)  # Reporter SAP ID
    reporter_name = Column(String(255), nullable=True)  # Reporter Name
    designation_key = Column(String(50), nullable=True)  # Designation_Key
    designation = Column(String(255), nullable=True)  # Designation
    gl_id_key = Column(String(100), nullable=True)  # GL ID_Key
    gl_id = Column(String(255), nullable=True)  # GL ID
    pe_id_key = Column(String(100), nullable=True)  # PE ID_Key
    pe_id = Column(String(255), nullable=True)  # PE ID

    # Column 19-20: Event timing
    created_on = Column(DateTime, nullable=True)  # Created On
    date_and_time_of_unsafe_event = Column(DateTime, nullable=True)  # Date and Time of Unsafe Event

    # Column 21-28: Event classification
    type_of_unsafe_event_key = Column(String(50), nullable=True)  # Type Of Unsafe Event_Key
    type_of_unsafe_event = Column(String(255), nullable=True)  # Type Of Unsafe Event
    unsafe_event_details_key = Column(String(50), nullable=True)  # Unsafe Event Details_Key
    unsafe_event_details = Column(Text, nullable=True)  # Unsafe Event Details
    action_related_to_high_risk_situation_key = Column(String(10), nullable=True)  # Action Related to High Risk Situation_Key
    action_related_to_high_risk_situation = Column(String(10), nullable=True)  # Action Related to High Risk Situation
    business_details_key = Column(String(50), nullable=True)  # Business Details_Key
    business_details = Column(String(255), nullable=True)  # Business Details

    # Column 29-34: Site and product details
    site_name = Column(Text, nullable=True)  # Site Name
    site_reference_key = Column(String(50), nullable=True)  # Site Reference_Key
    site_reference = Column(String(255), nullable=True)  # Site Reference
    product_type_key = Column(String(50), nullable=True)  # Product Type_Key
    product_type = Column(String(255), nullable=True)  # Product Type
    persons_involved = Column(Text, nullable=True)  # Persons Involved

    # Column 35-40: Work stoppage details
    work_was_stopped_key = Column(String(10), nullable=True)  # Work Was Stopped_Key
    work_was_stopped = Column(String(10), nullable=True)  # Work Was Stopped
    work_stopped_hours = Column(String(50), nullable=True)  # Work Stopped Hours
    no_go_violation_key = Column(String(50), nullable=True)  # No Go Violation_Key
    no_go_violation = Column(String(255), nullable=True)  # No Go Violation
    job_no = Column(String(100), nullable=True)  # Job No

    # Column 41-43: Additional details
    additional_comments = Column(Text, nullable=True)  # Additional Comments
    has_attachment = Column(Boolean, nullable=True)  # Has Attachment
    attachment = Column(String(500), nullable=True)  # Attachment

    # ==================== AUGMENTED COLUMNS (15) ====================
    # Weather Data (4 columns)
    weather_weather_condition = Column(String(100), nullable=True)  # Weather condition
    weather_temperature_celsius = Column(String(10), nullable=True)  # Temperature in Celsius
    weather_humidity_percent = Column(String(10), nullable=True)  # Humidity percentage
    weather_weather_severity_score = Column(Integer, nullable=True)  # Weather severity score (1-10)

    # Employee Data (6 columns)
    employee_employee_age = Column(Integer, nullable=True)  # Employee age
    employee_experience_level = Column(String(100), nullable=True)  # Experience level
    employee_years_of_experience = Column(String(10), nullable=True)  # Years of experience
    employee_safety_training_hours = Column(Integer, nullable=True)  # Safety training hours
    employee_last_training_date = Column(Date, nullable=True)  # Last training date
    employee_shift_type = Column(String(50), nullable=True)  # Shift type

    # Site Risk Data (2 columns)
    site_site_risk_category = Column(String(50), nullable=True)  # Site risk category
    site_last_safety_audit_days = Column(Integer, nullable=True)  # Days since last safety audit

    # Workload Metrics (3 columns)
    workload_workload_category = Column(String(50), nullable=True)  # Workload category
    workload_team_size = Column(Integer, nullable=True)  # Team size
    workload_work_duration_hours = Column(String(10), nullable=True)  # Work duration in hours

    # Automatic timestamp for when record is inserted
    db_uploaded_date = Column(DateTime, server_default=func.now(), nullable=False)
