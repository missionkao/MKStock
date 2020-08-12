import requests
import os


class TelegramSender:
    def __init__(self):
        self.url = "https://api.telegram.org"
        self.token = os.environ.get('TELEGRAM_TOKEN')
        self.channel_id = os.environ.get('TELEGRAM_CHANNEL_ID')

    def send_message(self, text):
        api_url = "{}/bot{}/sendMessage?chat_id={}&text={}".format(
            self.url, self.token, self.channel_id, text)
        requests.get(api_url)
