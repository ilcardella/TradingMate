import os
import sys
import inspect
import tkinter as tk
from tkinter import ttk
import datetime

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Actions, Markets
from Utils.Trade import Trade
from .WarningWindow import WarningWindow
from .Widgets import DatePicker


class AddTradeDialogWindow(tk.Toplevel):
    def __init__(self, master, confirmCallback):
        tk.Toplevel.__init__(self)
        self.master = master
        self.confirmCallback = confirmCallback
        self.transient(self.master)
        self.title("Add Trade")
        self.geometry(
            "+{}+{}".format(
                self.master.winfo_rootx() + 400, self.master.winfo_rooty() + 100
            )
        )
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()
        self.focus_set()

        self.create_UI()

    def create_UI(self):
        # Define the labels on the left hand column
        ttk.Label(self, text="Date:").grid(row=0, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Action:").grid(row=1, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Market:").grid(row=2, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Symbol:").grid(row=3, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Quantity:").grid(row=4, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Price [p] :").grid(row=5, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Fee [£] :").grid(row=6, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Stamp Duty [%] :").grid(row=7, sticky="w", padx=5, pady=5)
        ttk.Label(self, text="Notes:").grid(row=8, sticky="w", padx=5, pady=5)

        # Define the date entry widget
        self.dateSelected = tk.StringVar()
        self.dateSelected.trace_add("write", self.check_data_validity)
        datePicker = DatePicker(self, self.dateSelected)
        datePicker.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        datePicker.focus_set()

        # Define an option menu for the action
        self.actionSelected = tk.StringVar()
        menuList = [a.name for a in Actions]
        eAction = ttk.OptionMenu(
            self,
            self.actionSelected,
            menuList[0],
            *menuList,
            command=self.on_action_selected
        )
        eAction.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Define an option menu for the market exchange
        self.marketSelected = tk.StringVar()
        marketList = [a.name for a in Markets]
        self.eMarket = ttk.OptionMenu(
            self,
            self.marketSelected,
            marketList[0],
            *marketList,
            command=self.on_market_selected
        )
        self.eMarket.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        self.symbolSelected = tk.StringVar()
        self.symbolSelected.trace_add("write", self.check_data_validity)
        self.eSymbol = ttk.Entry(self, textvariable=self.symbolSelected)
        self.eSymbol.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        self.quantity_selected = tk.StringVar()
        self.quantity_selected.trace_add("write", self.check_data_validity)
        self.e_quantity = ttk.Entry(self, textvariable=self.quantity_selected)
        self.e_quantity.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        self.priceSelected = tk.StringVar()
        self.priceSelected.trace_add("write", self.check_data_validity)
        self.ePrice = ttk.Entry(self, textvariable=self.priceSelected)
        self.ePrice.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        self.feeSelected = tk.StringVar()
        self.feeSelected.trace_add("write", self.check_data_validity)
        self.eFee = ttk.Entry(self, textvariable=self.feeSelected)
        self.eFee.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        self.stampDutySelected = tk.StringVar()
        self.stampDutySelected.trace_add("write", self.check_data_validity)
        self.eStampDuty = ttk.Entry(self, textvariable=self.stampDutySelected)
        self.eStampDuty.grid(row=7, column=1, sticky="w", padx=5, pady=5)

        self.notesSelected = tk.StringVar()
        self.notesSelected.trace_add("write", self.check_data_validity)
        self.eNotes = ttk.Entry(self, textvariable=self.notesSelected)
        self.eNotes.grid(row=8, column=1, sticky="w", padx=5, pady=5)

        cancelButton = ttk.Button(self, text="Cancel", command=self.destroy)
        cancelButton.grid(row=9, column=0, sticky="e", padx=5, pady=5)
        self.addButton = ttk.Button(self, text="Add", command=self.add_new_trade)
        self.addButton.grid(row=9, column=1, sticky="e", padx=5, pady=5)
        self.addButton.config(state="disabled")

        # Make the mas ter thread block execution until this window is closed
        self.master.wait_window(self)

    def on_market_selected(self, selection):
        pass

    def on_action_selected(self, selection):
        # Clear data entry
        self.symbolSelected.set("")
        self.quantity_selected.set("")
        self.priceSelected.set("")
        self.feeSelected.set("")
        self.stampDutySelected.set("")
        self.notesSelected.set("")
        # Change layout
        if selection == Actions.BUY.name:
            self.eMarket.config(state="enabled")
            self.eSymbol.config(state="enabled")
            self.e_quantity.config(state="enabled")
            self.ePrice.config(state="enabled")
            self.eFee.config(state="enabled")
            self.eStampDuty.config(state="enabled")
            self.eNotes.config(state="enabled")
        elif selection == Actions.SELL.name:
            self.eMarket.config(state="enabled")
            self.eSymbol.config(state="enabled")
            self.e_quantity.config(state="enabled")
            self.ePrice.config(state="enabled")
            self.eFee.config(state="enabled")
            self.eStampDuty.config(state="disabled")
            self.eNotes.config(state="enabled")
        elif selection == Actions.DEPOSIT.name:
            self.eMarket.config(state="disabled")
            self.eSymbol.config(state="disabled")
            self.e_quantity.config(state="enabled")
            self.ePrice.config(state="disabled")
            self.eFee.config(state="disabled")
            self.eStampDuty.config(state="disabled")
            self.eNotes.config(state="enabled")
        elif selection == Actions.DIVIDEND.name:
            self.eMarket.config(state="enabled")
            self.eSymbol.config(state="enabled")
            self.e_quantity.config(state="enabled")
            self.ePrice.config(state="disabled")
            self.eFee.config(state="disabled")
            self.eStampDuty.config(state="disabled")
            self.eNotes.config(state="enabled")
        elif selection == Actions.WITHDRAW.name:
            self.eMarket.config(state="disabled")
            self.eSymbol.config(state="disabled")
            self.e_quantity.config(state="enabled")
            self.ePrice.config(state="disabled")
            self.eFee.config(state="disabled")
            self.eStampDuty.config(state="disabled")
            self.eNotes.config(state="enabled")
        elif selection == Actions.FEE.name:
            self.eMarket.config(state="disabled")
            self.eSymbol.config(state="disabled")
            self.e_quantity.config(state="enabled")
            self.ePrice.config(state="disabled")
            self.eFee.config(state="disabled")
            self.eStampDuty.config(state="disabled")
            self.eNotes.config(state="enabled")

    def add_new_trade(self):
        # Get selected data and call callback
        item = {}
        item["date"] = self.dateSelected.get()
        item["action"] = self.actionSelected.get()
        market = Markets[self.marketSelected.get()]
        item["symbol"] = (
            (market.name + ":" + self.symbolSelected.get())
            if self.symbolSelected.get() is not ""
            else ""
        )
        item["quantity"] = (
            float(self.quantity_selected.get())
            if self.quantity_selected.get() is not ""
            else 0
        )
        item["price"] = (
            float(self.priceSelected.get()) if self.priceSelected.get() is not "" else 0
        )
        item["fee"] = (
            float(self.feeSelected.get()) if self.feeSelected.get() is not "" else 0
        )
        item["stamp_duty"] = (
            float(self.stampDutySelected.get())
            if self.stampDutySelected.get() is not ""
            else 0
        )
        item["notes"] = str(self.notesSelected.get())
        newTrade = Trade.from_dict(item)
        result = self.confirmCallback(newTrade)

        if result["success"]:
            self.destroy()
        else:
            WarningWindow(self, "Warning", result["message"])

    def check_data_validity(self, *args):
        # Check the validity of the Entry widgets data to enable the Add button
        valid = (
            self.is_date_valid()
            and self.is_symbol_valid()
            and self.is_quantity_valid()
            and self.is_price_valid()
            and self.is_fee_valid()
            and self.is_sd_valid()
            and self.is_notes_valid()
        )
        self.addButton.config(state="normal" if valid else "disabled")

    def is_date_valid(self):
        value = self.dateSelected.get()
        try:
            datetime.datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            return False
        return True

    def is_symbol_valid(self):
        # If widget is disabled it should not affect the overall validity
        if str(self.eSymbol.cget("state")) == tk.DISABLED:
            return True
        if len(self.symbolSelected.get()) < 1:
            return False
        # Force uppercase
        self.symbolSelected.set(self.symbolSelected.get().upper())
        return True

    def is_quantity_valid(self):
        # If widget is disabled it should not affect the overall validity
        if str(self.e_quantity.cget("state")) == tk.DISABLED:
            return True
        try:
            value = float(self.quantity_selected.get())
            if value > 0:
                return True
            return False
        except Exception:
            return False

    def is_price_valid(self):
        # If widget is disabled it should not affect the overall validity
        if str(self.ePrice.cget("state")) == tk.DISABLED:
            return True
        try:
            value = float(self.priceSelected.get())
            if value >= 0.0:
                return True
            return False
        except Exception:
            return False

    def is_fee_valid(self):
        # If widget is disabled it should not affect the overall validity
        if str(self.eFee.cget("state")) == tk.DISABLED:
            return True
        try:
            value = float(self.feeSelected.get())
            if value >= 0.0:
                return True
            return False
        except Exception:
            return False

    def is_sd_valid(self):
        # If widget is disabled it should not affect the overall validity
        if str(self.eStampDuty.cget("state")) == tk.DISABLED:
            return True
        try:
            value = float(self.stampDutySelected.get())
            if value >= 0.0:
                return True
            return False
        except Exception:
            return False

    def is_notes_valid(self):
        # If widget is disabled it should not affect the overall validity
        if str(self.eNotes.cget("state")) == tk.DISABLED:
            return True
        try:
            test = str(self.notesSelected.get())
        except Exception as e:
            return False
        return True
