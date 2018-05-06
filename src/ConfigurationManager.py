import xml.etree.ElementTree as ET

class ConfigurationManager():

    def __init__(self):
        self.configFilePath = "data/config.xml"
        try:
            self.configValues = ET.parse(self.configFilePath).getroot()
            self.alphaVantageApiKey = self.configValues.find("ALPHAVANTAGE_API_KEY").text
            self.alphaVantageBaseURL = self.configValues.find("ALPHAVANTAGE_BASE_URL").text
            self.tradingDatabasePath = self.configValues.find("TRADING_LOG_PATH").text
            self.alphaVantagePollingPeriod = int(self.configValues.find("ALPHAVANTAGE_POLLING_PERIOD").text)
        except Exception:
            pass

    def get_trading_database_path(self):
        return self.tradingDatabasePath

    def get_alpha_vantage_api_key(self):
        return self.alphaVantageApiKey

    def get_alpha_vantage_base_url(self):
        return self.alphaVantageBaseURL

    def get_alpha_vantage_polling_period(self):
        return self.alphaVantagePollingPeriod