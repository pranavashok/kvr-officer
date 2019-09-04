from requests import Session, exceptions
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.packages.urllib3.exceptions import ProtocolError
from bs4 import BeautifulSoup
import re
import json


class Scraper:
    def __init__(self, appointment_type="Researcher"):
        self.session = Session()
        retry = Retry(total=12, connect=4, backoff_factor=0.1)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # Request params
        self.url = "https://www46.muenchen.de/termin/index.php"
        self.querystring = {"cts": "1080627"}
        self.type = appointment_type
        
        if self.type == "BlueCard":
            # Blue card
            self.payload = "step=WEB_APPOINT_SEARCH_BY_CASETYPES&CASETYPES%5BAufenthaltserlaubnis%20Blaue%20Karte%20EU%5D=1"
        else:
            # Guest scientist/research associate
            self.payload = "step=WEB_APPOINT_SEARCH_BY_CASETYPES&CASETYPES%5BAufenthaltserlaubnis%20f%C3%BCr%20Gastwissenschaftler%2C%20wissenschaftliche%20Mitarbeiter%5D=1"
        ## Can possibly add more here
        self.headers = {
            'Connection': "keep-alive",
            'Cache-Control': "max-age=0",
            'Origin': "https://www46.muenchen.de",
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Encoding': "gzip, deflate, br",
            'cookie': "PHPSESSID=balk5ssjisbb6o87dgpnnrtuj6",
            'Host': "www46.muenchen.de",
            'cache-control': "no-cache"
        }

    def get_appointments(self):
        original_response = self.__get_response_from_website()
        return self.__scrape_html(html=original_response)

    def __get_response_from_website(self):
        try:
            # Get session id
            resp = self.session.request("GET", self.url)
            resp.raise_for_status()

            # Get real data
            response = self.session.request(
                "POST", self.url, data=self.payload, headers=self.headers, params=self.querystring)
            response.raise_for_status()
            return response.text
        except exceptions.RequestException as e:
            print(e)
            return ""
        except exceptions.HTTPError as e:
            print(e)
            return ""
        except ProtocolError as e:
            print(e)
            return ""

    def __scrape_html(self, html):
        soup = BeautifulSoup(html, "lxml")
        script_tag = soup.find_all('script')[3].string
        regex = r'var jsonAppoints = (.*?);'
        appointments_text = self.__find_json_object(
            regex=regex, text=script_tag)

        appointments = json.loads(appointments_text)
        if self.type == "BlueCard":
            # Blue card
            return appointments["Termin Wartezone SCIF"]["appoints"]
        else:
            # Wissenschaftler
            return appointments["Termin Wartezone 8"]["appoints"]

    def __find_json_object(self, regex, text):
        match = re.search(regex, text)
        appointments = str(match.groups()[0])
        appointments = appointments[1:len(appointments)-1]
        return appointments
