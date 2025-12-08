"""
WeatherAPI Service - Dados climáticos em tempo real gratuitos

API gratuita com 1M chamadas/mês, atualizações a cada 15 minutos
Monitoramento de Montreal de 07/12/2025 até 01/01/2027

Documentação: https://www.weatherapi.com/docs/
"""

from typing import Optional, Dict, Any
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherAPIService:
    """Serviço WeatherAPI para dados climáticos em tempo real"""

    BASE_URL = "http://api.weatherapi.com/v1"
    MONTREAL_LOCATION = "Montreal,Canada"

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializar WeatherAPI Service

        Args:
            api_key: Chave da API (opcional para desenvolvimento)
        """
        self.api_key = api_key or "demo"  # Usar demo se não houver chave
        self.session = requests.Session()
        self.session.timeout = 30

        logger.info("WeatherAPI Service initialized for Montreal real-time monitoring")

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fazer requisição para WeatherAPI"""
        try:
            params["key"] = self.api_key
            params["q"] = self.MONTREAL_LOCATION

            url = f"{self.BASE_URL}/{endpoint}"
            response = self.session.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"WeatherAPI request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"WeatherAPI error: {e}")
            return None

    def get_current_weather(self) -> Optional[Dict[str, Any]]:
        """Obter dados climáticos atuais de Montreal"""
        data = self._make_request("current.json", {})

        if not data:
            return None

        try:
            current = data.get("current", {})
            location = data.get("location", {})

            # Estrutura padronizada para o dashboard
            weather_data = {
                "location": "Montreal, CA",
                "temperature": current.get("temp_c", 0),
                "feels_like": current.get("feelslike_c", current.get("temp_c", 0)),
                "humidity": current.get("humidity", 0),
                "wind_speed": current.get("wind_kph", 0),
                "wind_direction": current.get("wind_dir", ""),
                "pressure": current.get("pressure_mb", 0),
                "weather_main": current.get("condition", {}).get("text", "Unknown"),
                "weather_description": current.get("condition", {}).get("text", "Current conditions"),
                "visibility": current.get("vis_km", 0),
                "uv_index": current.get("uv", 0),
                "cloud_cover": current.get("cloud", 0),
                "timestamp": current.get("last_updated", datetime.now().isoformat()),
                "source": "WeatherAPI",
                "coordinates": {
                    "lat": location.get("lat"),
                    "lon": location.get("lon")
                },
                "raw_data": data
            }

            logger.info(f"Current weather data retrieved from WeatherAPI for Montreal")
            return weather_data

        except Exception as e:
            logger.error(f"Error parsing current weather data: {e}")
            return None

    def get_forecast_weather(self, days: int = 7) -> Optional[list]:
        """Obter previsão do tempo para Montreal"""
        data = self._make_request("forecast.json", {"days": min(days, 10), "aqi": "no", "alerts": "no"})

        if not data:
            return None

        try:
            forecast_days = data.get("forecast", {}).get("forecastday", [])
            forecast_data = []

            for day_data in forecast_days:
                day_info = day_data.get("day", {})
                astro = day_data.get("astro", {})

                forecast_item = {
                    "date": day_data.get("date"),
                    "temperature_max": day_info.get("maxtemp_c", 0),
                    "temperature_min": day_info.get("mintemp_c", 0),
                    "temperature_mean": (day_info.get("maxtemp_c", 0) + day_info.get("mintemp_c", 0)) / 2,
                    "feels_like_max": day_info.get("maxtemp_c", 0),  # Aproximação
                    "feels_like_min": day_info.get("mintemp_c", 0),
                    "precipitation": day_info.get("totalprecip_mm", 0),
                    "humidity": day_info.get("avghumidity", 0),
                    "wind_speed_max": day_info.get("maxwind_kph", 0),
                    "wind_speed_mean": day_info.get("maxwind_kph", 0),
                    "weather_main": day_info.get("condition", {}).get("text", "Unknown"),
                    "weather_description": day_info.get("condition", {}).get("text", "Forecast conditions"),
                    "sunrise": astro.get("sunrise"),
                    "sunset": astro.get("sunset"),
                    "source": "WeatherAPI"
                }

                forecast_data.append(forecast_item)

            logger.info(f"Forecast data retrieved for {len(forecast_data)} days")
            return forecast_data

        except Exception as e:
            logger.error(f"Error parsing forecast data: {e}")
            return None

    def get_hourly_forecast(self, hours: int = 24) -> Optional[list]:
        """Obter previsão horária detalhada"""
        data = self._make_request("forecast.json", {"days": 2, "aqi": "no", "alerts": "no"})

        if not data:
            return None

        try:
            hourly_data = []
            forecast_days = data.get("forecast", {}).get("forecastday", [])

            for day_data in forecast_days:
                for hour_data in day_data.get("hour", []):
                    if len(hourly_data) >= hours:
                        break

                    hourly_item = {
                        "timestamp": hour_data.get("time"),
                        "temperature": hour_data.get("temp_c", 0),
                        "feels_like": hour_data.get("feelslike_c", 0),
                        "humidity": hour_data.get("humidity", 0),
                        "precipitation": hour_data.get("precip_mm", 0),
                        "wind_speed": hour_data.get("wind_kph", 0),
                        "wind_direction": hour_data.get("wind_dir", ""),
                        "pressure": hour_data.get("pressure_mb", 0),
                        "cloud_cover": hour_data.get("cloud", 0),
                        "weather_main": hour_data.get("condition", {}).get("text", "Unknown"),
                        "source": "WeatherAPI"
                    }

                    hourly_data.append(hourly_item)

                if len(hourly_data) >= hours:
                    break

            logger.info(f"Hourly forecast data retrieved: {len(hourly_data)} hours")
            return hourly_data[:hours]

        except Exception as e:
            logger.error(f"Error parsing hourly forecast data: {e}")
            return None

    def get_weather_alerts(self) -> Optional[list]:
        """Obter alertas meteorológicos atuais"""
        data = self._make_request("forecast.json", {"days": 1, "alerts": "yes"})

        if not data:
            return None

        try:
            alerts = data.get("alerts", {}).get("alert", [])

            if alerts:
                alert_list = []
                for alert in alerts:
                    alert_item = {
                        "headline": alert.get("headline", ""),
                        "msgtype": alert.get("msgtype", ""),
                        "severity": alert.get("severity", ""),
                        "urgency": alert.get("urgency", ""),
                        "areas": alert.get("areas", ""),
                        "category": alert.get("category", ""),
                        "certainty": alert.get("certainty", ""),
                        "event": alert.get("event", ""),
                        "note": alert.get("note", ""),
                        "effective": alert.get("effective", ""),
                        "expires": alert.get("expires", ""),
                        "desc": alert.get("desc", ""),
                        "instruction": alert.get("instruction", "")
                    }
                    alert_list.append(alert_item)

                logger.info(f"Weather alerts retrieved: {len(alert_list)} alerts")
                return alert_list
            else:
                return []  # No alerts

        except Exception as e:
            logger.error(f"Error parsing weather alerts: {e}")
            return None

    def get_realtime_monitoring_data(self) -> Optional[Dict[str, Any]]:
        """Obter dados completos para monitoramento em tempo real"""
        try:
            current = self.get_current_weather()
            forecast = self.get_forecast_weather(3)  # 3 dias de forecast
            alerts = self.get_weather_alerts()

            if not current:
                return None

            monitoring_data = {
                "timestamp": datetime.now().isoformat(),
                "location": "Montreal, Canada",
                "current": current,
                "forecast_3day": forecast or [],
                "alerts": alerts or [],
                "source": "WeatherAPI",
                "monitoring_period": {
                    "start": "2025-12-07",
                    "end": "2027-01-01",
                    "duration_days": 391
                }
            }

            logger.info("Real-time monitoring data retrieved successfully")
            return monitoring_data

        except Exception as e:
            logger.error(f"Error getting real-time monitoring data: {e}")
            return None

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Status do serviço de monitoramento"""
        return {
            "service": "WeatherAPI",
            "status": "active",
            "location": "Montreal, Canada",
            "monitoring_period": "2025-12-07 to 2027-01-01",
            "update_frequency": "15 minutes",
            "free_tier_limit": "1,000,000 calls/month",
            "features": [
                "Current weather",
                "3-day forecast",
                "Hourly data",
                "Weather alerts",
                "Real-time updates"
            ],
            "coordinates": {"lat": 45.5019, "lon": -73.5673},
            "timezone": "America/Toronto"
        }
