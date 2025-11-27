import logging
import os
from flask import Flask
from flask_cors import CORS

from .api.weather_api import weather_bp
from .services.database_service import DatabaseService
from .services.alert_service import AlertService
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
    app.config['DATABASE_URL'] = config_class.DATABASE_URL
    app.config['OPENWEATHER_API_KEY'] = config_class.OPENWEATHER_API_KEY
    app.config['CITY'] = config_class.CITY
    app.config['ETL_INTERVAL'] = config_class.ETL_INTERVAL
    app.config['HOST'] = config_class.HOST
    app.config['PORT'] = config_class.PORT
    app.config['TELEGRAM_TOKEN'] = config_class.TELEGRAM_TOKEN
    app.config['TELEGRAM_CHAT_ID'] = config_class.TELEGRAM_CHAT_ID

    # Initialize extensions
    CORS(app)

    # Initialize services
    db_service = DatabaseService(app.config['DATABASE_URL'])
    alert_service = AlertService()

    # Store services in app context
    app.config['db_service'] = db_service
    app.config['alert_service'] = alert_service

    # Register blueprints
    app.register_blueprint(weather_bp, url_prefix='/api/v1/weather')

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

            return app.render_template('dashboard.html',
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
