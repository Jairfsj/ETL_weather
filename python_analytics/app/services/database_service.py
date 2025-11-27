import logging
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ..models.weather import WeatherData, WeatherStats, WeatherDataList

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations"""

    def __init__(self, connection_string: str):
        logger.info(f"DatabaseService init - received: {connection_string}")
        logger.info(f"Type: {type(connection_string)}")
        self.connection_string = str(connection_string)  # Ensure it's a string
        logger.info(f"After conversion: {self.connection_string}")
        self._engine: Optional[Engine] = None

    @property
    def engine(self) -> Engine:
        """Lazy-loaded database engine"""
        if self._engine is None:
            logger.info(f"Creating engine with connection string: {self.connection_string}")
            logger.info(f"Connection string type: {type(self.connection_string)}")
            self._engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            logger.info("Database connection established")
        return self._engine

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    def get_weather_data(self, limit: int = 100) -> WeatherDataList:
        """Fetch weather data from database"""
        try:
            query = """
                SELECT id, city, temperature, feels_like, humidity, pressure,
                       wind_speed, wind_direction, weather_main, weather_description,
                       weather_icon, timestamp, timezone, created_at
                FROM weather_data
                ORDER BY timestamp DESC
                LIMIT %s
            """ % limit

            df = pd.read_sql(query, self.engine)

            weather_data = []
            for _, row in df.iterrows():
                weather_data.append(WeatherData.from_db_row(row))

            logger.info(f"Retrieved {len(weather_data)} weather records")
            return WeatherDataList(weather_data)

        except Exception as e:
            logger.error(f"Failed to fetch weather data: {e}")
            raise

    def get_weather_stats(self) -> WeatherStats:
        """Get weather statistics"""
        try:
            query = """
                SELECT
                    COUNT(*) as total_records,
                    AVG(temperature) as avg_temperature,
                    MIN(temperature) as min_temperature,
                    MAX(temperature) as max_temperature,
                    AVG(humidity) as avg_humidity,
                    AVG(wind_speed) as avg_wind_speed,
                    MODE() WITHIN GROUP (ORDER BY weather_main) as most_common_weather,
                    MAX(created_at) as last_updated
                FROM weather_data
            """

            with self.get_connection() as conn:
                result = conn.execute(text(query))
                row = result.fetchone()

            if row:
                return WeatherStats(
                    total_records=row[0] or 0,
                    avg_temperature=row[1] or 0.0,
                    min_temperature=row[2] or 0.0,
                    max_temperature=row[3] or 0.0,
                    avg_humidity=row[4] or 0.0,
                    avg_wind_speed=row[5] or 0.0,
                    most_common_weather=row[6] or "Unknown",
                    last_updated=row[7]
                )
            else:
                # Return empty stats if no data
                from datetime import datetime
                return WeatherStats(
                    total_records=0,
                    avg_temperature=0.0,
                    min_temperature=0.0,
                    max_temperature=0.0,
                    avg_humidity=0.0,
                    avg_wind_speed=0.0,
                    most_common_weather="No data",
                    last_updated=datetime.utcnow()
                )

        except Exception as e:
            logger.error(f"Failed to fetch weather stats: {e}")
            raise

    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            logger.info(f"Testing connection to: {self.connection_string}")
            # Simple connection test
            conn = self.engine.connect()
            conn.execute(text("SELECT 1"))
            conn.close()
            logger.info("Database health check passed")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            logger.error(f"Connection string type: {type(self.connection_string)}")
            return False

