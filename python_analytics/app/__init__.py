import logging
import os
import time
from flask import Flask, render_template, g
from flask_cors import CORS

from .api.weather_api import weather_bp
from .services.database_service import DatabaseService
from .services.alert_service import AlertService
from .services.aeris_weather_service import AerisWeatherService
from .services.open_meteo_service import OpenMeteoService
from .services.weatherapi_service import WeatherAPIService
from .utils.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=None) -> Flask:
    """Create and configure the Flask application"""
    app = Flask(__name__,
                template_folder="templates",
                static_folder="static")

    # Load configuration
    if config_class is None:
        config_class = Config

    # Set configuration manually to avoid property issues
    app.config['SECRET_KEY'] = config_class.SECRET_KEY
    app.config['DEBUG'] = config_class.DEBUG
    app.config['DATABASE_URL'] = f"postgresql://{os.getenv('POSTGRES_USER', 'etl_user')}:{os.getenv('POSTGRES_PASSWORD', 'supersecret')}@{os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'weather_db')}"
    app.config['OPENWEATHER_API_KEY'] = config_class.OPENWEATHER_API_KEY
    app.config['AERIS_CLIENT_ID'] = config_class.AERIS_CLIENT_ID
    app.config['AERIS_CLIENT_SECRET'] = config_class.AERIS_CLIENT_SECRET
    app.config['CITY'] = config_class.CITY
    app.config['ETL_INTERVAL'] = config_class.ETL_INTERVAL
    app.config['HOST'] = config_class.HOST
    app.config['PORT'] = config_class.PORT
    app.config['TELEGRAM_TOKEN'] = config_class.TELEGRAM_TOKEN
    app.config['TELEGRAM_CHAT_ID'] = config_class.TELEGRAM_CHAT_ID

    # Initialize extensions with secure CORS configuration
    CORS(app,
         origins=[
             "http://localhost:5000",
             "http://127.0.0.1:5000",
             "http://localhost:8080",
             "http://127.0.0.1:8080"
         ],
         methods=["GET", "POST", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=False,
         max_age=86400  # 24 hours
    )

    # Initialize services
    db_service = DatabaseService(app.config['DATABASE_URL'])
    alert_service = AlertService()
    aeris_weather_service = AerisWeatherService()
    open_meteo_service = OpenMeteoService()
    weatherapi_service = WeatherAPIService()

    # Store services in app context
    app.config['db_service'] = db_service
    app.config['alert_service'] = alert_service
    app.config['aeris_weather_service'] = aeris_weather_service
    app.config['open_meteo_service'] = open_meteo_service
    app.config['weatherapi_service'] = weatherapi_service

    # Register blueprints
    app.register_blueprint(weather_bp, url_prefix='/api/v1/weather')

    # Security middleware - request logging
    @app.before_request
    def log_request_info():
        """Log security-relevant request information"""
        client_ip = request.remote_addr or request.headers.get('X-Forwarded-For', 'unknown')
        user_agent = request.headers.get('User-Agent', 'unknown')
        method = request.method
        path = request.path
        query_string = request.query_string.decode('utf-8') if request.query_string else ''

        # Log security events
        if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            logger.warning(f"SECURITY: {method} request to {path} from {client_ip}")

        # Log all API requests for monitoring
        if path.startswith('/api/'):
            logger.info(f"API_REQUEST: {method} {path} from {client_ip} - UA: {user_agent[:50]}...")

        # Store request info for potential security analysis
        g.request_start_time = time.time()
        g.client_ip = client_ip
        g.user_agent = user_agent

    @app.after_request
    def log_response_info(response):
        """Log response information and timing"""
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            status_code = response.status_code
            client_ip = getattr(g, 'client_ip', 'unknown')

            # Log slow requests or errors
            if duration > 5.0:  # 5 seconds
                logger.warning(f"SLOW_REQUEST: {request.method} {request.path} took {duration:.2f}s from {client_ip}")

            if status_code >= 400:
                logger.warning(f"ERROR_RESPONSE: {status_code} for {request.method} {request.path} from {client_ip}")

        return response

    # Register routes
    register_routes(app)

    # Health check at root
    @app.route('/')
    def index():
        """Root endpoint with API information"""
        return {
            'message': 'Montreal Weather Dashboard API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/v1/weather/health',
                'latest': '/api/v1/weather/latest',
                'current': '/api/v1/weather/current',
                'stats': '/api/v1/weather/stats',
                'chart_data': '/api/v1/weather/chart-data',
                'aeris_montreal': '/api/v1/weather/aeris/montreal',
                'aeris_csv': '/api/v1/weather/aeris/montreal/csv',
                'aeris_locations': '/api/v1/weather/aeris/locations?locations=montreal,ca&locations=toronto,ca',
                'aeris_historical_date': '/api/v1/weather/aeris/historical/2024-01-01',
                'aeris_historical_range': '/api/v1/weather/aeris/historical?start_date=2024-01-01&end_date=2024-01-05',
                'aeris_historical_csv': '/api/v1/weather/aeris/historical/csv?start_date=2024-01-01&end_date=2024-01-05',
                'openmeteo_current': '/api/v1/weather/openmeteo/current',
                'openmeteo_forecast': '/api/v1/weather/openmeteo/forecast?days=7',
                'openmeteo_historical': '/api/v1/weather/openmeteo/historical?start_date=2024-01-01&end_date=2024-01-31',
                'openmeteo_monitoring': '/api/v1/weather/openmeteo/monitoring?weeks=4',
                'openmeteo_csv': '/api/v1/weather/openmeteo/historical/csv?start_date=2024-01-01&end_date=2024-01-31',
                'long_term_monitoring': '/api/v1/weather/openmeteo/long-term?years=2',
                'seasonal_analysis': '/api/v1/weather/openmeteo/seasonal-analysis?years=2',
                'yearly_trends': '/api/v1/weather/openmeteo/yearly-trends?years=2',
                'monitoring_status': '/api/v1/weather/monitoring/status',
                'weatherapi_current': '/api/v1/weather/weatherapi/current',
                'weatherapi_forecast': '/api/v1/weather/weatherapi/forecast?days=7',
                'weatherapi_realtime': '/api/v1/weather/weatherapi/realtime',
                'weatherapi_status': '/api/v1/weather/weatherapi/status',
                'dashboard': '/dashboard'
            }
        }

    logger.info("Flask application created successfully")
    return app


def register_routes(app: Flask):
    """Register additional routes"""
    @app.route('/dashboard')
    def dashboard():
        """Serve the dashboard page"""
        try:
            db_service = app.config['db_service']
            weather_data = db_service.get_weather_data(limit=1)
            latest_weather = weather_data.get_latest()

            # Get chart data for the last 24 hours
            chart_weather = db_service.get_weather_data(limit=48)  # More data for charts
            chart_data = {
                'temperature': chart_weather.get_temperature_trend(24),
                'humidity': [{'timestamp': item['timestamp'], 'humidity': item['humidity']} for item in chart_weather.get_temperature_trend(24)]
            }

            return render_template('dashboard.html',
                                   latest_weather=latest_weather,
                                   chart_data=chart_data)

        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            alert_service = app.config['alert_service']
            alert_service.send_error_alert(str(e), "dashboard")
            return "Dashboard temporarily unavailable", 500


if __name__ == "__main__":
    app = create_app()
    logger.info("Starting Montreal Weather Dashboard server...")

    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true"
    )
