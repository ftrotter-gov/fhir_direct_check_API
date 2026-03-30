Initial Design
==============

Please use the libraries mentioned in the ReadMe.md to make a dockerized Flask API that efficiently checks for valid Direct and FHIR endpoints.

The API should take standard API practice.. and accept one or many SMTP-style possible direct addresses (i.e. could@beadirect.address) or a possible FHIR url (i.e. https://this.could.be/fhir) and then uses inspectorfhir and getdc respectively to test for validity.

The results should be save to a postgresql sql server whose password parameters should be saved in a .env file that is excluded in .gitignore.

The table structure should be:

* endpoint type: DirectAddress or FHIRAddress
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

This unormalized table structure should be adjusted as needed to accomodate the getdc and inspectorfhir results when used as a library.

The goal is to be able to quickly provide one or many such addresses to the API..
have them checked... and provide the results back (a json reflection of the database contents for the various arguments)

The API should support 10 endpoints at a time.

If an endpoint has been checked in the last 6 months it should not be checked again by default.

The library should use a dockerized flask instance. It should be testable on localhost and deployable using standard cloud docker deployment approaches.

the postgresSQL configuration should support having a database that does not live on the same server as the service.
But the docker instance should install a postgresql instance to ensure that it works out-of-the-box in a standalone manner.
