import json
import os
from typing import List, Optional
import pandas as pd
from requests import request
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AerisWeatherService:
    def __init__(self):
        self.client_id = os.getenv('AERIS_CLIENT_ID')
        self.client_secret = os.getenv('AERIS_CLIENT_SECRET')

        if not self.client_id or not self.client_secret:
            logger.warning("AERIS_CLIENT_ID and/or AERIS_CLIENT_SECRET not set. AerisWeather service will not work.")

        # Default fields for Montreal weather data
        self.default_fields = [
            'place.name',
            'place.country',
            'periods.tempC',  # Temperature in Celsius
            'periods.feelslikeC',  # Feels like temperature in Celsius
            'periods.humidity',  # Humidity percentage
            'periods.windSpeedKPH',  # Wind speed in km/h
            'periods.windDir',  # Wind direction
            'periods.pressureMB',  # Pressure in millibars
            'periods.weather',  # Weather description
            'periods.icon',  # Weather icon
            'periods.timestamp'  # Timestamp
        ]

        # Montreal location
        self.montreal_location = "montreal,ca"

    def aeris_api_dataframe(self, location: str, custom_fields: List[str] = None) -> Optional[pd.DataFrame]:
        """Fetch weather data for a single location from AerisWeather API"""

        if not self.client_id or not self.client_secret:
            logger.error("AerisWeather credentials not configured")
            return None

        formatted_fields = []
        if custom_fields is not None:
            formatted_fields = ','.join(custom_fields)
        else:
            formatted_fields = ','.join(self.default_fields)

        logger.info(f"Retrieving AerisWeather data for {location}...")

        try:
            res = request(
                method="GET",
                url=f"https://api.aerisapi.com/conditions/{location}",
                params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "fields": formatted_fields,
                },
                timeout=30
            )

            if res.status_code != 200:
                logger.error(f"AerisWeather API returned status code {res.status_code}: {res.text}")
                return None

            api_response_body = json.loads(res.text)

            # Check if response has the expected structure
            if 'response' not in api_response_body or not api_response_body['response']:
                logger.warning(f"No data found for location {location}")
                return None

            try:
                # Normalize the main response data (excluding periods)
                df_pre_period = pd.json_normalize(api_response_body['response'][0]).drop("periods", axis=1, errors='ignore')

                # Normalize the periods data
                df_periods = pd.json_normalize(api_response_body['response'][0], "periods", record_prefix="periods.")

                # Join the dataframes
                result_df = df_pre_period.join(df_periods, how="cross")

                logger.info(f"Successfully retrieved data for {location}")
                return result_df

            except (IndexError, KeyError) as e:
                logger.error(f"Error parsing API response for {location}: {e}")
                logger.debug(f"API Response: {api_response_body}")
                return None

        except Exception as e:
            logger.error(f"Error fetching data from AerisWeather API for {location}: {e}")
            return None

    def get_montreal_weather(self, custom_fields: List[str] = None) -> Optional[pd.DataFrame]:
        """Get current weather data for Montreal"""
        return self.aeris_api_dataframe(self.montreal_location, custom_fields)

    def locations_loop(self, locations: List[str], custom_fields: List[str] = None) -> Optional[pd.DataFrame]:
        """Fetch weather data for multiple locations"""
        all_dataframes = []

        for location in locations:
            df = self.aeris_api_dataframe(location, custom_fields)
            if df is not None:
                all_dataframes.append(df)

        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            logger.info(f"Successfully combined data for {len(all_dataframes)} locations")
            return combined_df
        else:
            logger.warning("No data retrieved for any locations")
            return None

    def save_to_csv(self, df: pd.DataFrame, output_dir: str = "csv_output") -> Optional[str]:
        """Save DataFrame to CSV file"""
        try:
            now = datetime.now()
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)

            filename = f"aeris-weather-montreal-{now.strftime('%Y%m%d%H%M%S')}.csv"
            file_path = output_path / filename

            df.to_csv(file_path, encoding="utf-8", index=False)
            logger.info(f"CSV file created: {file_path}")

            return str(file_path)

        except Exception as e:
            logger.error(f"Error saving CSV file: {e}")
            return None

    def get_montreal_weather_summary(self) -> Optional[dict]:
        """Get a summary of Montreal weather data"""
        df = self.get_montreal_weather()

        if df is None or df.empty:
            return None

        try:
            # Extract the latest period data
            latest_data = df.iloc[0] if len(df) > 0 else None

            if latest_data is None:
                return None

            summary = {
                "location": latest_data.get('place.name', 'Montreal'),
                "country": latest_data.get('place.country', 'CA'),
                "temperature_c": latest_data.get('periods.tempC'),
                "feels_like_c": latest_data.get('periods.feelslikeC'),
                "humidity": latest_data.get('periods.humidity'),
                "wind_speed_kph": latest_data.get('periods.windSpeedKPH'),
                "wind_direction": latest_data.get('periods.windDir'),
                "pressure_mb": latest_data.get('periods.pressureMB'),
                "weather": latest_data.get('periods.weather'),
                "icon": latest_data.get('periods.icon'),
                "timestamp": latest_data.get('periods.timestamp'),
                "source": "AerisWeather"
            }

            return summary

        except Exception as e:
            logger.error(f"Error creating weather summary: {e}")
            return None
