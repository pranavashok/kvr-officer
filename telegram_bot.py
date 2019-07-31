from requests import Session, exceptions
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from os.path import join, dirname
from dotenv import load_dotenv
import os

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


class TelegramBot:
    def __init__(self):
        self.session = Session()
        retry = Retry(total=12, connect=8, backoff_factor=0.1)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.telegram_token = os.environ['TELEGRAM_TOKEN']
        self.chat_id = os.environ['CHAT_ID']

    def send_message(self, text):
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text
        }

        self.session.request("POST", url, data=payload)
