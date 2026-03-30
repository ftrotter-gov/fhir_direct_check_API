"""Rate limiting middleware for IP-based access control."""
from functools import wraps
from flask import request, jsonify, current_app
from collections import defaultdict
from datetime import datetime, timedelta
import threading


class RateLimiter:
    """
    IP-based rate limiter with localhost exemption.
    
    Tracks request counts per IP address and enforces rate limits
    for non-localhost connections.
    """
    
    def __init__(self):
        """Initialize rate limiter with thread-safe request tracking."""
        self.request_counts = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_localhost(self, *, ip_address):
        """
        Check if IP address is localhost.
        
        Args:
            ip_address: The IP address to check
            
        Returns:
            bool: True if localhost, False otherwise
        """
        localhost_ips = ['127.0.0.1', '::1', 'localhost']
        return ip_address in localhost_ips
    
    def check_rate_limit(self, *, ip_address, max_requests, time_window_minutes):
        """
        Check if IP address is within rate limit.
        
        Args:
            ip_address: The IP address to check
            max_requests: Maximum requests allowed
            time_window_minutes: Time window in minutes
            
        Returns:
            tuple: (is_allowed: bool, remaining: int)
        """
        # Localhost is always allowed
        if self.is_localhost(ip_address=ip_address):
            return True, -1  # -1 indicates unlimited
        
        with self.lock:
            now = datetime.utcnow()
            cutoff_time = now - timedelta(minutes=time_window_minutes)
            
            # Remove old requests outside the time window
            self.request_counts[ip_address] = [
                timestamp for timestamp in self.request_counts[ip_address]
                if timestamp > cutoff_time
            ]
            
            # Check if under the limit
            current_count = len(self.request_counts[ip_address])
            
            if current_count < max_requests:
                # Add current request
                self.request_counts[ip_address].append(now)
                remaining = max_requests - current_count - 1
                return True, remaining
            else:
                remaining = 0
                return False, remaining
    
    def cleanup_old_entries(self, *, time_window_minutes):
        """
        Clean up old entries from request tracking.
        
        Args:
            time_window_minutes: Time window in minutes
        """
        with self.lock:
            now = datetime.utcnow()
            cutoff_time = now - timedelta(minutes=time_window_minutes)
            
            # Remove IPs with no recent requests
            ips_to_remove = []
            for ip_address, timestamps in self.request_counts.items():
                # Filter out old timestamps
                recent = [ts for ts in timestamps if ts > cutoff_time]
                if recent:
                    self.request_counts[ip_address] = recent
                else:
                    ips_to_remove.append(ip_address)
            
            # Remove IPs with no recent activity
            for ip_address in ips_to_remove:
                del self.request_counts[ip_address]


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit_check(f):
    """
    Decorator to enforce rate limiting on Flask routes.
    
    Checks rate limits before executing the decorated function.
    Returns 429 if rate limit exceeded.
    
    Args:
        f: The function to decorate
        
    Returns:
        function: Decorated function with rate limiting
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client IP address
        ip_address = request.remote_addr
        
        # Get rate limit configuration from app config
        max_requests = current_app.config.get('RATE_LIMIT_REQUESTS', 100)
        time_window_minutes = current_app.config.get('RATE_LIMIT_PERIOD_MINUTES', 5)
        
        # Check rate limit
        is_allowed, remaining = rate_limiter.check_rate_limit(
            ip_address=ip_address,
            max_requests=max_requests,
            time_window_minutes=time_window_minutes
        )
        
        if not is_allowed:
            return jsonify({
                'error': 'Rate Limit Exceeded',
                'message': f'You have exceeded the rate limit of {max_requests} requests per {time_window_minutes} minutes',
                'retry_after': f'{time_window_minutes} minutes'
            }), 429
        
        # Add rate limit info to response headers
        response = f(*args, **kwargs)
        
        # If response is a tuple (response, status_code), handle appropriately
        if isinstance(response, tuple):
            response_obj, status_code = response[0], response[1]
            if hasattr(response_obj, 'headers') and remaining >= 0:
                response_obj.headers['X-RateLimit-Limit'] = str(max_requests)
                response_obj.headers['X-RateLimit-Remaining'] = str(remaining)
            return response_obj, status_code
        else:
            if hasattr(response, 'headers') and remaining >= 0:
                response.headers['X-RateLimit-Limit'] = str(max_requests)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
            return response
    
    return decorated_function
