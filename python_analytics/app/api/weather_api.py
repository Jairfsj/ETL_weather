import logging
from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any
from datetime import datetime
from ..services.database_service import DatabaseService
from ..services.alert_service import AlertService
from ..services.aeris_weather_service import AerisWeatherService
from ..services.open_meteo_service import OpenMeteoService

logger = logging.getLogger(__name__)
weather_bp = Blueprint('weather', __name__)


def get_db_service() -> DatabaseService:
    """Get database service from app context"""
    return current_app.config['db_service']


def get_alert_service() -> AlertService:
    """Get alert service from app context"""
    return current_app.config['alert_service']


def get_aeris_weather_service() -> AerisWeatherService:
    """Get AerisWeather service from app context"""
    return current_app.config['aeris_weather_service']


def get_open_meteo_service() -> OpenMeteoService:
    """Get Open-Meteo service from app context"""
    return current_app.config['open_meteo_service']


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


# AerisWeather API endpoints

@weather_bp.route('/aeris/montreal')
def get_aeris_montreal_weather():
    """Get current Montreal weather data from AerisWeather API"""
    try:
        aeris_service = get_aeris_weather_service()
        weather_summary = aeris_service.get_montreal_weather_summary()

        if weather_summary is None:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch weather data from AerisWeather API. Check API credentials.'
            }), 503

        return jsonify({
            'success': True,
            'data': weather_summary,
            'source': 'AerisWeather'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching AerisWeather data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/aeris/montreal/csv')
def download_aeris_montreal_csv():
    """Download Montreal weather data as CSV from AerisWeather API"""
    try:
        aeris_service = get_aeris_weather_service()
        df = aeris_service.get_montreal_weather()

        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': 'No weather data available for download'
            }), 404

        csv_path = aeris_service.save_to_csv(df)

        if csv_path is None:
            return jsonify({
                'success': False,
                'error': 'Failed to save CSV file'
            }), 500

        return jsonify({
            'success': True,
            'message': 'CSV file created successfully',
            'file_path': csv_path,
            'source': 'AerisWeather'
        }), 200

    except Exception as e:
        logger.error(f"Error creating CSV from AerisWeather data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/aeris/locations')
def get_aeris_multiple_locations():
    """Get weather data for multiple locations from AerisWeather API"""
    try:
        locations = request.args.getlist('locations')

        if not locations:
            return jsonify({
                'success': False,
                'error': 'No locations provided. Use ?locations=montreal,ca&locations=toronto,ca'
            }), 400

        custom_fields = request.args.getlist('fields')

        aeris_service = get_aeris_weather_service()
        df = aeris_service.locations_loop(locations, custom_fields if custom_fields else None)

        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': 'No weather data found for the specified locations'
            }), 404

        # Convert DataFrame to dict for JSON response
        result = df.to_dict('records')

        return jsonify({
            'success': True,
            'data': result,
            'count': len(result),
            'source': 'AerisWeather'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching multiple locations from AerisWeather: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# AerisWeather Historical Data endpoints

@weather_bp.route('/aeris/historical/<date>')
def get_aeris_historical_date(date):
    """Get historical weather data for a specific date from AerisWeather API"""
    try:
        # Parse date
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400

        locations = request.args.getlist('locations')
        if not locations:
            locations = ['montreal,ca']

        custom_fields = request.args.getlist('fields')

        aeris_service = get_aeris_weather_service()
        df = aeris_service.get_historical_weather_date(target_date, locations, custom_fields if custom_fields else None)

        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': f'No historical data found for date {date}'
            }), 404

        # Convert DataFrame to dict for JSON response
        result = df.to_dict('records')

        return jsonify({
            'success': True,
            'data': result,
            'date': date,
            'locations': locations,
            'count': len(result),
            'source': 'AerisWeather'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching historical data for date {date}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/aeris/historical')
def get_aeris_historical_range():
    """Get historical weather data for a date range from AerisWeather API"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': 'Both start_date and end_date are required (format: YYYY-MM-DD)'
            }), 400

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400

        if start_date > end_date:
            return jsonify({
                'success': False,
                'error': 'start_date must be before or equal to end_date'
            }), 400

        locations = request.args.getlist('locations')
        if not locations:
            locations = ['montreal,ca']

        custom_fields = request.args.getlist('fields')

        aeris_service = get_aeris_weather_service()
        results = aeris_service.get_historical_weather_range(start_date, end_date, locations, custom_fields if custom_fields else None)

        if results is None or len(results) == 0:
            return jsonify({
                'success': False,
                'error': f'No historical data found for date range {start_date_str} to {end_date_str}'
            }), 404

        return jsonify({
            'success': True,
            'data': results,
            'date_range': {
                'start': start_date_str,
                'end': end_date_str
            },
            'locations': locations,
            'total_dates': len(results),
            'source': 'AerisWeather'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching historical data range: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/aeris/historical/csv')
def generate_aeris_historical_csvs():
    """Generate CSV files for historical weather data"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': 'Both start_date and end_date are required (format: YYYY-MM-DD)'
            }), 400

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400

        if start_date > end_date:
            return jsonify({
                'success': False,
                'error': 'start_date must be before or equal to end_date'
            }), 400

        # Check date range (limit to prevent abuse)
        date_range_days = (end_date - start_date).days + 1
        if date_range_days > 30:
            return jsonify({
                'success': False,
                'error': 'Date range cannot exceed 30 days'
            }), 400

        locations = request.args.getlist('locations')
        if not locations:
            locations = ['montreal,ca']

        custom_fields = request.args.getlist('fields')

        # Create date range
        dt_list = pd.date_range(start=start_date, end=end_date, freq='D')

        aeris_service = get_aeris_weather_service()
        generated_files = aeris_service.generate_historical_csvs(dt_list, locations, custom_fields=custom_fields if custom_fields else None)

        if not generated_files:
            return jsonify({
                'success': False,
                'error': 'No CSV files were generated'
            }), 404

        return jsonify({
            'success': True,
            'message': f'Successfully generated {len(generated_files)} historical CSV files',
            'files': generated_files,
            'date_range': {
                'start': start_date_str,
                'end': end_date_str,
                'days': date_range_days
            },
            'locations': locations,
            'source': 'AerisWeather'
        }), 200

    except Exception as e:
        logger.error(f"Error generating historical CSV files: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Open-Meteo API endpoints (Melhor opção para monitoramento semi-real)

@weather_bp.route('/openmeteo/current')
def get_openmeteo_current():
    """Get current weather data from Open-Meteo API (best for real-time monitoring)"""
    try:
        openmeteo_service = get_open_meteo_service()
        weather_data = openmeteo_service.get_current_weather()

        if weather_data is None:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch current weather data from Open-Meteo'
            }), 503

        return jsonify({
            'success': True,
            'data': weather_data,
            'source': 'Open-Meteo',
            'note': 'Best API for real-time Montreal monitoring (no API key required)'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching Open-Meteo current weather: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/openmeteo/forecast')
def get_openmeteo_forecast():
    """Get weather forecast from Open-Meteo API"""
    try:
        days = request.args.get('days', default=7, type=int)
        days = min(max(days, 1), 16)  # Limit between 1 and 16 days

        openmeteo_service = get_open_meteo_service()
        forecast_data = openmeteo_service.get_forecast_weather(days)

        if forecast_data is None or len(forecast_data) == 0:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch forecast data from Open-Meteo'
            }), 503

        return jsonify({
            'success': True,
            'data': forecast_data,
            'days': len(forecast_data),
            'source': 'Open-Meteo'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching Open-Meteo forecast: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/openmeteo/historical')
def get_openmeteo_historical():
    """Get historical weather data from Open-Meteo API"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': 'Both start_date and end_date are required (format: YYYY-MM-DD)'
            }), 400

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400

        if start_date > end_date:
            return jsonify({
                'success': False,
                'error': 'start_date must be before or equal to end_date'
            }), 400

        # Check date range (max 1 year for Open-Meteo)
        date_diff = (end_date - start_date).days
        if date_diff > 365:
            return jsonify({
                'success': False,
                'error': 'Date range cannot exceed 365 days for Open-Meteo API'
            }), 400

        openmeteo_service = get_open_meteo_service()
        df = openmeteo_service.get_historical_weather(start_date, end_date)

        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': f'No historical data found for date range {start_date_str} to {end_date_str}'
            }), 404

        # Convert DataFrame to dict for JSON response
        result = df.to_dict('records')

        return jsonify({
            'success': True,
            'data': result,
            'date_range': {
                'start': start_date_str,
                'end': end_date_str,
                'days': len(result)
            },
            'source': 'Open-Meteo',
            'note': 'Free historical data up to 60 years available'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching Open-Meteo historical data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/openmeteo/monitoring')
def get_openmeteo_monitoring():
    """Get weekly monitoring data (3-4 times per week) from Open-Meteo API"""
    try:
        weeks_back = request.args.get('weeks', default=4, type=int)
        weeks_back = min(max(weeks_back, 1), 52)  # Limit between 1 and 52 weeks

        openmeteo_service = get_open_meteo_service()
        df = openmeteo_service.get_weekly_monitoring_data(weeks_back)

        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': f'No monitoring data found for {weeks_back} weeks back'
            }), 404

        # Convert DataFrame to dict for JSON response
        result = df.to_dict('records')

        # Generate summary
        summary = openmeteo_service.get_monitoring_summary(weeks_back)

        return jsonify({
            'success': True,
            'data': result,
            'summary': summary,
            'monitoring_schedule': '3 times per week (Mon, Wed, Fri)',
            'weeks_back': weeks_back,
            'total_records': len(result),
            'source': 'Open-Meteo',
            'note': 'Optimized for semi-real monitoring (3-4 times per week)'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching Open-Meteo monitoring data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/openmeteo/historical/csv')
def generate_openmeteo_historical_csv():
    """Generate CSV file with historical weather data from Open-Meteo"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': 'Both start_date and end_date are required (format: YYYY-MM-DD)'
            }), 400

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400

        if start_date > end_date:
            return jsonify({
                'success': False,
                'error': 'start_date must be before or equal to end_date'
            }), 400

        openmeteo_service = get_open_meteo_service()
        df = openmeteo_service.get_historical_weather(start_date, end_date)

        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': 'No data available for CSV generation'
            }), 404

        csv_path = openmeteo_service.save_to_csv(df)

        if csv_path is None:
            return jsonify({
                'success': False,
                'error': 'Failed to save CSV file'
            }), 500

        return jsonify({
            'success': True,
            'message': 'Open-Meteo historical CSV generated successfully',
            'file_path': csv_path,
            'date_range': {
                'start': start_date_str,
                'end': end_date_str,
                'days': len(df)
            },
            'source': 'Open-Meteo'
        }), 200

    except Exception as e:
        logger.error(f"Error generating Open-Meteo historical CSV: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Long-term monitoring endpoints (2024-2026)

@weather_bp.route('/openmeteo/long-term')
def get_openmeteo_long_term():
    """Get long-term monitoring data (2024-2026)"""
    try:
        years = request.args.get('years', default=2, type=int)
        years = min(max(years, 1), 3)  # Limit to 1-3 years

        openmeteo_service = get_open_meteo_service()
        df = openmeteo_service.get_long_term_monitoring_data(years)

        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': f'No long-term monitoring data found for {years} years'
            }), 404

        # Convert DataFrame to dict for JSON response
        result = df.to_dict('records')

        return jsonify({
            'success': True,
            'data': result,
            'period': f'2024-{2024 + years - 1}',
            'years': years,
            'total_records': len(result),
            'monitoring_frequency': '3 times per week (Mon, Wed, Fri)',
            'source': 'Open-Meteo',
            'note': 'Long-term climate monitoring data for Montreal'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching long-term monitoring data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/openmeteo/seasonal-analysis')
def get_openmeteo_seasonal_analysis():
    """Get seasonal analysis of climate data"""
    try:
        years = request.args.get('years', default=2, type=int)
        years = min(max(years, 1), 3)  # Limit to 1-3 years

        openmeteo_service = get_open_meteo_service()
        seasonal_data = openmeteo_service.get_seasonal_analysis(years)

        if seasonal_data is None or len(seasonal_data) == 0:
            return jsonify({
                'success': False,
                'error': f'No seasonal analysis data available for {years} years'
            }), 404

        return jsonify({
            'success': True,
            'data': seasonal_data,
            'period': f'2024-{2024 + years - 1}',
            'years': years,
            'seasons': list(seasonal_data.keys()),
            'source': 'Open-Meteo',
            'analysis_type': 'seasonal_climate_analysis'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching seasonal analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/openmeteo/yearly-trends')
def get_openmeteo_yearly_trends():
    """Get yearly trends analysis"""
    try:
        years = request.args.get('years', default=2, type=int)
        years = min(max(years, 1), 3)  # Limit to 1-3 years

        openmeteo_service = get_open_meteo_service()
        yearly_data = openmeteo_service.get_yearly_trends(years)

        if yearly_data is None or len(yearly_data) == 0:
            return jsonify({
                'success': False,
                'error': f'No yearly trends data available for {years} years'
            }), 404

        return jsonify({
            'success': True,
            'data': yearly_data,
            'period': f'2024-{2024 + years - 1}',
            'years': years,
            'analyzed_years': list(yearly_data.keys()),
            'source': 'Open-Meteo',
            'analysis_type': 'yearly_climate_trends'
        }), 200

    except Exception as e:
        logger.error(f"Error fetching yearly trends: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@weather_bp.route('/monitoring/status')
def get_monitoring_status():
    """Get current monitoring system status"""
    try:
        today = datetime.now().date()
        current_year = today.year

        # Calculate monitoring progress
        total_years = 3  # 2024-2026
        years_completed = current_year - 2024
        progress_percentage = min(100, max(0, (years_completed / total_years) * 100))

        # Check if today is a monitoring day
        monitoring_days = [0, 2, 4]  # Mon, Wed, Fri
        is_monitoring_day = today.weekday() in monitoring_days

        # Get next monitoring date
        next_monitoring = today
        while next_monitoring.weekday() not in monitoring_days:
            next_monitoring += timedelta(days=1)

        status_info = {
            'system_status': 'active',
            'monitoring_period': '2024-2026',
            'current_year': current_year,
            'years_remaining': 2026 - current_year,
            'progress_percentage': round(progress_percentage, 1),
            'monitoring_frequency': '3 times per week',
            'monitoring_days': ['Monday', 'Wednesday', 'Friday'],
            'is_monitoring_day_today': is_monitoring_day,
            'next_monitoring_date': next_monitoring.strftime('%Y-%m-%d'),
            'data_sources': ['Open-Meteo (Primary)', 'AerisWeather (Backup)'],
            'last_updated': datetime.now().isoformat(),
            'reports_generated': 'Monthly and yearly climate reports',
            'alerts_system': 'Extreme weather condition alerts'
        }

        return jsonify({
            'success': True,
            'status': status_info,
            'message': f'Climate monitoring system active - {progress_percentage:.1f}% through the 2024-2026 period'
        }), 200

    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


