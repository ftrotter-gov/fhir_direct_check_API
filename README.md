# FHIR Direct Check API

A Dockerized Flask API service that validates Direct and FHIR endpoints, providing cached results and rate-limited access.

## About the Project

This service allows you to validate:

- **Direct Addresses**: Verifies if an SMTP-style address is a valid Direct address by checking DNS/LDAP records
- **FHIR Endpoints**: Validates FHIR server URLs by checking metadata endpoints and SMART-on-FHIR discovery

Built using [getdc](https://github.com/TransparentHealth/getdc) and [inspectorfhir](https://github.com/TransparentHealth/inspectorfhir) libraries.

### Key Features

- Validate up to 10 endpoints per request
- Automatic caching (6-month validity by default)
- IP-based rate limiting (100 requests per 5 minutes, unlimited for localhost)
- Paginated bulk data download
- PostgreSQL database for persistent storage
- Docker Compose for easy deployment
- Health and readiness endpoints for monitoring

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) Python 3.12+ for local development

### Running with Docker Compose

1. Clone the repository:

```bash
git clone <repository-url>
cd fhir_direct_check_API
```

2. Copy the example environment file:

```bash
cp .env.example .env
# Edit .env if you need to customize settings
```

3. Start the services:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:5000`

### Local Development

1. Create a virtual environment:

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Configure DATABASE_URL for your local PostgreSQL instance
```

4. Initialize the database:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Run the development server:

```bash
flask run
```

## API Endpoints

### POST /validate

Validate one or more Direct/FHIR endpoints.

**Request:**

```json
{
  "endpoints": [
    "provider@direct.example.com",
    "https://fhir.example.com/api"
  ]
}
```

**Response:**

```json
{
  "results": {
    "provider@direct.example.com": {
      "endpoint_type": "DirectAddress",
      "endpoint_text": "provider@direct.example.com",
      "last_checked": "2026-03-29T20:00:00",
      "is_direct_dns": true,
      "is_direct_ldap": false,
      "is_valid_direct": true,
      "is_valid_endpoint": true,
      "from_cache": false,
      "validation_error": null
    },
    "https://fhir.example.com/api": {
      "endpoint_type": "FHIRAddress",
      "endpoint_text": "https://fhir.example.com/api",
      "last_checked": "2026-03-29T20:00:00",
      "fhir_metadata_url": "https://fhir.example.com/api/metadata",
      "is_valid_fhir": true,
      "is_valid_endpoint": true,
      "from_cache": false,
      "validation_error": null
    }
  },
  "total_endpoints": 2,
  "cache_validity_months": 6
}
```

### GET /download

Download all validation data with pagination.

**Query Parameters:**

- `page` (int, default: 1): Page number
- `per_page` (int, default: 100, max: 1000): Results per page

**Example:**

```bash
curl "http://localhost:5000/download?page=1&per_page=50"
```

**Response:**

```json
{
  "data": [...],
  "page": 1,
  "per_page": 50,
  "total": 150,
  "total_pages": 3,
  "has_next": true,
  "has_prev": false
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

### GET /ready

Readiness check (verifies database connectivity).

**Response:**

```json
{
  "status": "ready"
}
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `SECRET_KEY` | - | Flask secret key (change in production!) |
| `MAX_ENDPOINTS_PER_REQUEST` | 10 | Maximum endpoints per validation request |
| `CACHE_VALIDITY_MONTHS` | 6 | How long cached results remain valid |
| `RATE_LIMIT_REQUESTS` | 100 | Requests allowed per time window |
| `RATE_LIMIT_PERIOD_MINUTES` | 5 | Rate limit time window |

## Testing

Run the test suite with pytest:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest

# Run specific test file
pytest tests/test_routes.py

# Run with verbose output
pytest -v
```

## Database Schema

The `endpoint_validations` table stores:

- `endpoint_type`: 'DirectAddress' or 'FHIRAddress'
- `endpoint_text`: The endpoint being validated
- `last_checked`: Timestamp of last validation
- Direct-specific fields: `is_direct_dns`, `is_direct_ldap`, `is_valid_direct`
- FHIR-specific fields: `fhir_metadata_url`, `oidc_discovery_url`, SMART discovery URLs, etc.
- `is_valid_endpoint`: Overall validation status
- `validation_error`: Error message if validation failed

## Deployment

### Using External PostgreSQL

1. Update `DATABASE_URL` in your `.env` file to point to your PostgreSQL server
2. Remove the `postgres` service from `docker-compose.yml` if not needed
3. Run: `docker-compose up --build`

### Production Considerations

- Set a strong `SECRET_KEY`
- Use a managed PostgreSQL service
- Configure proper network security
- Consider using a reverse proxy (nginx, Traefik)
- Set up monitoring using `/health` and `/ready` endpoints
- Review rate limiting settings based on your use case

## Rate Limiting

- **Localhost**: Unlimited access (127.0.0.1, ::1)
- **Other IPs**: 100 requests per 5 minutes (configurable)
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests in window

## Caching Behavior

- Results are cached for 6 months by default
- Cached results include `"from_cache": true` in response
- Cache automatically used when valid
- No force-refresh option (by design)

<!---
### Project Vision
**{project vision}** -->

<!--
### Project Mission
**{project mission}** -->

<!--
### Agency Mission
TODO: Good to include since this is an agency-led project -->

<!--
### Team Mission
TODO: Good to include since this is an agency-led project -->

<!--
## Core Team

A list of core team members responsible for the code and documentation in this repository can be found in [COMMUNITY.md](COMMUNITY.md).
-->

<!--
## Repository Structure

TODO: Including the repository structure helps viewers quickly understand the project layout. Using the "tree -d" command can be a helpful way to generate this information, but, be sure to update it as the project evolves and changes over time.

**{list directories and descriptions}**

TODO: Add a 'table of contents" for your documentation. Tier 0/1 projects with simple README.md files without many sections may or may not need this, but it is still extremely helpful to provide "bookmark" or "anchor" links to specific sections of your file to be referenced in tickets, docs, or other communication channels.

**{list of .md at top directory and descriptions}**

-->

<!---
## Local Development

 TODO - with example below:
This project is monorepo with several apps. Please see the [api](./api/README.md) and [frontend](./frontend/README.md) READMEs for information on spinning up those projects locally. Also see the project [documentation](./documentation) for more info.
-->

<!--
## Coding Style and Linters

TODO - Add the repo's linting and code style guidelines

Each application has its own linting and testing guidelines. Lint and code tests are run on each commit, so linters and tests should be run locally before committing.
 -->

<!---
## Branching Model

TODO - with example below:
This project follows [trunk-based development](https://trunkbaseddevelopment.com/), which means:

* Make small changes in [short-lived feature branches](https://trunkbaseddevelopment.com/short-lived-feature-branches/) and merge to `main` frequently.
* Be open to submitting multiple small pull requests for a single ticket (i.e. reference the same ticket across multiple pull requests).
* Treat each change you merge to `main` as immediately deployable to production. Do not merge changes that depend on subsequent changes you plan to make, even if you plan to make those changes shortly.
* Ticket any unfinished or partially finished work.
* Tests should be written for changes introduced, and adhere to the text percentage threshold determined by the project.

This project uses **continuous deployment** using [Github Actions](https://github.com/features/actions) which is configured in the [./github/workflows](.github/workflows) directory.

Pull-requests are merged to `main` and the changes are immediately deployed to the development environment. Releases are created to push changes to production.
-->

## Policies

### Open Source Policy

We adhere to the [CMS Open Source Policy](https://github.com/CMSGov/cms-open-source-policy). If you have any questions, just [shoot us an email](mailto:opensource@cms.hhs.gov).

### Security and Responsible Disclosure Policy

_Submit a vulnerability:_ Vulnerability reports can be submitted through [Bugcrowd](https://bugcrowd.com/cms-vdp). Reports may be submitted anonymously. If you share contact information, we will acknowledge receipt of your report within 3 business days.

### Software Bill of Materials (SBOM)

A Software Bill of Materials (SBOM) is a formal record containing the details and supply chain relationships of various components used in building software.

In the spirit of [Executive Order 14028 - Improving the Nation's Cyber Security](https://www.gsa.gov/technology/it-contract-vehicles-and-purchasing-programs/information-technology-category/it-security/executive-order-14028), a SBOM for this repository is provided here: https://github.com/{{ cookiecutter.project_org }}/{{ cookiecutter.project_repo_name }}/network/dependencies.

For more information and resources about SBOMs, visit: https://www.cisa.gov/sbom.

## Public domain

This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/) as indicated in [LICENSE](LICENSE).

All contributions to this project will be released under the CC0 dedication. By submitting a pull request or issue, you are agreeing to comply with this waiver of copyright interest.
