import os
from typing import Optional


class Config:
    """Base configuration class"""

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Database configuration
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'etl_user')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'supersecret')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'weather_db')

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from environment variables"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # OpenWeatherMap configuration
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    CITY = os.getenv('CITY', 'Montreal')

    # ETL configuration
    ETL_INTERVAL = int(os.getenv('ETL_INTERVAL', '300'))

    # Flask server configuration
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '5000'))

    # Telegram alerts
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SECRET_KEY = 'dev-secret-key'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    @property
    def SECRET_KEY(self) -> str:
        """Require secret key in production"""
        secret = os.getenv('SECRET_KEY')
        if not secret:
            raise ValueError("SECRET_KEY environment variable is required in production")
        return secret


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    # Use in-memory SQLite for tests
    DATABASE_URL = "sqlite:///:memory:"


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}


def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    return config.get(config_name.lower(), config['default'])()

