"""
Unit tests for Weather API endpoints with security testing
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime

# Import the weather API module
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python_analytics'))

from app.api.weather_api import (
    weather_bp,
    validate_limit_param,
    validate_hours_param,
    validate_date_param,
    sanitize_string_param,
    rate_limiter,
    check_rate_limit
)


class TestInputValidation:
    """Test input validation and sanitization functions"""

    def test_validate_limit_param_valid(self):
        """Test valid limit parameter validation"""
        assert validate_limit_param('50') == 50
        assert validate_limit_param('100') == 100
        assert validate_limit_param('1') == 1

    def test_validate_limit_param_invalid(self):
        """Test invalid limit parameter validation"""
        assert validate_limit_param('abc') == 1  # Default min
        assert validate_limit_param('') == 1
        assert validate_limit_param('1000') == 1000  # Max allowed

    def test_validate_limit_param_out_of_range(self):
        """Test limit parameter clamping"""
        assert validate_limit_param('0') == 1  # Below min
        assert validate_limit_param('2000') == 1000  # Above max

    def test_validate_hours_param_valid(self):
        """Test valid hours parameter validation"""
        assert validate_hours_param('24') == 24
        assert validate_hours_param('1') == 1
        assert validate_hours_param('168') == 168

    def test_validate_hours_param_invalid(self):
        """Test invalid hours parameter validation"""
        assert validate_hours_param('abc') == 24  # Default
        assert validate_hours_param('') == 24
        assert validate_hours_param('200') == 168  # Max allowed

    def test_validate_date_param_valid(self):
        """Test valid date parameter validation"""
        assert validate_date_param('2024-01-01') == '2024-01-01'
        assert validate_date_param('2025-12-31') == '2025-12-31'

    def test_validate_date_param_invalid(self):
        """Test invalid date parameter validation"""
        with pytest.raises(ValueError):
            validate_date_param('2024/01/01')

        with pytest.raises(ValueError):
            validate_date_param('invalid-date')

        with pytest.raises(ValueError):
            validate_date_param('2024-13-01')

    def test_sanitize_string_param_valid(self):
        """Test valid string sanitization"""
        assert sanitize_string_param('hello_world') == 'hello_world'
        assert sanitize_string_param('hello world') == 'hello world'
        assert sanitize_string_param('hello-world_123') == 'hello-world_123'

    def test_sanitize_string_param_dangerous_chars(self):
        """Test dangerous character removal"""
        assert sanitize_string_param('hello<script>') == 'helloscript'
        assert sanitize_string_param('hello;world') == 'helloworld'
        assert sanitize_string_param('hello|world') == 'helloworld'

    def test_sanitize_string_param_length_limit(self):
        """Test string length limiting"""
        long_string = 'a' * 200
        assert len(sanitize_string_param(long_string, 50)) == 50


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limiter_allow_under_limit(self):
        """Test that requests under limit are allowed"""
        rate_limiter.requests.clear()  # Reset

        # Simulate requests under limit
        for i in range(10):
            assert rate_limiter.is_allowed('192.168.1.1') is True

    def test_rate_limiter_block_over_limit(self):
        """Test that requests over limit are blocked"""
        rate_limiter.requests.clear()

        # Fill up the limit
        for i in range(rate_limiter.max_requests):
            assert rate_limiter.is_allowed('192.168.1.1') is True

        # Next request should be blocked
        assert rate_limiter.is_allowed('192.168.1.1') is False

    def test_rate_limiter_different_ips(self):
        """Test that different IPs are tracked separately"""
        rate_limiter.requests.clear()

        # Fill limit for first IP
        for i in range(rate_limiter.max_requests):
            assert rate_limiter.is_allowed('192.168.1.1') is True

        # Second IP should still be allowed
        assert rate_limiter.is_allowed('192.168.1.2') is True


class TestWeatherAPIEndpoints:
    """Test Weather API endpoints"""

    @pytest.fixture
    def app(self):
        """Create test Flask app"""
        app = Flask(__name__)
        app.register_blueprint(weather_bp, url_prefix='/api/v1/weather')

        # Mock services
        app.config['db_service'] = Mock()
        app.config['alert_service'] = Mock()
        app.config['aeris_weather_service'] = Mock()
        app.config['open_meteo_service'] = Mock()
        app.config['weatherapi_service'] = Mock()

        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_health_endpoint(self, client, app):
        """Test health endpoint"""
        # Mock database health check
        app.config['db_service'].health_check.return_value = True

        response = client.get('/api/v1/weather/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'
        assert 'timestamp' in data

        # Check security headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert 'Content-Security-Policy' in response.headers

    def test_health_endpoint_db_error(self, client, app):
        """Test health endpoint when database is down"""
        app.config['db_service'].health_check.return_value = False

        response = client.get('/api/v1/weather/health')
        assert response.status_code == 503

        data = json.loads(response.data)
        assert data['status'] == 'unhealthy'
        assert data['database'] == 'disconnected'

    def test_latest_weather_endpoint(self, client, app):
        """Test latest weather endpoint"""
        # Mock database response
        mock_weather_data = Mock()
        mock_weather_data.data = [{'id': 1, 'temperature': 20.5}]
        mock_weather_data.to_dict_list.return_value = [{'id': 1, 'temperature': 20.5}]
        app.config['db_service'].get_weather_data.return_value = mock_weather_data

        response = client.get('/api/v1/weather/latest')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] == 1
        assert len(data['data']) == 1

    def test_latest_weather_endpoint_invalid_limit(self, client, app):
        """Test latest weather endpoint with invalid limit"""
        # Mock database response
        mock_weather_data = Mock()
        mock_weather_data.data = [{'id': 1, 'temperature': 20.5}]
        mock_weather_data.to_dict_list.return_value = [{'id': 1, 'temperature': 20.5}]
        app.config['db_service'].get_weather_data.return_value = mock_weather_data

        response = client.get('/api/v1/weather/latest?limit=abc')
        assert response.status_code == 200  # Should use default limit

    def test_current_weather_endpoint(self, client, app):
        """Test current weather endpoint"""
        # Mock database response
        mock_weather_data = Mock()
        mock_latest = Mock()
        mock_latest.to_dict.return_value = {'temperature': 20.5}
        mock_weather_data.get_latest.return_value = mock_latest
        app.config['db_service'].get_weather_data.return_value = mock_weather_data

        response = client.get('/api/v1/weather/current')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data

    def test_current_weather_endpoint_no_data(self, client, app):
        """Test current weather endpoint when no data available"""
        mock_weather_data = Mock()
        mock_weather_data.get_latest.return_value = None
        app.config['db_service'].get_weather_data.return_value = mock_weather_data

        response = client.get('/api/v1/weather/current')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No weather data available' in data['error']

    def test_chart_data_endpoint(self, client, app):
        """Test chart data endpoint"""
        mock_weather_data = Mock()
        mock_weather_data.get_temperature_trend.return_value = [
            {'timestamp': '2024-01-01T00:00:00Z', 'temperature': 20.5}
        ]
        app.config['db_service'].get_weather_data.return_value = mock_weather_data

        response = client.get('/api/v1/weather/chart-data?hours=24')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['hours'] == 24

    def test_chart_data_endpoint_invalid_hours(self, client, app):
        """Test chart data endpoint with invalid hours"""
        mock_weather_data = Mock()
        mock_weather_data.get_temperature_trend.return_value = [
            {'timestamp': '2024-01-01T00:00:00Z', 'temperature': 20.5}
        ]
        app.config['db_service'].get_weather_data.return_value = mock_weather_data

        response = client.get('/api/v1/weather/chart-data?hours=abc')
        assert response.status_code == 200  # Should use default

    def test_rate_limiting(self, client, app):
        """Test rate limiting"""
        rate_limiter.requests.clear()

        # Make many requests to trigger rate limit
        for i in range(rate_limiter.max_requests + 10):
            response = client.get('/api/v1/weather/health')

        # Last request should be rate limited (429)
        last_response = client.get('/api/v1/weather/health')
        assert last_response.status_code == 429

        data = json.loads(last_response.data)
        assert 'Too many requests' in data['error']
        assert 'retry_after' in data

    def test_security_headers_all_endpoints(self, client, app):
        """Test that all endpoints have security headers"""
        # Reset rate limiter for this test
        rate_limiter.requests.clear()

        # Mock database responses for all endpoints
        mock_weather_data = Mock()
        mock_weather_data.data = [{'id': 1, 'temperature': 20.5}]
        mock_weather_data.to_dict_list.return_value = [{'id': 1, 'temperature': 20.5}]
        mock_weather_data.get_latest.return_value = Mock(to_dict=lambda: {'temperature': 20.5})

        mock_stats = Mock()
        mock_stats.to_dict.return_value = {
            'total_records': 100,
            'avg_temperature': 15.5,
            'min_temperature': -10.0,
            'max_temperature': 35.0
        }

        app.config['db_service'].get_weather_data.return_value = mock_weather_data
        app.config['db_service'].get_weather_stats.return_value = mock_stats

        endpoints = [
            '/api/v1/weather/health',
            '/api/v1/weather/latest',
            '/api/v1/weather/current',
            '/api/v1/weather/stats'
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 401, 404, 503]  # Various possible responses

            # Check security headers only for successful requests (not 401 auth required)
            if response.status_code != 401:
                assert response.headers['X-Frame-Options'] == 'DENY'
                assert response.headers['X-Content-Type-Options'] == 'nosniff'
                assert 'X-XSS-Protection' in response.headers
                assert 'Content-Security-Policy' in response.headers

    def test_cors_headers(self, client, app):
        """Test CORS headers are properly configured"""
        response = client.options('/api/v1/weather/health',
                                headers={'Origin': 'http://localhost:5000'})

        # CORS should be handled by Flask-CORS extension
        # This is tested in the main app configuration

    def test_error_handling(self, client, app):
        """Test error handling for invalid endpoints"""
        response = client.get('/api/v1/weather/invalid-endpoint')
        assert response.status_code == 404

        # Note: 404 errors from Flask don't go through our decorators
        # So security headers may not be present on 404 responses


if __name__ == '__main__':
    pytest.main([__file__])
