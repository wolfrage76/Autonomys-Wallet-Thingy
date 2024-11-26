import requests
import logging

class NotificationManager:
    def __init__(self, discord_webhook=None, pushbullet_token=None, pushover_config=None, telegram_config=None):
        self.discord_webhook = discord_webhook
        self.pushbullet_token = pushbullet_token
        self.pushover_config = pushover_config  # Dictionary: {'user_key': '...', 'api_token': '...'}
        self.telegram_config = telegram_config  # Dictionary: {'bot_token': '...', 'chat_id': '...'}
        print('Balance Checker Initialized')

    def send_notification(self, message):
        if self.discord_webhook:
            self._send_discord_notification(message)
        if self.pushbullet_token:
            self._send_pushbullet_notification(message)
        if self.pushover_config:
            self._send_pushover_notification(message)
        if self.telegram_config:
            self._send_telegram_notification(message)

    def _send_discord_notification(self, message):
        try:
            payload = {"content": message}
            response = requests.post(self.discord_webhook, json=payload)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Error sending Discord notification: {e}")

    def _send_pushbullet_notification(self, message):
        try:
            headers = {
                'Access-Token': self.pushbullet_token,
                'Content-Type': 'application/json'
            }
            payload = {"type": "note", "title": "Balance Alert", "body": message}
            response = requests.post("https://api.pushbullet.com/v2/pushes", json=payload, headers=headers)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Error sending Pushbullet notification: {e}")

    def _send_pushover_notification(self, message):
        try:
            payload = {
                'user': self.pushover_config['user_key'],
                'token': self.pushover_config['api_token'],
                'message': message
            }
            response = requests.post("https://api.pushover.net/1/messages.json", data=payload)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Error sending Pushover notification: {e}")

    def _send_telegram_notification(self, message):
        try:
            bot_token = self.telegram_config['bot_token']
            chat_id = self.telegram_config['chat_id']
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {'chat_id': chat_id, 'text': message}
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Error sending Telegram notification: {e}")
