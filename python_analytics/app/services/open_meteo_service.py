import json
import os
from typing import List, Optional, Dict, Any
import pandas as pd
from requests import request
from pathlib import Path
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

class OpenMeteoService:
    """
    Serviço para integração com Open-Meteo API - Melhor opção para monitoramento semi-real de Montreal

    Características:
    - Gratuita, sem chave API necessária
    - Dados históricos de até 60 anos
    - Dados em tempo real e previsões
    - Coordenadas geográficas precisas para Montreal
    """

    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.historical_url = "https://archive-api.open-meteo.com/v1/archive"

        # Coordenadas precisas de Montreal
        self.montreal_coords = {
            "latitude": 45.5019,
            "longitude": -73.5673
        }

        # Campos padrão para monitoramento semi-real
        self.current_fields = [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "wind_speed_10m",
            "wind_direction_10m",
            "surface_pressure"
        ]

        # Campos históricos (diários agregados)
        self.historical_daily_fields = [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "apparent_temperature_mean",
            "precipitation_sum",
            "relative_humidity_2m_max",
            "relative_humidity_2m_min",
            "relative_humidity_2m_mean",
            "wind_speed_10m_max",
            "wind_speed_10m_mean",
            "surface_pressure_max",
            "surface_pressure_min",
            "surface_pressure_mean"
        ]

        logger.info("Open-Meteo service initialized for Montreal monitoring")

    def get_current_weather(self) -> Optional[Dict[str, Any]]:
        """Busca dados climáticos atuais de Montreal"""

        params = {
            "latitude": self.montreal_coords["latitude"],
            "longitude": self.montreal_coords["longitude"],
            "current_weather": True,
            "timezone": "America/Toronto"
        }

        try:
            response = request("GET", self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "current_weather" in data:
                current = data["current_weather"]

                # Estrutura padronizada compatível com o dashboard
                weather_data = {
                    "location": "Montreal, CA",
                    "temperature": current.get("temperature", 0),
                    "feels_like": current.get("apparent_temperature", current.get("temperature", 0)),
                    "humidity": None,  # Open-Meteo current_weather não inclui umidade
                    "wind_speed": current.get("windspeed", 0),
                    "wind_direction": current.get("winddirection", 0),
                    "pressure": None,  # Não disponível em current_weather
                    "weather_main": "Clear",  # Placeholder
                    "weather_description": "Current conditions",
                    "timestamp": current.get("time", datetime.now().isoformat()),
                    "source": "Open-Meteo",
                    "coordinates": self.montreal_coords
                }

                logger.info(f"Current weather data retrieved from Open-Meteo for Montreal")
                return weather_data
            else:
                logger.warning("No current weather data found in Open-Meteo response")
                return None

        except Exception as e:
            logger.error(f"Error fetching current weather from Open-Meteo: {e}")
            return None

    def get_forecast_weather(self, days: int = 7) -> Optional[List[Dict[str, Any]]]:
        """Busca previsão do tempo para Montreal"""

        params = {
            "latitude": self.montreal_coords["latitude"],
            "longitude": self.montreal_coords["longitude"],
            "daily": ",".join(self.historical_daily_fields[:5]),  # Limitar campos para forecast
            "timezone": "America/Toronto",
            "forecast_days": min(days, 16)  # Máximo 16 dias
        }

        try:
            response = request("GET", self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "daily" in data:
                forecast_data = []
                daily_data = data["daily"]

                for i in range(len(daily_data.get("time", []))):
                    forecast_item = {
                        "date": daily_data["time"][i],
                        "temperature_max": daily_data.get("temperature_2m_max", [0])[i],
                        "temperature_min": daily_data.get("temperature_2m_min", [0])[i],
                        "temperature_mean": daily_data.get("temperature_2m_mean", [0])[i],
                        "feels_like_max": daily_data.get("apparent_temperature_max", [0])[i],
                        "feels_like_min": daily_data.get("apparent_temperature_min", [0])[i],
                        "precipitation": daily_data.get("precipitation_sum", [0])[i],
                        "source": "Open-Meteo"
                    }
                    forecast_data.append(forecast_item)

                logger.info(f"Forecast data retrieved for {len(forecast_data)} days")
                return forecast_data
            else:
                logger.warning("No forecast data found in Open-Meteo response")
                return None

        except Exception as e:
            logger.error(f"Error fetching forecast from Open-Meteo: {e}")
            return None

    def get_historical_weather(self, start_date: date, end_date: date) -> Optional[pd.DataFrame]:
        """Busca dados históricos de Montreal para um período"""

        if start_date >= end_date:
            logger.error("Start date must be before end date")
            return None

        # Limitar a 365 dias para evitar sobrecarga
        date_diff = (end_date - start_date).days
        if date_diff > 365:
            logger.warning(f"Date range too large ({date_diff} days), limiting to 365 days")
            end_date = start_date + timedelta(days=365)

        params = {
            "latitude": self.montreal_coords["latitude"],
            "longitude": self.montreal_coords["longitude"],
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "daily": ",".join(self.historical_daily_fields),
            "timezone": "America/Toronto"
        }

        try:
            response = request("GET", self.historical_url, params=params, timeout=60)
            response.raise_for_status()

            data = response.json()

            if "daily" in data:
                daily_data = data["daily"]

                # Criar DataFrame
                df_data = {
                    "date": pd.to_datetime(daily_data["time"]),
                    "temperature_max": daily_data.get("temperature_2m_max", []),
                    "temperature_min": daily_data.get("temperature_2m_min", []),
                    "temperature_mean": daily_data.get("temperature_2m_mean", []),
                    "feels_like_max": daily_data.get("apparent_temperature_max", []),
                    "feels_like_min": daily_data.get("apparent_temperature_min", []),
                    "feels_like_mean": daily_data.get("apparent_temperature_mean", []),
                    "humidity_max": daily_data.get("relative_humidity_2m_max", []),
                    "humidity_min": daily_data.get("relative_humidity_2m_min", []),
                    "humidity_mean": daily_data.get("relative_humidity_2m_mean", []),
                    "precipitation": daily_data.get("precipitation_sum", []),
                    "wind_speed_max": daily_data.get("wind_speed_10m_max", []),
                    "wind_speed_mean": daily_data.get("wind_speed_10m_mean", []),
                    "pressure_max": daily_data.get("surface_pressure_max", []),
                    "pressure_min": daily_data.get("surface_pressure_min", []),
                    "pressure_mean": daily_data.get("surface_pressure_mean", []),
                    "source": "Open-Meteo"
                }

                df = pd.DataFrame(df_data)
                df["location"] = "Montreal, CA"
                df["coordinates"] = str(self.montreal_coords)

                logger.info(f"Historical data retrieved: {len(df)} days from {start_date} to {end_date}")
                return df
            else:
                logger.warning("No historical data found in Open-Meteo response")
                return None

        except Exception as e:
            logger.error(f"Error fetching historical data from Open-Meteo: {e}")
            return None

    def get_weekly_monitoring_data(self, weeks_back: int = 4) -> Optional[pd.DataFrame]:
        """Busca dados semanais para monitoramento (3-4 vezes por semana)"""

        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks_back)

        df = self.get_historical_weather(start_date, end_date)

        if df is not None:
            # Filtrar para dados 3-4 vezes por semana (ex: segunda, quarta, sexta)
            df['weekday'] = df['date'].dt.weekday
            # 0=Segunda, 2=Quarta, 4=Sexta (3 dias por semana)
            monitoring_days = df[df['weekday'].isin([0, 2, 4])].copy()

            logger.info(f"Weekly monitoring data: {len(monitoring_days)} records for {weeks_back} weeks")
            return monitoring_days

        return None

    def save_to_csv(self, df: pd.DataFrame, filename: str = None, output_dir: str = "csv_output") -> Optional[str]:
        """Salva DataFrame em CSV"""

        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)

            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"open_meteo_montreal_{timestamp}.csv"

            file_path = output_path / filename
            df.to_csv(file_path, index=False, encoding="utf-8")

            logger.info(f"Open-Meteo data saved to CSV: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Error saving Open-Meteo CSV: {e}")
            return None

    def get_monitoring_summary(self, weeks_back: int = 4) -> Optional[Dict[str, Any]]:
        """Retorna resumo estatístico para monitoramento"""

        df = self.get_weekly_monitoring_data(weeks_back)

        if df is None or df.empty:
            return None

        try:
            summary = {
                "period_weeks": weeks_back,
                "total_records": len(df),
                "date_range": {
                    "start": df['date'].min().strftime("%Y-%m-%d"),
                    "end": df['date'].max().strftime("%Y-%m-%d")
                },
                "temperature": {
                    "max": df['temperature_max'].max(),
                    "min": df['temperature_min'].min(),
                    "mean": df['temperature_mean'].mean(),
                    "std": df['temperature_mean'].std()
                },
                "humidity": {
                    "max": df['humidity_max'].max(),
                    "min": df['humidity_min'].min(),
                    "mean": df['humidity_mean'].mean()
                },
                "precipitation": {
                    "total": df['precipitation'].sum(),
                    "days_with_rain": (df['precipitation'] > 0).sum(),
                    "mean_daily": df['precipitation'].mean()
                },
                "wind": {
                    "max_speed": df['wind_speed_max'].max(),
                    "mean_speed": df['wind_speed_mean'].mean()
                },
                "source": "Open-Meteo",
                "location": "Montreal, CA"
            }

            logger.info(f"Monitoring summary generated for {weeks_back} weeks")
            return summary

        except Exception as e:
            logger.error(f"Error generating monitoring summary: {e}")
            return None
