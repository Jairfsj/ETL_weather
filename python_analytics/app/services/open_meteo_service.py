"""
Open-Meteo Service - Monitoramento climático Montreal (2025-2026)

Serviço simplificado para coleta de dados climáticos históricos
usando a API Open-Meteo (gratuita, sem limites).
"""

from typing import Optional
import pandas as pd
from requests import request
from pathlib import Path
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

class OpenMeteoService:
    """Serviço Open-Meteo para Montreal"""

    MONTREAL_COORDS = {"latitude": 45.5019, "longitude": -73.5673}
    HISTORICAL_FIELDS = [
        "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
        "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean",
        "precipitation_sum", "relative_humidity_2m_max", "relative_humidity_2m_min",
        "relative_humidity_2m_mean", "wind_speed_10m_max", "wind_speed_10m_mean"
    ]

    def __init__(self):
        self.historical_url = "https://archive-api.open-meteo.com/v1/archive"

    def get_historical_weather(self, start_date: date, end_date: date) -> Optional[pd.DataFrame]:
        """Busca dados históricos de Montreal"""
        if start_date >= end_date:
            return None

        # Limitar a 365 dias para evitar sobrecarga
        if (end_date - start_date).days > 365:
            end_date = start_date + timedelta(days=365)

        params = {
            "latitude": self.MONTREAL_COORDS["latitude"],
            "longitude": self.MONTREAL_COORDS["longitude"],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": ",".join(self.HISTORICAL_FIELDS),
            "timezone": "America/Toronto"
        }

        try:
            response = request("GET", self.historical_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "daily" in data:
                daily_data = data["daily"]
                df_data = {
                    "date": pd.to_datetime(daily_data["time"]),
                    "temperature_max": daily_data.get("temperature_2m_max", []),
                    "temperature_min": daily_data.get("temperature_2m_min", []),
                    "temperature_mean": daily_data.get("temperature_2m_mean", []),
                    "feels_like_max": daily_data.get("apparent_temperature_max", []),
                    "feels_like_min": daily_data.get("apparent_temperature_min", []),
                    "feels_like_mean": daily_data.get("apparent_temperature_mean", []),
                    "precipitation": daily_data.get("precipitation_sum", []),
                    "humidity_max": daily_data.get("relative_humidity_2m_max", []),
                    "humidity_min": daily_data.get("relative_humidity_2m_min", []),
                    "humidity_mean": daily_data.get("relative_humidity_2m_mean", []),
                    "wind_speed_max": daily_data.get("wind_speed_10m_max", []),
                    "wind_speed_mean": daily_data.get("wind_speed_10m_mean", [])
                }

                df = pd.DataFrame(df_data)
                logger.info(f"Historical data: {len(df)} records")
                return df

        except Exception as e:
            logger.error(f"Error: {e}")

        return None

    def get_weekly_monitoring_data(self, weeks_back: int = 4) -> Optional[pd.DataFrame]:
        """Busca dados semanais (3x por semana)"""
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks_back)

        df = self.get_historical_weather(start_date, end_date)

        if df is not None:
            df['weekday'] = df['date'].dt.weekday
            monitoring_days = df[df['weekday'].isin([0, 2, 4])].copy()
            logger.info(f"Monitoring data: {len(monitoring_days)} records")
            return monitoring_days

        return None

    def save_to_csv(self, df: pd.DataFrame, filename: str, output_dir: str = "data") -> Optional[str]:
        """Salva DataFrame como CSV"""
        try:
            Path(output_dir).mkdir(exist_ok=True)
            filepath = Path(output_dir) / filename
            df.to_csv(filepath, index=False)
            logger.info(f"Saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Save error: {e}")
            return None
