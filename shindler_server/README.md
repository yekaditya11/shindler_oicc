# Shindler EI Tech API Server

A comprehensive FastAPI server providing safety KPIs from EI Tech App data with date filtering capabilities.

## Features

- **Comprehensive Safety KPIs**: Access to 18+ core safety metrics
- **Date Range Filtering**: Filter data by start and end dates
- **Real-time Database Connection**: Direct connection to PostgreSQL database
- **RESTful API**: Standard HTTP endpoints with JSON responses
- **Interactive Documentation**: Swagger UI and ReDoc documentation
- **Simple & Clean**: Focused single endpoint design

## API Endpoints

### Main EI Tech KPI Endpoint

```
GET /api/v1/ei_tech
```

Returns comprehensive safety KPIs with optional date filtering.

**Parameters:**
- `start_date` (optional): Start date for filtering (YYYY-MM-DD format)
- `end_date` (optional): End date for filtering (YYYY-MM-DD format)

**Default Behavior:** When no date parameters are provided, the API returns data for the **last 1 year** from today's date.

**Example Usage:**

```bash
# Get last 1 year of KPIs (default behavior)
curl "http://localhost:8000/api/v1/ei_tech"

# Get KPIs for a specific date range
curl "http://localhost:8000/api/v1/ei_tech?start_date=2024-01-01&end_date=2024-12-31"

# Get KPIs from a specific start date
curl "http://localhost:8000/api/v1/ei_tech?start_date=2024-06-01"
```

### Additional Endpoints

```
GET /health                   # Overall API health check
GET /docs                     # Swagger UI documentation
GET /redoc                    # ReDoc documentation
GET /api/info                 # API information and usage examples
```

## KPI Categories

The `/api/v1/ei_tech` endpoint returns the following KPI categories:

### Core Safety Metrics
- `number_of_unsafe_events`: Total and unique event counts
- `monthly_unsafe_events_trend`: Events per time period
- `near_misses`: Serious near miss statistics
- `serious_near_misses_trend`: Trend analysis

### Geographic & Risk Analysis
- `unsafe_events_by_branch`: Events breakdown by branch
- `unsafe_events_by_region`: Regional distribution
- `at_risk_regions`: High-risk location analysis
- `branch_risk_index`: Risk scoring by branch
- `frequent_unsafe_event_locations`: Location hotspots

### Behavioral Analysis
- `common_unsafe_behaviors`: Unsafe acts analysis
- `common_unsafe_conditions`: Unsafe conditions analysis
- `monthly_weekly_trends_unsafe_behaviors`: Time-based behavioral trends
- `monthly_weekly_trends_unsafe_conditions`: Time-based condition trends

### Operational Impact
- `number_of_nogo_violations`: NOGO violation counts
- `work_hours_lost`: Stop work duration analysis
- `time_taken_to_report_incidents`: Reporting delay analysis

### Action & Compliance
- `action_creation_and_compliance`: Action effectiveness analysis
- `action_closure_rate`: Action completion rates

### Secondary Analysis
- `unsafe_events_by_time_of_day`: Time-of-day patterns
- `unsafe_event_distribution_by_business_type`: Business type breakdown
- `nogo_violation_trends_by_regions_branches`: Regional safety performance

## Installation & Setup

### Prerequisites

- Python 3.8+
- PostgreSQL database access
- Azure OpenAI account (optional)

### Installation Steps

1. **Clone the repository and navigate to the shindler_server directory:**
   ```bash
   cd shindler_server
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file with the following configuration:
   ```env
   # PostgreSQL Database Configuration
   POSTGRES_HOST=your_host_here
   POSTGRES_PORT=5432
   POSTGRES_DB=your_database_here
   POSTGRES_USER=your_username_here
   POSTGRES_PASSWORD=your_password_here

   # Azure OpenAI Configuration (optional)
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_API_KEY=your_key_here
   AZURE_OPENAI_API_VERSION=2025-01-01-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_here
   ```

5. **Start the server:**
   ```bash
   python app.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Response Format

All endpoints return JSON responses with the following structure:

```json
{
  "status": "success",
  "message": "EI Tech KPIs retrieved successfully",
  "data": {
    "number_of_unsafe_events": {...},
    "monthly_unsafe_events_trend": [...],
    "query_metadata": {
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "date_filter_applied": true,
      "executed_at": "2024-01-15T10:30:00"
    }
  }
}
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid date format or date range
- **500 Internal Server Error**: Database connection issues or query failures
- **422 Validation Error**: Missing or invalid parameters

## Database Requirements

The API requires access to a PostgreSQL database with the `unsafe_events_ei_tech` table containing EI Tech App safety data.

## Development

### Running in Development Mode

```bash
uvicorn app:app --reload --log-level debug
```

### Testing Database Connection

Create a simple test script or use the health endpoint:

```bash
curl http://localhost:8000/health
```

## Architecture

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM for PostgreSQL connectivity
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Include comprehensive docstrings
4. Test database connections before committing
5. Update documentation for new endpoints

## Support

For technical support or questions about the EI Tech KPI API, please contact the development team.

## Version History

- **v1.0.0**: Initial release with comprehensive EI Tech KPIs and date filtering 