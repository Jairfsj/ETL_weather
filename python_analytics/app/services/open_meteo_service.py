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
        """Busca dados semanais para monitoramento (3 vezes por semana)"""
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks_back)

        df = self.get_historical_weather(start_date, end_date)

        if df is not None:
            # Filtrar para 3 dias por semana (segunda, quarta, sexta)
            df['weekday'] = df['date'].dt.weekday
            monitoring_days = df[df['weekday'].isin([0, 2, 4])].copy()

            logger.info(f"Weekly monitoring data: {len(monitoring_days)} records")
            return monitoring_days

        return None

    def get_long_term_monitoring_data(self, years: int = 2) -> Optional[pd.DataFrame]:
        """Busca dados de monitoramento de longo prazo (até 2026)"""

        end_date = date.today()
        start_date = end_date - timedelta(days=365 * years)

        logger.info(f"Fetching long-term monitoring data from {start_date} to {end_date}")

        df = self.get_historical_weather(start_date, end_date)

        if df is not None:
            # Filtrar para dados de monitoramento (3 vezes por semana)
            df['weekday'] = df['date'].dt.weekday
            monitoring_days = df[df['weekday'].isin([0, 2, 4])].copy()  # Mon, Wed, Fri

            # Adicionar colunas de análise
            monitoring_days['year'] = monitoring_days['date'].dt.year
            monitoring_days['month'] = monitoring_days['date'].dt.month
            monitoring_days['season'] = monitoring_days['date'].dt.month.map({
                12: 'Winter', 1: 'Winter', 2: 'Winter',
                3: 'Spring', 4: 'Spring', 5: 'Spring',
                6: 'Summer', 7: 'Summer', 8: 'Summer',
                9: 'Fall', 10: 'Fall', 11: 'Fall'
            })

            logger.info(f"Long-term monitoring data: {len(monitoring_days)} records for {years} years")
            return monitoring_days

        return None

    def get_seasonal_analysis(self, years: int = 2) -> Optional[Dict[str, pd.DataFrame]]:
        """Análise sazonal dos dados climáticos"""

        df = self.get_long_term_monitoring_data(years)

        if df is None or df.empty:
            return None

        seasonal_data = {}

        seasons = ['Winter', 'Spring', 'Summer', 'Fall']

        for season in seasons:
            season_df = df[df['season'] == season].copy()

            if not season_df.empty:
                seasonal_data[season] = {
                    'data': season_df,
                    'summary': {
                        'temperature_avg': season_df['temperature_mean'].mean(),
                        'temperature_max': season_df['temperature_max'].max(),
                        'temperature_min': season_df['temperature_min'].min(),
                        'humidity_avg': season_df['humidity_mean'].mean(),
                        'precipitation_total': season_df['precipitation'].sum(),
                        'precipitation_avg': season_df['precipitation'].mean(),
                        'wind_avg': season_df['wind_speed_mean'].mean(),
                        'record_count': len(season_df)
                    }
                }

        logger.info(f"Seasonal analysis completed for {years} years")
        return seasonal_data

    def get_yearly_trends(self, years: int = 2) -> Optional[Dict[str, pd.DataFrame]]:
        """Análise de tendências anuais"""

        df = self.get_long_term_monitoring_data(years)

        if df is None or df.empty:
            return None

        yearly_data = {}

        for year in df['year'].unique():
            year_df = df[df['year'] == year].copy()

            if not year_df.empty:
                yearly_data[str(year)] = {
                    'data': year_df,
                    'monthly_avg': year_df.groupby('month')['temperature_mean'].mean(),
                    'summary': {
                        'avg_temperature': year_df['temperature_mean'].mean(),
                        'max_temperature': year_df['temperature_max'].max(),
                        'min_temperature': year_df['temperature_min'].min(),
                        'total_precipitation': year_df['precipitation'].sum(),
                        'avg_humidity': year_df['humidity_mean'].mean(),
                        'record_count': len(year_df)
                    }
                }

        logger.info(f"Yearly trends analysis completed for {years} years")
        return yearly_data

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
