import requests
import json
from enum import Enum
from .Utils import AutoTradeActions

class IG_Constants(Enum):
    API_SESSION = '/session'
    API_ACCOUNTS = '/accounts'
    API_POSITIONS = '/positions'
    API_PRICES = '/prices'
    API_MARKETS = '/markets'
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
        url = self.apiBaseURI + IG_Constants.API_SESSION.value
        response = requests.post(url, 
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
        auth_r = requests.put(url,
                            data=json.dumps(data),
                            headers=self.authenticated_headers)

        # Fetch account balances
        url = self.apiBaseURI + IG_Constants.API_ACCOUNTS.value
        d = self.http_get(url)
        for i in d['accounts']:
            if str(i['accountType']) == "SPREADBET":
                self.accountBalance = i['balance']['balance']
                self.accountDeposit = i['balance']['deposit']

    def can_trade(self):
        # Trade only if available balance is less than 60% of total account
        percentage = 100 * float(self.accountDeposit) / float(self.accountBalance)
        return percentage < 60

    def get_open_positions(self):
        positionMap = {}
        position_base_url = self.apiBaseURI + IG_Constants.API_POSITIONS.value
        position_json = self.http_get(position_base_url)
        for item in position_json['positions']:
            direction = item['position']['direction']
            dealSize = item['position']['dealSize']
            ccypair = item['market']['epic']
            key = ccypair + '-' + direction
            if(key in positionMap):
                positionMap[key] = dealSize + positionMap[key]
            else:
                positionMap[key] = dealSize
        return positionMap

    def get_market_prices(self, epic):
        base_url = self.apiBaseURI + IG_Constants.API_MARKETS.value + '/' + epic
        d = self.http_get(base_url)
        return d['snapshot']#['bid']

    def get_price_history(self, epic, timeRange):
        # Price resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5,
        # MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3,
        # HOUR_4, DAY, WEEK, MONTH)
        base_url = self.apiBaseURI + IG_Constants.API_PRICES.value + '/' + epic + "/DAY/" + str(timeRange)
        d = self.http_get(base_url)
        remaining_allowance = d['allowance']['remainingAllowance']
        reset_time = self.humanize_time(int(d['allowance']['allowanceExpiry']))
        print("-----------------DEBUG-----------------")
        print("#################DEBUG#################")
        print("Remaining API Calls left: " + str(remaining_allowance))
        print("Time to API Key reset: " + str(reset_time))
        print("-----------------DEBUG-----------------")
        print("#################DEBUG#################")
        return d['prices']

    def trade(self, marketAction):
        # TODO perform a trade win the marketAction direction
        if marketAction == AutoTradeActions.BUY:
            print("IG_Interface>trade(): " + marketAction.value)
        elif marketAction == AutoTradeActions.SELL:
            print("IG_Interface>trade(): " + marketAction.value)
        elif marketAction == AutoTradeActions.EXIT_BUY:
            print("IG_Interface>trade(): " + marketAction.value)
        elif marketAction == AutoTradeActions.EXIT_SELL:
            print("IG_Interface>trade(): " + marketAction.value)
        elif marketAction == AutoTradeActions.NONE:
            return
    
    def http_get(self, url):
        auth_r = requests.get(url, headers=self.authenticated_headers)
        return json.loads(auth_r.text)

    def humanize_time(self, secs):
        mins, secs = divmod(secs, 60)
        hours, mins = divmod(mins, 60)
        return '%02d:%02d:%02d' % (hours, mins, secs)

    