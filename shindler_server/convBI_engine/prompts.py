intent_prompt = [
    ("human", """Classify the user's intent based on their question and full conversation history.

Current question: {question}

Conversation history: {history}

Categories:
- general: General greetings, pleasantries, casual conversation (hi, hello, bye, thanks, etc.)
- system_query: Questions about data, database queries, system information, get data, etc.

IMPORTANT: Use the conversation history to understand context. For example:
- If previous questions were about data and current question is "What about region X?", classify as system_query
- If this is a follow-up question referencing previous data queries, classify as system_query

Respond with only the category name (general or system_query)""")
]

greeting_prompt = [
    ("human", """Respond to the user's greeting or casual message in a friendly, professional manner.
Keep it brief and helpful.
User message: {question}""")
]

file_identification_prompt = [
    ("human", """Identify the table name which need to be queried to answer the question based on the DDL given below.
DDL: {ddl}
User question: {question}
previous conversation: {history}
just return the table name. no explanation needed.""")
]

required_columns_prompt = [
    ("human", """Based on the SQL error and the context and user question, give the list of required columns that need to be considered (watch the cells of each column) for rephrasing the SQL query.
Question: {question}
SQL query: {query}
Error Message: {error_message}
Column info: {col_info}
conversation history: {history}
Respond with only the list of column names
Example:
["id", "role", "name"]
Don't add ```json or ``` in the output, just give the list of column names""")
]

text_to_sql_prompt = [
    ("human", """Convert the user's question into a SQL query based on the DDL given below.
DDL: {ddl}
User question: {question}
column info: {col_info}
previous conversation: {history}
Respond with only the SQL query. no explanation needed.
Don't add ```json or ``` in the output, just give the list of column names""")
]


summarizer_prompt= [
    ("human", """Summarize the query result based on the user's question.
User question: {question}
Query result: {query_result}
previous conversation: {history}
filename: {filename}
     
Respond with only the summary. no explanation needed.
summary must be refering to the filename given: 
unsafe_events_ei_tech -> ei tech
unsafe_events_ni_tct -> ni tct
unsafe_events_srs -> srs

FORMATTING GUIDELINES:
- For monthly data: Format as "Month: X events" (e.g., "January: 770 events, February: 1,511 events")
- Use clear, simple language with proper formatting
- Include specific numbers with commas for readability
- For time periods: Use consistent formatting (e.g., "January: 770, February: 1,511, March: 1,647")
- Keep the response concise and well-structured
- Use bullet points or clear line breaks for multiple data points
""")
]

clarification_prompt = [
    ("human", """Based on the user's question and the error message, ask user to provide more information. It shouldn't be techinical like asking for column names.
User question: {question}
Error Message: {error_message}
previous conversation: {history}
Respond with only the rephrased question. no explanation needed.""")
]

prompt_ddl="""
unsafe_events_ei_tech (
    event_id INTEGER,
    reporter_name VARCHAR(255),
    manager_name VARCHAR(255),
    branch VARCHAR(255),
    reported_date DATE,
    reporter_id VARCHAR(100),
    date_of_unsafe_event DATE,
    time VARCHAR(50),
    time_of_unsafe_event VARCHAR(50),
    unsafe_event_type VARCHAR(255),
    business_details VARCHAR(255),
    site_reference TEXT,
    unsafe_event_location VARCHAR(255),
    product_type VARCHAR(255),
    employee_id VARCHAR(100),
    employee_name VARCHAR(255),
    subcontractor_company_name VARCHAR(255),
    subcontractor_id VARCHAR(100),
    subcontractor_city VARCHAR(255),
    subcontractor_name VARCHAR(255),
    kg_name VARCHAR(100),
    country_name VARCHAR(100),
    division VARCHAR(255),
    department VARCHAR(255),
    city VARCHAR(255),
    sub_area VARCHAR(100),
    district VARCHAR(255),
    zone VARCHAR(255),
    serious_near_miss VARCHAR(10),
    unsafe_act VARCHAR(255),
    unsafe_act_other TEXT,
    unsafe_condition TEXT,
    unsafe_condition_other TEXT,
    work_stopped VARCHAR(10),
    stop_work_nogo_violation VARCHAR(255),
    nogo_violation_detail TEXT,
    stop_work_duration VARCHAR(255),
    other_safety_issues TEXT,
    comments_remarks TEXT,
    event_requires_sanction VARCHAR(10),
    action_description_1 TEXT,
    action_description_2 TEXT,
    action_description_3 TEXT,
    action_description_4 TEXT,
    action_description_5 TEXT,
    image VARCHAR(500),
    status VARCHAR(50),
    region VARCHAR(100),
    db_uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

unsafe_events_srs (
    event_id VARCHAR(100),
    reporter_name VARCHAR(255),
    reported_date DATE,
    reporter_id VARCHAR(100),
    date_of_unsafe_event DATE,
    time_of_unsafe_event VARCHAR(50),
    unsafe_event_type VARCHAR(255),
    business_details VARCHAR(255),
    site_reference TEXT,
    unsafe_event_location VARCHAR(255),
    product_type VARCHAR(255),
    employee_id VARCHAR(100),
    employee_name VARCHAR(255),
    subcontractor_company_name VARCHAR(255),
    subcontractor_id VARCHAR(100),
    subcontractor_city VARCHAR(255),
    subcontractor_name VARCHAR(255),
    kg_name VARCHAR(100),
    country_name VARCHAR(100),
    division VARCHAR(255),
    department VARCHAR(255),
    city VARCHAR(255),
    sub_area VARCHAR(100),
    district VARCHAR(255),
    zone VARCHAR(255),
    serious_near_miss VARCHAR(10),
    unsafe_act TEXT,
    unsafe_act_other TEXT,
    unsafe_condition TEXT,
    unsafe_condition_other TEXT,
    work_stopped VARCHAR(10),
    stop_work_nogo_violation VARCHAR(10),
    nogo_violation_detail TEXT,
    stop_work_duration VARCHAR(255),
    other_safety_issues TEXT,
    comments_remarks TEXT,
    event_requires_sanction VARCHAR(10),
    action_description_1 TEXT,
    action_description_2 TEXT,
    action_description_3 TEXT,
    action_description_4 TEXT,
    action_description_5 TEXT,
    branch VARCHAR(255),
    region VARCHAR(100),
    db_uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

unsafe_events_ni_tct (
    reporting_id INTEGER,
    status_key VARCHAR(50),
    status VARCHAR(50),
    location_key INTEGER,
    location VARCHAR(255),
    branch_key INTEGER,
    no INTEGER,
    branch_name VARCHAR(255),
    region_key VARCHAR(100),
    region VARCHAR(100),
    reporter_sap_id VARCHAR(100),
    reporter_name VARCHAR(255),
    designation_key VARCHAR(50),
    designation VARCHAR(255),
    gl_id_key VARCHAR(100),
    gl_id VARCHAR(255),
    pe_id_key VARCHAR(100),
    pe_id VARCHAR(255),
    created_on TIMESTAMP,
    date_and_time_of_unsafe_event TIMESTAMP,
    type_of_unsafe_event_key VARCHAR(50),
    type_of_unsafe_event VARCHAR(255),
    unsafe_event_details_key VARCHAR(50),
    unsafe_event_details TEXT,
    action_related_to_high_risk_situation_key VARCHAR(10),
    action_related_to_high_risk_situation VARCHAR(10),
    business_details_key VARCHAR(50),
    business_details VARCHAR(255),
    site_name TEXT,
    site_reference_key VARCHAR(50),
    site_reference VARCHAR(255),
    product_type_key VARCHAR(50),
    product_type VARCHAR(255),
    persons_involved TEXT,
    work_was_stopped_key VARCHAR(10),
    work_was_stopped VARCHAR(10),
    work_stopped_hours VARCHAR(50),
    no_go_violation_key VARCHAR(50),
    no_go_violation VARCHAR(255),
    job_no VARCHAR(100),
    additional_comments TEXT,
    has_attachment BOOLEAN,
    attachment VARCHAR(500),
    db_uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
