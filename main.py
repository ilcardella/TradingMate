# Imports
from src.Controller import Controller

class TradingMate():
    
    def __init__(self):
        self.controller = Controller()

    def start(self):
        self.controller.start()
        
# MAIN
if __name__ == "__main__":
    app = TradingMate()
    app.start()

