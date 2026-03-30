"""Database models for FHIR Direct Check API."""
from datetime import datetime, timedelta
from app import db


class EndpointValidation(db.Model):
    """
    Model for storing endpoint validation results.
    
    This unnormalized table stores both Direct and FHIR endpoint validation data,
    adjusted to accommodate results from getdc and inspectorfhir libraries.
    """
    
    __tablename__ = 'endpoint_validations'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Core endpoint information
    endpoint_type = db.Column(db.String(50), nullable=False)  # 'DirectAddress' or 'FHIRAddress'
    endpoint_text = db.Column(db.String(500), nullable=False, unique=True, index=True)
    last_checked = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Direct address validation fields
    is_direct_dns = db.Column(db.Boolean, default=False)
    is_direct_ldap = db.Column(db.Boolean, default=False)
    is_valid_direct = db.Column(db.Boolean, default=False)
    
    # FHIR endpoint validation fields
    fhir_metadata_url = db.Column(db.String(500))
    oidc_discovery_url = db.Column(db.String(500))
    smart_discovery_1_url = db.Column(db.String(500))
    smart_discovery_2_url = db.Column(db.String(500))
    documentation_url = db.Column(db.String(500))
    is_documentation_found = db.Column(db.Boolean, default=False)
    swagger_json_url = db.Column(db.String(500))
    is_swagger_json_found = db.Column(db.Boolean, default=False)
    is_valid_fhir = db.Column(db.Boolean, default=False)
    
    # Overall validation status
    is_valid_endpoint = db.Column(db.Boolean, default=False)
    
    # Error tracking
    validation_error = db.Column(db.Text)
    
    def __repr__(self):
        return f'<EndpointValidation {self.endpoint_type}: {self.endpoint_text}>'
    
    def is_cache_valid(self, *, validity_months=6):
        """
        Check if the cached validation result is still valid.
        
        Args:
            validity_months: Number of months cache is valid (default 6)
            
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if not self.last_checked:
            return False
        
        expiry_date = self.last_checked + timedelta(days=validity_months * 30)
        return datetime.utcnow() < expiry_date
    
    def to_dict(self, *, include_cache_info=False):
        """
        Convert model to dictionary for JSON serialization.
        
        Args:
            include_cache_info: Whether to include cache metadata
            
        Returns:
            dict: Dictionary representation of the model
        """
        result = {
            'endpoint_type': self.endpoint_type,
            'endpoint_text': self.endpoint_text,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'is_direct_dns': self.is_direct_dns,
            'is_direct_ldap': self.is_direct_ldap,
            'is_valid_direct': self.is_valid_direct,
            'fhir_metadata_url': self.fhir_metadata_url,
            'oidc_discovery_url': self.oidc_discovery_url,
            'smart_discovery_1_url': self.smart_discovery_1_url,
            'smart_discovery_2_url': self.smart_discovery_2_url,
            'documentation_url': self.documentation_url,
            'is_documentation_found': self.is_documentation_found,
            'swagger_json_url': self.swagger_json_url,
            'is_swagger_json_found': self.is_swagger_json_found,
            'is_valid_fhir': self.is_valid_fhir,
            'is_valid_endpoint': self.is_valid_endpoint,
            'validation_error': self.validation_error
        }
        
        if include_cache_info:
            result['from_cache'] = True
        
        return result
    
    @classmethod
    def upsert(cls, *, endpoint_text, validation_data):
        """
        Insert or update endpoint validation record.
        
        Args:
            endpoint_text: The endpoint text (email or URL)
            validation_data: Dictionary of validation results
            
        Returns:
            EndpointValidation: The created or updated record
        """
        existing = cls.query.filter_by(endpoint_text=endpoint_text).first()
        
        if existing:
            # Update existing record
            for key, value in validation_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.last_checked = datetime.utcnow()
            record = existing
        else:
            # Create new record
            validation_data['endpoint_text'] = endpoint_text
            validation_data['last_checked'] = datetime.utcnow()
            record = cls(**validation_data)
            db.session.add(record)
        
        db.session.commit()
        return record
