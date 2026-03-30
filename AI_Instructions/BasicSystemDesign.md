# Initial Design

Please use the libraries mentioned in the ReadMe.md to make a dockerized Flask API that efficiently checks for valid Direct and FHIR endpoints.

## Core Requirements

The API should take standard API practice and accept one or many SMTP-style possible direct addresses (i.e. could@beadirect.address) or a possible FHIR url (i.e. https://this.could.be/fhir) and then uses inspectorfhir and getdc respectively to test for validity.

The results should be saved to a PostgreSQL SQL server whose password parameters should be saved in a .env file that is excluded in .gitignore.

## Python Version

* Use Python 3.12

## Authentication & Rate Limiting

* IP allowlisting approach
* Allow unlimited access from localhost
* All other hosts: 100 queries every 5 minutes

## API Endpoints

* Single unified endpoint: `POST /validate` that accepts mixed Direct/FHIR addresses
* Health/readiness endpoints for monitoring
* Batch download endpoint for entire table in paged JSON format (same structure as database)

## Caching Behavior

* Always use cached results if available (last checked < 6 months)
* Do not implement force-refresh functionality
* Results should indicate whether data came from cache or fresh validation

## Database Schema

The table structure should be:

* endpoint_type: DirectAddress or FHIRAddress
* endpoint_text: The endpoint itself
* last_checked (timestamp)
* is_direct_dns
* is_direct_ldap
* is_valid_direct
* fhir_metadata_url
* oidc_discovery_url
* smart_discovery_1_url
* smart_discovery_2_url
* documentation_url
* is_documentation_found
* swagger_json_url
* is_swagger_json_found
* is_valid_fhir
* is_valid_endpoint

This unnormalized table structure should be adjusted as needed to accommodate the getdc and inspectorfhir results when used as a library.

## API Behavior

* Accept up to 10 endpoints at a time
* Return results on a per-address basis (results array coded by submitted addresses)
* If an endpoint has been checked in the last 6 months, use cached results
* For partial failures, return results for successful checks with error details for failures
* Response format should indicate whether results came from cache or fresh validation

## Docker Configuration

* Use docker-compose.yml that includes both Flask app and PostgreSQL
* PostgreSQL configuration should support external database (configurable via .env)
* Docker instance should include PostgreSQL to work out-of-the-box in standalone manner
* Testable on localhost and deployable using standard cloud docker deployment approaches

## Testing Requirements

* Unit tests using pytest
* Integration tests using pytest
* Test coverage for core validation logic
