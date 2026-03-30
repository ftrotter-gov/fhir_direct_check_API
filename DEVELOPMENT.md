# Development Guide

## Project Structure

```
fhir_direct_check_API/
├── app/                          # Application package
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── validators.py            # Validation logic (getdc/inspectorfhir)
│   ├── rate_limiter.py          # Rate limiting middleware
│   ├── routes.py                # API endpoints
│   └── config.py                # Configuration classes
├── tests/                        # Test suite
│   ├── conftest.py              # Pytest fixtures
│   ├── test_validators.py      # Validator unit tests
│   ├── test_rate_limiter.py    # Rate limiter tests
│   └── test_routes.py           # API integration tests
├── AI_Instructions/             # Project documentation
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Application container
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── .env.example                # Environment template
└── run.py                       # Development entry point

```

## Development Workflow

### Initial Setup

1. Clone and setup:

```bash
git clone <repo-url>
cd fhir_direct_check_API
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment:

```bash
cp .env.example .env
# Edit .env with your database settings
```

3. Initialize database:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Running Locally

#### Option 1: Flask CLI

```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

#### Option 2: Python Script

```bash
python run.py
```

#### Option 3: Docker Compose

```bash
docker-compose up --build
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_routes.py

# Run specific test
pytest tests/test_routes.py::TestHealthEndpoints::test_health_check

# Verbose output
pytest -v -s
```

### Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback one migration
flask db downgrade

# View migration history
flask db history
```

### Code Style

This project follows Python best practices:

- **Static Methods**: Classes organize functions; use `@staticmethod` decorators
- **Named Parameters**: All function parameters use named arguments (after `*`)
- **SQL Style**: UPPERCASE for SQL keywords, lowercase for identifiers
- **Error Messages**: Always descriptive, include file name (e.g., "routes.py Error: ...")
- **DRY Principle**: Refactor repeated code into reusable functions

### API Testing with curl

#### Validate Endpoints

```bash
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "endpoints": [
      "test@example.com",
      "https://fhir.example.com/api"
    ]
  }'
```

#### Download Data

```bash
curl "http://localhost:5000/download?page=1&per_page=10"
```

#### Health Checks

```bash
curl http://localhost:5000/health
curl http://localhost:5000/ready
```

## Architecture Notes

### Validation Flow

1. Request arrives at `/validate` endpoint
2. Rate limiter checks IP address and limits
3. Endpoint type detected (Direct vs FHIR)
4. Check database for cached results
5. If cache valid (< 6 months), return cached data
6. If cache invalid/missing, perform fresh validation:
   - Direct: Use getdc library
   - FHIR: Use inspectorfhir library
7. Save results to database (upsert)
8. Return results with `from_cache` flag

### Caching Strategy

- Cache validity: 6 months (configurable)
- Idempotent upsert: Updates existing records
- No force-refresh by design
- Cache status included in responses

### Rate Limiting

- In-memory tracking (per-process)
- Localhost always allowed
- Configurable limits per IP
- Automatic cleanup of old entries

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U fhir_user -d fhir_direct_check
```

### API Container Issues

```bash
# View API logs
docker-compose logs api

# Restart API service
docker-compose restart api

# Rebuild from scratch
docker-compose down
docker-compose up --build
```

### Testing Issues

```bash
# Clear pytest cache
rm -rf .pytest_cache

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Adding New Features

### Adding a New API Endpoint

1. Add route function in `app/routes.py`
2. Apply `@rate_limit_check` decorator if needed
3. Add tests in `tests/test_routes.py`
4. Update README.md with endpoint documentation

### Adding Database Fields

1. Update model in `app/models.py`
2. Create migration: `flask db migrate -m "Add new field"`
3. Apply migration: `flask db upgrade`
4. Update `to_dict()` method if field should be in API responses
5. Update tests as needed

### Modifying Validation Logic

1. Update validators in `app/validators.py`
2. Update mapping functions for library results
3. Add unit tests in `tests/test_validators.py`
4. Test with real endpoints

## Performance Considerations

- Cache reduces validation API calls
- Database queries optimized with indexes
- Rate limiting prevents abuse
- Pagination limits response sizes
- Connection pooling for database

## Security Best Practices

- Never commit `.env` file
- Use strong `SECRET_KEY` in production
- Keep dependencies updated
- Validate all user inputs
- Use parameterized SQL queries (SQLAlchemy ORM)
- Rate limiting prevents DoS
