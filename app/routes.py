"""API routes for FHIR Direct Check API."""
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import EndpointValidation
from app.validators import EndpointValidator
from app.rate_limiter import rate_limit_check
from sqlalchemy import func

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response indicating service health
    """
    return jsonify({'status': 'healthy'}), 200


@api_blueprint.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check endpoint that verifies database connectivity.
    
    Returns:
        JSON response indicating service readiness
    """
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'ready'}), 200
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'error': f'routes.py Error: Database connection failed - {str(e)}'
        }), 503


@api_blueprint.route('/validate', methods=['POST'])
@rate_limit_check
def validate_endpoints():
    """
    Validate one or more Direct/FHIR endpoints.
    
    Accepts up to 10 endpoints, checks cache, and performs validation as needed.
    
    Request body:
        {
            "endpoints": ["address1", "url1", ...]
        }
    
    Returns:
        JSON response with validation results keyed by endpoint
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data or 'endpoints' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Request must include "endpoints" array'
            }), 400
        
        endpoints = data['endpoints']
        
        # Validate input
        if not isinstance(endpoints, list):
            return jsonify({
                'error': 'Bad Request',
                'message': '"endpoints" must be an array'
            }), 400
        
        if len(endpoints) == 0:
            return jsonify({
                'error': 'Bad Request',
                'message': 'At least one endpoint must be provided'
            }), 400
        
        max_endpoints = current_app.config.get('MAX_ENDPOINTS_PER_REQUEST', 10)
        if len(endpoints) > max_endpoints:
            return jsonify({
                'error': 'Bad Request',
                'message': f'Maximum {max_endpoints} endpoints allowed per request'
            }), 400
        
        # Process each endpoint
        results = {}
        cache_validity_months = current_app.config.get('CACHE_VALIDITY_MONTHS', 6)
        
        for endpoint_text in endpoints:
            endpoint_text = str(endpoint_text).strip()
            
            if not endpoint_text:
                results[endpoint_text] = {
                    'error': 'routes.py Error: Empty endpoint provided',
                    'from_cache': False
                }
                continue
            
            # Check for cached result
            cached_record = EndpointValidation.query.filter_by(
                endpoint_text=endpoint_text
            ).first()
            
            if cached_record and cached_record.is_cache_valid(validity_months=cache_validity_months):
                # Use cached result
                results[endpoint_text] = cached_record.to_dict(include_cache_info=True)
            else:
                # Perform fresh validation
                validation_result = _perform_validation(endpoint_text=endpoint_text)
                
                # Save to database
                try:
                    EndpointValidation.upsert(
                        endpoint_text=endpoint_text,
                        validation_data=validation_result
                    )
                    
                    # Fetch the saved record to return consistent format
                    saved_record = EndpointValidation.query.filter_by(
                        endpoint_text=endpoint_text
                    ).first()
                    
                    result_dict = saved_record.to_dict()
                    result_dict['from_cache'] = False
                    results[endpoint_text] = result_dict
                    
                except Exception as db_error:
                    # Return validation result even if save fails
                    validation_result['from_cache'] = False
                    validation_result['database_error'] = f'routes.py Error: Failed to save - {str(db_error)}'
                    results[endpoint_text] = validation_result
        
        return jsonify({
            'results': results,
            'total_endpoints': len(endpoints),
            'cache_validity_months': cache_validity_months
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': f'routes.py Error: Validation request failed - {str(e)}'
        }), 500


@api_blueprint.route('/download', methods=['GET'])
@rate_limit_check
def download_data():
    """
    Download endpoint validation data in paginated format.
    
    Query parameters:
        page (int): Page number (default 1)
        per_page (int): Results per page (default 100, max 1000)
    
    Returns:
        JSON response with paginated validation data
    """
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        
        if per_page < 1:
            per_page = 100
        elif per_page > 1000:
            per_page = 1000
        
        # Query database with pagination
        query = EndpointValidation.query.order_by(EndpointValidation.last_checked.desc())
        
        # Get total count
        total_count = query.count()
        
        # Calculate total pages
        total_pages = (total_count + per_page - 1) // per_page
        
        # Get paginated results
        paginated_results = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to dictionary format
        data = [record.to_dict() for record in paginated_results]
        
        return jsonify({
            'data': data,
            'page': page,
            'per_page': per_page,
            'total': total_count,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': f'routes.py Error: Download request failed - {str(e)}'
        }), 500


def _perform_validation(*, endpoint_text):
    """
    Perform validation on a single endpoint.
    
    Args:
        endpoint_text: The endpoint to validate
        
    Returns:
        dict: Validation results
    """
    # Detect endpoint type
    endpoint_type = EndpointValidator.detect_endpoint_type(endpoint_text=endpoint_text)
    
    # Perform appropriate validation
    if endpoint_type == 'DirectAddress':
        return EndpointValidator.validate_direct_address(address=endpoint_text)
    else:
        return EndpointValidator.validate_fhir_endpoint(url=endpoint_text)
