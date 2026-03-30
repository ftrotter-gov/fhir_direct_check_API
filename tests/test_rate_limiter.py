"""Unit tests for rate limiter."""
import pytest
from app.rate_limiter import RateLimiter


class TestRateLimiter:
    """Tests for RateLimiter class."""
    
    def test_localhost_detection_ipv4(self):
        """Test localhost detection for IPv4."""
        limiter = RateLimiter()
        assert limiter.is_localhost(ip_address='127.0.0.1') is True
    
    def test_localhost_detection_ipv6(self):
        """Test localhost detection for IPv6."""
        limiter = RateLimiter()
        assert limiter.is_localhost(ip_address='::1') is True
    
    def test_localhost_detection_hostname(self):
        """Test localhost detection for hostname."""
        limiter = RateLimiter()
        assert limiter.is_localhost(ip_address='localhost') is True
    
    def test_non_localhost_detection(self):
        """Test non-localhost IP detection."""
        limiter = RateLimiter()
        assert limiter.is_localhost(ip_address='192.168.1.1') is False
    
    def test_localhost_unlimited_access(self):
        """Test localhost has unlimited access."""
        limiter = RateLimiter()
        is_allowed, remaining = limiter.check_rate_limit(
            ip_address='127.0.0.1',
            max_requests=100,
            time_window_minutes=5
        )
        assert is_allowed is True
        assert remaining == -1
    
    def test_rate_limit_allows_under_limit(self):
        """Test rate limit allows requests under limit."""
        limiter = RateLimiter()
        is_allowed, remaining = limiter.check_rate_limit(
            ip_address='192.168.1.1',
            max_requests=10,
            time_window_minutes=5
        )
        assert is_allowed is True
        assert remaining >= 0
    
    def test_rate_limit_tracks_requests(self):
        """Test rate limiter tracks multiple requests."""
        limiter = RateLimiter()
        ip = '192.168.1.1'
        max_requests = 3
        
        # Make requests up to limit
        for i in range(max_requests):
            is_allowed, remaining = limiter.check_rate_limit(
                ip_address=ip,
                max_requests=max_requests,
                time_window_minutes=5
            )
            assert is_allowed is True
        
        # Next request should be denied
        is_allowed, remaining = limiter.check_rate_limit(
            ip_address=ip,
            max_requests=max_requests,
            time_window_minutes=5
        )
        assert is_allowed is False
        assert remaining == 0
    
    def test_rate_limit_independent_ips(self):
        """Test rate limits are independent per IP."""
        limiter = RateLimiter()
        
        # First IP makes requests
        is_allowed1, _ = limiter.check_rate_limit(
            ip_address='192.168.1.1',
            max_requests=1,
            time_window_minutes=5
        )
        
        # Second IP should still be allowed
        is_allowed2, _ = limiter.check_rate_limit(
            ip_address='192.168.1.2',
            max_requests=1,
            time_window_minutes=5
        )
        
        assert is_allowed1 is True
        assert is_allowed2 is True
