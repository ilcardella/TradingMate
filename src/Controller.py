from .Model import Model
from .View import View


class Controller():

    def __init__(self):
        # Init the model
        self.model = Model(self.update_live_prices)
        # Init the view
        self.view = View(self.on_close_view_event)

    def start(self):
        self.model.start()
        for logEntry in self.model.get_log_as_list():
            self.view.add_entry_to_log(logEntry.get_date(),
                                        logEntry.get_action(), 
                                        logEntry.get_symbol(),
                                        logEntry.get_amount(),
                                        logEntry.get_price(),
                                        logEntry.get_fee())

        self.view.start() # This should be the last instruction in this function

    def on_close_view_event(self):
        self.model.stop_application()
        self.stop_application()

    def stop_application(self):
        print("TODO Controller stop_application")

    def update_live_prices(self, pricesDict):
        self.view.update_live_prices(pricesDict)
