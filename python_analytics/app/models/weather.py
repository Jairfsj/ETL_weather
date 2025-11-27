from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from flask import jsonify


@dataclass
class WeatherData:
    id: Optional[int]
    city: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_direction: Optional[float]
    weather_main: str
    weather_description: str
    weather_icon: str
    timestamp: int
    timezone: int
    created_at: datetime

    @classmethod
    def from_db_row(cls, row) -> 'WeatherData':
        """Create WeatherData instance from database row"""
        return cls(
            id=row[0],
            city=row[1],
            temperature=row[2],
            feels_like=row[3],
            humidity=row[4],
            pressure=row[5],
            wind_speed=row[6],
            wind_direction=row[7],
            weather_main=row[8],
            weather_description=row[9],
            weather_icon=row[10],
            timestamp=row[11],
            timezone=row[12],
            created_at=row[13]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'city': self.city,
            'temperature': round(self.temperature, 1),
            'feels_like': round(self.feels_like, 1),
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': round(self.wind_speed, 1),
            'wind_direction': self.wind_direction,
            'weather_main': self.weather_main,
            'weather_description': self.weather_description,
            'weather_icon': self.weather_icon,
            'timestamp': self.timestamp,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @property
    def temperature_display(self) -> str:
        """Formatted temperature display"""
        return f"{self.temperature:.1f}°C"

    @property
    def feels_like_display(self) -> str:
        """Formatted feels like temperature display"""
        return f"{self.feels_like:.1f}°C"

    @property
    def wind_speed_display(self) -> str:
        """Formatted wind speed display"""
        return f"{self.wind_speed:.1f} km/h"

    @property
    def weather_icon_url(self) -> str:
        """OpenWeatherMap icon URL"""
        return f"https://openweathermap.org/img/wn/{self.weather_icon}@2x.png"


@dataclass
class WeatherStats:
    total_records: int
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    avg_humidity: float
    avg_wind_speed: float
    most_common_weather: str
    last_updated: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            'total_records': self.total_records,
            'avg_temperature': round(self.avg_temperature, 1),
            'min_temperature': round(self.min_temperature, 1),
            'max_temperature': round(self.max_temperature, 1),
            'avg_humidity': round(self.avg_humidity, 1),
            'avg_wind_speed': round(self.avg_wind_speed, 1),
            'most_common_weather': self.most_common_weather,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class WeatherDataList:
    """Helper class for handling lists of weather data"""

    def __init__(self, weather_data: List[WeatherData]):
        self.data = weather_data

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert list to dictionary list"""
        return [item.to_dict() for item in self.data]

    def get_latest(self) -> Optional[WeatherData]:
        """Get the most recent weather data"""
        return max(self.data, key=lambda x: x.timestamp) if self.data else None

    def get_temperature_trend(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get temperature trend data for charts"""
        # Sort by timestamp
        sorted_data = sorted(self.data, key=lambda x: x.timestamp)

        # Filter last N hours (simplified - in real app you'd use proper time filtering)
        recent_data = sorted_data[-min(len(sorted_data), hours):]

        return [
            {
                'timestamp': item.timestamp,
                'temperature': item.temperature,
                'humidity': item.humidity,
                'created_at': item.created_at.isoformat() if item.created_at else None
            }
            for item in recent_data
        ]

