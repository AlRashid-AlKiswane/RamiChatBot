import requests
import smtplib
import os, sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(root_dir)

from src.config.setting import get_settings, Settings

class AlertManager:
    def __init__(self):
        # Get settings from the environment
        self.app_settings: Settings = get_settings()
        
        # Access Telegram bot settings from app_settings
        self.telegram_bot_token = self.app_settings.TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = self.app_settings.TELEGRAM_CHAT_ID
    
    def send_telegram_alert(self, subject, message):
        """Sends a Telegram message when an error occurs."""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        data = {
            "chat_id": self.telegram_chat_id,
            "text": f"Subject: {subject}\n\nMessage: {message}"
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            print(f"Alert sent to Telegram: {subject}")
        except Exception as e:
            print(f"Failed to send alert to Telegram: {e}")

# Example usage
if __name__ == "__main__":

    alert = AlertManager()
    alert.send_telegram_alert("Test Alert", "This is a test alert from the monitoring system.")