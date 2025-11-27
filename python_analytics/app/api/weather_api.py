import logging
from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any
from ..services.database_service import DatabaseService
from ..services.alert_service import AlertService

logger = logging.getLogger(__name__)
weather_bp = Blueprint('weather', __name__)


def get_db_service() -> DatabaseService:
    """Get database service from app context"""
    return current_app.config['db_service']


def get_alert_service() -> AlertService:
    """Get alert service from app context"""
    return current_app.config['alert_service']


@weather_bp.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        db_service = get_db_service()
        db_healthy = db_service.health_check()

        return jsonify({
            'status': 'healthy' if db_healthy else 'unhealthy',
            'database': 'connected' if db_healthy else 'disconnected',
            'timestamp': '2024-01-01T00:00:00Z'  # Would use datetime.utcnow() in real implementation
        }), 200 if db_healthy else 503

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@weather_bp.route('/latest')
def get_latest_weather():
    """Get latest weather data"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        limit = min(max(limit, 1), 1000)  # Clamp between 1 and 1000

        db_service = get_db_service()
        weather_data = db_service.get_weather_data(limit=limit)

        return jsonify({
            'success': True,
            'count': len(weather_data.data),
            'data': weather_data.to_dict_list()
        })

    except Exception as e:
        logger.error(f"Failed to fetch latest weather: {e}")
        alert_service = get_alert_service()
        alert_service.send_error_alert(str(e), "latest weather endpoint")

        return jsonify({
            'success': False,
            'error': 'Failed to fetch weather data',
            'details': str(e)
        }), 500


@weather_bp.route('/current')
def get_current_weather():
    """Get current (latest) weather conditions"""
    try:
        db_service = get_db_service()
        weather_data = db_service.get_weather_data(limit=1)

        latest = weather_data.get_latest()

        if latest:
            return jsonify({
                'success': True,
                'data': latest.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No weather data available'
            }), 404

    except Exception as e:
        logger.error(f"Failed to fetch current weather: {e}")
        alert_service = get_alert_service()
        alert_service.send_error_alert(str(e), "current weather endpoint")

        return jsonify({
            'success': False,
            'error': 'Failed to fetch current weather',
            'details': str(e)
        }), 500


@weather_bp.route('/stats')
def get_weather_stats():
    """Get weather statistics"""
    try:
        db_service = get_db_service()
        stats = db_service.get_weather_stats()

        return jsonify({
            'success': True,
            'data': stats.to_dict()
        })

    except Exception as e:
        logger.error(f"Failed to fetch weather stats: {e}")
        alert_service = get_alert_service()
        alert_service.send_error_alert(str(e), "weather stats endpoint")

        return jsonify({
            'success': False,
            'error': 'Failed to fetch weather statistics',
            'details': str(e)
        }), 500


@weather_bp.route('/chart-data')
def get_chart_data():
    """Get data formatted for charts"""
    try:
        hours = request.args.get('hours', default=24, type=int)
        hours = min(max(hours, 1), 168)  # Clamp between 1 and 168 hours (1 week)

        db_service = get_db_service()
        weather_data = db_service.get_weather_data(limit=hours * 2)  # Get more data than needed

        chart_data = weather_data.get_temperature_trend(hours)

        return jsonify({
            'success': True,
            'hours': hours,
            'count': len(chart_data),
            'data': chart_data
        })

    except Exception as e:
        logger.error(f"Failed to fetch chart data: {e}")
        alert_service = get_alert_service()
        alert_service.send_error_alert(str(e), "chart data endpoint")

        return jsonify({
            'success': False,
            'error': 'Failed to fetch chart data',
            'details': str(e)
        }), 500


@weather_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/health',
            '/latest',
            '/current',
            '/stats',
            '/chart-data'
        ]
    }), 404


@weather_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    alert_service = AlertService()
    alert_service.send_error_alert("Internal server error occurred", "API")

    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

