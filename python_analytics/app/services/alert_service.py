import logging
import requests
import os
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertService:
    """Service for sending alerts via Telegram"""

    def __init__(self):
        self.telegram_token: Optional[str] = os.getenv('TELEGRAM_TOKEN')
        self.telegram_chat_id: Optional[str] = os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.telegram_token and self.telegram_chat_id)

        if self.enabled:
            logger.info("Telegram alerts enabled")
        else:
            logger.info("Telegram alerts disabled (missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID)")

    def send_alert(self, message: str, level: str = "INFO") -> bool:
        """Send alert message via Telegram"""
        if not self.enabled:
            logger.debug(f"Alert not sent (disabled): {message}")
            return False

        try:
            emoji = {
                "ERROR": "🚨",
                "WARNING": "⚠️",
                "INFO": "ℹ️",
                "SUCCESS": "✅"
            }.get(level.upper(), "📢")

            full_message = f"{emoji} Weather Dashboard Alert\n\n{message}\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": full_message,
                "parse_mode": "HTML"
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"Alert sent successfully: {level}")
                return True
            else:
                logger.error(f"Failed to send alert: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return False

    def send_error_alert(self, error_message: str, context: str = ""):
        """Send error alert"""
        message = f"❌ Error in {context}\n\n{error_message}"
        self.send_alert(message, "ERROR")

    def send_system_alert(self, message: str):
        """Send system status alert"""
        self.send_alert(message, "INFO")

    def send_weather_alert(self, city: str, condition: str, temperature: float):
        """Send weather-related alert"""
        message = f"🌤️ Weather Update for {city}\n\nCurrent condition: {condition}\nTemperature: {temperature:.1f}°C"
        self.send_alert(message, "INFO")

