import requests
import json
from enum import Enum

class Constants(Enum):
    API_SESSION = '/session'
    API_ACCOUNTS = '/accounts'
    ORDER_TYPE = "MARKET"
    ORDER_SIZE = "1"
    ORDER_EXPIRY = "DFB"
    USE_GUARANTEED_STOP = True
    CURRENCY = "GBP"
    ORDER_FORCE_OPEN = True
    ORDER_STOP_MULTIPLIER = 3
    MARGIN = 20  # (20% for stocks)
    MARGIN_MAX = 100


class IG:
    def __init__(self, useDemo, data):
        self.username = data['username']
        self.password = data['password']
        self.apiKey = data['apiKey']
        self.accountId = data['accountId']
        self._setup(useDemo)

    def _setup(self, useDemo):
        self.useDemo = useDemo
        self.demoPrefix = ''
        if self.useDemo:
            self.demoPrefix = 'demo-'
        self.apiBaseURI = 'https://' + self.demoPrefix + 'api.ig.com/gateway/deal'
        self.credentials = {"identifier": self.username, "password": self.password}
        self.headers = {'Content-Type': 'application/json; charset=utf-8',
                        'Accept': 'application/json; charset=utf-8',
                        'X-IG-API-KEY': self.apiKey,
                        'Version': '2'
                        }
        self.authenticated_headers = ''

    def authenticate(self):
        # Authenticate with the user credentials
        url_session = self.apiBaseURI + Constants.API_SESSION.value
        response = requests.post(url_session, 
                                data=json.dumps(self.credentials), 
                                headers=self.headers)
        headers_json = dict(response.headers)
        CST_token = headers_json["CST"]
        x_sec_token = headers_json["X-SECURITY-TOKEN"]

        # Build the headers containing auth tokens to use in further api calls
        self.authenticated_headers = {'Content-Type': 'application/json; charset=utf-8',
                                'Accept': 'application/json; charset=utf-8',
                                'X-IG-API-KEY': self.apiKey,
                                'CST': CST_token,
                                'X-SECURITY-TOKEN': x_sec_token}

        # Set the default account to use
        data = {"accountId": self.accountId, "defaultAccount": "True"}  # Main Demo acc
        auth_r = requests.put(url_session,
                                data=json.dumps(data),
                                headers=self.authenticated_headers)
