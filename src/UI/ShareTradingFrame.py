import os
import sys
import inspect
import tkinter as tk
from tkinter import ttk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from Utils.Utils import Callbacks, Utils
from .AddTradeDialogWindow import AddTradeDialogWindow
from .ConfirmWindow import ConfirmWindow

INVALID_STRING = "-"
assets_dir = os.path.join(Utils.get_install_path(), "data")


class ShareTradingFrame(tk.Frame):
    def __init__(self, parent, portfolio_id):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self._portfolio_id = portfolio_id
        self.callbacks = {}
        self.trades_cache = []
        self._create_UI()

    def set_callback(self, id, callback):
        self.callbacks[id] = callback

    def _create_UI(self):
        # Create frame containing buttons on the top row of the frame
        buttonsFrame = ttk.Frame(self, relief="groove", borderwidth=1)
        buttonsFrame.pack(fill="x", expand=True, anchor="n")
        # Add buttons for the share trading page
        self.save_icon = tk.PhotoImage(
            file=assets_dir + "/assets/save_file_icon.png"
        ).subsample(2)
        saveButton = ttk.Button(
            buttonsFrame, text="Save Portfolio", command=self._save_portfolio
        )
        saveButton.pack(side="left", anchor="n", padx=5, pady=5)
        saveButton.config(image=self.save_icon)

        self.save_as_icon = tk.PhotoImage(
            file=assets_dir + "/assets/save_as_file_icon.png"
        ).subsample(2)
        save_as_btn = ttk.Button(
            buttonsFrame, text="Save as...", command=self._save_as_portfolio
        )
        save_as_btn.pack(side="left", anchor="n", padx=5, pady=5)
        save_as_btn.config(image=self.save_as_icon)

        self.add_icon = tk.PhotoImage(
            file=assets_dir + "/assets/add_icon.png"
        ).subsample(2)
        addTradeButton = ttk.Button(
            buttonsFrame, text="Add Trade...", command=self._display_add_trade_panel
        )
        addTradeButton.pack(side="left", anchor="n", padx=5, pady=5)
        addTradeButton.config(image=self.add_icon)

        self.autoRefresh = tk.IntVar(value=1)
        self.autoRefreshCheckBox = ttk.Checkbutton(
            buttonsFrame,
            text="Auto",
            variable=self.autoRefresh,
            command=self.set_auto_refresh,
            onvalue=1,
            offvalue=0,
        )
        self.autoRefreshCheckBox.pack(side="right", anchor="n", padx=5, pady=5)
        self.refreshButton = ttk.Button(
            buttonsFrame, text="Refresh", command=self._refresh_live_data
        )
        self.refreshButton.pack(side="right", anchor="n", padx=5, pady=5)

        # This frame is a container for smaller frames displaying balances
        balancesFrame = ttk.Frame(self)
        balancesFrame.pack(fill="none", expand=True, anchor="n", pady=5)

        # Create frame containing fund balances
        fundBalFrame = ttk.Frame(balancesFrame, relief="groove", borderwidth=1)
        fundBalFrame.pack(side="left", fill="y", anchor="n", pady=5)
        # Create four different frames for cash, portfolio, total and profit/loss
        cashFrame = ttk.Frame(fundBalFrame)
        cashFrame.pack(side="left", fill="y", anchor="n", padx=10, pady=5)
        cashLabel = ttk.Label(cashFrame, text="Cash [£]")
        cashLabel.pack(side="top")
        self.cashStringVar = tk.StringVar()
        cashValueLabel = ttk.Label(cashFrame, textvariable=self.cashStringVar)
        cashValueLabel.pack(side="bottom")
        # Portfolio balance frame
        portfolioFrame = ttk.Frame(fundBalFrame)
        portfolioFrame.pack(side="left", fill="y", anchor="n", padx=10, pady=5)
        portfolioLabel = ttk.Label(portfolioFrame, text="Portfolio [£]")
        portfolioLabel.pack(side="top")
        self.portfolioStringVar = tk.StringVar()
        portfolioValueLabel = ttk.Label(
            portfolioFrame, textvariable=self.portfolioStringVar
        )
        portfolioValueLabel.pack(side="bottom")
        # Total value balance frame
        totalFrame = ttk.Frame(fundBalFrame)
        totalFrame.pack(side="left", fill="both", anchor="n", padx=10, pady=5)
        totalLabel = ttk.Label(totalFrame, text="Total [£]")
        totalLabel.pack(side="top")
        self.totalStringVar = tk.StringVar()
        totalValueLabel = ttk.Label(totalFrame, textvariable=self.totalStringVar)
        totalValueLabel.pack(side="bottom")
        # profits balance frames
        plFrame = ttk.Frame(fundBalFrame)
        plFrame.pack(side="left", fill="both", anchor="n", padx=10, pady=5)
        plLabel = ttk.Label(plFrame, text="P/L [£]")
        plLabel.pack(side="top")
        self.plStringVar = tk.StringVar()
        self.plStringVar.trace_add("write", self._update_pl_label_background)
        self.plValueLabel = ttk.Label(plFrame, textvariable=self.plStringVar)
        self.plValueLabel.pack(side="bottom")
        plpcFrame = ttk.Frame(fundBalFrame)
        plpcFrame.pack(side="left", fill="both", anchor="n", padx=10, pady=5)
        plpcLabel = ttk.Label(plpcFrame, text="P/L [%]")
        plpcLabel.pack(side="top")
        self.plpcStringVar = tk.StringVar()
        self.plpcStringVar.trace_add("write", self._update_pl_label_background)
        self.plpcValueLabel = ttk.Label(plpcFrame, textvariable=self.plpcStringVar)
        self.plpcValueLabel.pack(side="bottom")

        # Create frame containing open positions P/L
        holdBalFrame = ttk.Frame(balancesFrame, relief="groove", borderwidth=1)
        holdBalFrame.pack(side="left", fill="y", anchor="n", padx=5, pady=5)
        # holding P/L of current positions
        holdPlFrame = ttk.Frame(holdBalFrame)
        holdPlFrame.pack(side="left", fill="y", anchor="n", padx=10, pady=5)
        holdPlLabel = ttk.Label(holdPlFrame, text="Holding P/L [£]")
        holdPlLabel.pack(side="top")
        self.holdPLStringVar = tk.StringVar()
        self.holdPLStringVar.trace_add("write", self._update_pl_label_background)
        self.holdPLValueLabel = ttk.Label(
            holdPlFrame, textvariable=self.holdPLStringVar
        )
        self.holdPLValueLabel.pack(side="bottom")
        holdPlPcFrame = ttk.Frame(holdBalFrame)
        holdPlPcFrame.pack(side="left", fill="y", anchor="n", padx=10, pady=5)
        holdPlPcLabel = ttk.Label(holdPlPcFrame, text="Holding P/L [%]")
        holdPlPcLabel.pack(side="top")
        self.holdPlPcStringVar = tk.StringVar()
        self.holdPlPcStringVar.trace_add("write", self._update_pl_label_background)
        self.holdPlPcValueLabel = ttk.Label(
            holdPlPcFrame, textvariable=self.holdPlPcStringVar
        )
        self.holdPlPcValueLabel.pack(side="bottom")

        # Frame containing the holdings table
        holdingsFrame = ttk.Frame(self, relief="groove", borderwidth=1)
        holdingsFrame.pack(fill="x", expand=True, anchor="n")
        # Title label
        currLabel = ttk.Label(holdingsFrame, text="Portfolio")
        currLabel.pack()
        # Create a table for the current data
        self.currentDataTreeView = ttk.Treeview(holdingsFrame)
        self.currentDataTreeView.pack(fill="x")
        self.currentDataTreeView["columns"] = (
            "quantity",
            "open",
            "last",
            "cost",
            "value",
            "pl",
            "pl_pc",
        )
        self.currentDataTreeView.heading("#0", text="Symbol", anchor="w")
        self.currentDataTreeView.heading("quantity", text="Quantity", anchor="w")
        self.currentDataTreeView.heading("open", text="Open [p]", anchor="w")
        self.currentDataTreeView.heading("last", text="Last [p]", anchor="w")
        self.currentDataTreeView.heading("cost", text="Cost [£]", anchor="w")
        self.currentDataTreeView.heading("value", text="Value [£]", anchor="w")
        self.currentDataTreeView.heading("pl", text="P/L £", anchor="w")
        self.currentDataTreeView.heading("pl_pc", text="P/L %", anchor="w")
        self.currentDataTreeView.column("#0", width=100)
        self.currentDataTreeView.column("quantity", width=100)
        self.currentDataTreeView.column("open", width=100)
        self.currentDataTreeView.column("last", width=100)
        self.currentDataTreeView.column("cost", width=100)
        self.currentDataTreeView.column("value", width=100)
        self.currentDataTreeView.column("pl", width=100)
        self.currentDataTreeView.column("pl_pc", width=100)
        # Treeview colour layout
        self.currentDataTreeView.tag_configure("profit", background="lightgreen")
        self.currentDataTreeView.tag_configure("loss", background="LightPink1")
        self.currentDataTreeView.tag_configure("invalid", background="yellow")

        # Frame containing the trading history
        logFrame = ttk.Frame(self, relief="groove", borderwidth=1)
        logFrame.pack(fill="x", expand=True, anchor="n")
        # Title label
        logLabel = ttk.Label(logFrame, text="Trades History")
        logLabel.pack()
        # Use a Frame as container for the treeview and the scrollbar
        tableFrame = ttk.Frame(logFrame)
        tableFrame.pack(fill="x")
        # Create a table for the trading log
        self.logTreeView = ttk.Treeview(tableFrame)
        self.logTreeView.pack(fill="x", side="left", expand=True)
        self.logTreeView["columns"] = (
            "action",
            "symbol",
            "quantity",
            "price",
            "fee",
            "stamp_duty",
            "total",
        )
        self.logTreeView.heading("#0", text="Date", anchor="w")
        self.logTreeView.heading("action", text="Action", anchor="w")
        self.logTreeView.heading("symbol", text="Symbol", anchor="w")
        self.logTreeView.heading("quantity", text="Quantity", anchor="w")
        self.logTreeView.heading("price", text="Price [p]", anchor="w")
        self.logTreeView.heading("fee", text="Fee [£]", anchor="w")
        self.logTreeView.heading("stamp_duty", text="Stamp Duty [%]", anchor="w")
        self.logTreeView.heading("total", text="Total [£]", anchor="w")
        self.logTreeView.column("#0", width=100)
        self.logTreeView.column("action", width=100)
        self.logTreeView.column("symbol", width=100)
        self.logTreeView.column("quantity", width=100)
        self.logTreeView.column("price", width=100)
        self.logTreeView.column("fee", width=100)
        self.logTreeView.column("stamp_duty", width=100)
        self.logTreeView.column("total", width=100)
        # Treeview colour layout
        self.logTreeView.tag_configure("oddrow", background="white")
        self.logTreeView.tag_configure("evenrow", background="lightblue")
        # Create a scrollbar for the history log
        scrollBar = tk.Scrollbar(
            tableFrame, orient="vertical", command=self.logTreeView.yview
        )
        scrollBar.pack(side="right", fill="y")
        self.logTreeView.configure(yscrollcommand=scrollBar.set)
        # Create popup menu for the trade history log
        self.logPopupMenu = tk.Menu(self.logTreeView, tearoff=0)
        self.logPopupMenu.add_command(
            label="Add trade...", command=self._display_add_trade_panel
        )
        self.logPopupMenu.add_command(
            label="Delete last...", command=self._delete_last_trade
        )
        self.logTreeView.bind("<Button-3>", self._trade_log_popup_menu_event)

    def _trade_log_popup_menu_event(self, event):
        self.logPopupMenu.tk_popup(event.x_root, event.y_root)

    def _display_add_trade_panel(self):
        AddTradeDialogWindow(self.parent, self._on_add_new_trade_event)

    def _delete_last_trade(self):
        ConfirmWindow(
            self.parent,
            "Confirm",
            "Are you sure?",
            self._on_confirmed_delete_last_trade,
        )

    def _on_confirmed_delete_last_trade(self):
        self.callbacks[Callbacks.ON_DELETE_LAST_TRADE_EVENT](self._portfolio_id)

    def _on_add_new_trade_event(self, new_trade):
        return self.callbacks[Callbacks.ON_NEW_TRADE_EVENT](
            new_trade, self._portfolio_id
        )

    def _refresh_live_data(self):
        # Disable the refresh inputs temporarily
        self.refreshButton.config(state="disabled")
        self.autoRefreshCheckBox.config(state="disabled")
        # Notify the Controller to request new data
        self.callbacks[Callbacks.ON_MANUAL_REFRESH_EVENT](self._portfolio_id)

    def _check_string_value(self, var):
        valid_var = var
        if var is None or len(var) < 1:
            valid_var = INVALID_STRING
        return valid_var

    def _check_float_value(self, var, valid=True, canBeNegative=False):
        valid_var = var
        if var is None or (not canBeNegative and var < 0) or not valid:
            valid_var = INVALID_STRING
        else:
            valid_var = round(var, 3)
        return valid_var

    def _update_pl_label_background(self, *args):
        try:
            value = float(self.plStringVar.get())
            self.plValueLabel.config(foreground="green" if value >= 0.0 else "red")
        except:
            pass
        try:
            value = float(self.plpcStringVar.get())
            self.plpcValueLabel.config(foreground="green" if value >= 0.0 else "red")
        except:
            pass
        try:
            value = float(self.holdPLStringVar.get())
            self.holdPLValueLabel.config(foreground="green" if value >= 0.0 else "red")
        except:
            pass
        try:
            value = float(self.holdPlPcStringVar.get())
            self.holdPlPcValueLabel.config(
                foreground="green" if value >= 0.0 else "red"
            )
        except:
            pass

    def _save_portfolio(self):
        self.callbacks[Callbacks.ON_SAVE_LOG_FILE_EVENT](self._portfolio_id)

    def _save_as_portfolio(self):
        self.callbacks[Callbacks.ON_SAVE_AS_EVENT](self._portfolio_id)

    def _update_refresh_button_state(self):
        # Disable the Refresh button when AutoRefresh is active
        self.autoRefreshCheckBox.config(state="enabled")  # reset status of checkbox
        value = self.autoRefresh.get()
        self.refreshButton.config(state="disabled" if value == 1 else "enabled")

    def _logtreeview_changed(self, trades):
        """Return True if the logTreeView contains exactly the same
        trades in the given list. Otherwise returns False"""
        if trades == self.trades_cache:
            return False
        return True

    def set_auto_refresh(self):
        self._update_refresh_button_state()
        value = self.autoRefresh.get()
        self.callbacks[Callbacks.ON_SET_AUTO_REFRESH_EVENT](
            bool(value), self._portfolio_id
        )

    def add_entry_to_log_table(self, trade):
        v_date = self._check_string_value(trade.date.strftime("%d/%m/%Y"))
        v_act = self._check_string_value(trade.action.name)
        v_sym = self._check_string_value(trade.symbol)
        v_am = self._check_float_value(trade.quantity)
        v_pri = self._check_float_value(trade.price)
        v_fee = self._check_float_value(trade.fee)
        v_sd = self._check_float_value(trade.sdr)
        v_tot = self._check_float_value(trade.total, canBeNegative=True)
        tag = "evenrow" if len(self.logTreeView.get_children()) % 2 == 0 else "oddrow"
        self.logTreeView.insert(
            "",
            "end",
            text=v_date,
            values=(v_act, v_sym, v_am, v_pri, v_fee, v_sd, v_tot),
            tags=(tag,),
        )
        self.trades_cache.append(trade)

    def update_trades_log(self, trades):
        if self._logtreeview_changed(trades):
            self.reset_view(True)
            for trade in trades:
                self.add_entry_to_log_table(trade)

    def update_share_trading_holding(
        self, symbol, quantity, openPrice, lastPrice, cost, value, pl, plPc, validity
    ):
        v_symbol = self._check_string_value(symbol)
        v_quantity = self._check_float_value(quantity)
        v_openPrice = self._check_float_value(openPrice)
        v_lastPrice = self._check_float_value(lastPrice, valid=validity)
        v_cost = self._check_float_value(cost)
        v_value = self._check_float_value(value, valid=validity)
        v_pl = self._check_float_value(pl, valid=validity, canBeNegative=True)
        v_plPc = self._check_float_value(plPc, valid=validity, canBeNegative=True)
        tag = "invalid"
        if validity:
            tag = "profit" if plPc >= 0 else "loss"
        found = False
        for child in self.currentDataTreeView.get_children():
            item = self.currentDataTreeView.item(child)
            s = item["text"]
            if v_symbol == s:
                found = True
                self.currentDataTreeView.item(
                    child,
                    values=(
                        v_quantity,
                        v_openPrice,
                        v_lastPrice,
                        v_cost,
                        v_value,
                        v_pl,
                        v_plPc,
                    ),
                    tags=(tag,),
                )
                break
        if not found:
            # tag = "evenrow" if len(self.currentDataTreeView.get_children()) % 2 == 0 else "oddrow"
            self.currentDataTreeView.insert(
                "",
                "end",
                text=symbol,
                values=(
                    v_quantity,
                    v_openPrice,
                    v_lastPrice,
                    v_cost,
                    v_value,
                    v_pl,
                    v_plPc,
                ),
                tags=(tag,),
            )

    def update_portfolio_balances(
        self, cash, holdingsValue, totalValue, pl, plPerc, holdingPL, holdingPLPC, valid
    ):
        v_cash = self._check_float_value(cash)
        v_holdVal = self._check_float_value(holdingsValue, valid=valid)
        v_tot = self._check_float_value(totalValue, valid=valid)
        v_pl = self._check_float_value(pl, valid=valid, canBeNegative=True)
        v_plPerc = self._check_float_value(plPerc, valid=valid, canBeNegative=True)
        v_holdPl = self._check_float_value(holdingPL, valid=valid, canBeNegative=True)
        v_holdPlPc = self._check_float_value(
            holdingPLPC, valid=valid, canBeNegative=True
        )

        self.cashStringVar.set(str(v_cash))
        self.portfolioStringVar.set(str(v_holdVal))
        self.totalStringVar.set(str(v_tot))
        self.plStringVar.set(str(v_pl))
        self.plpcStringVar.set(str(v_plPerc))
        self.holdPLStringVar.set(str(v_holdPl))
        self.holdPlPcStringVar.set(str(v_holdPlPc))

    def reset_view(self, resetHistory=False):
        self._update_refresh_button_state()
        self.cashStringVar.set(str(INVALID_STRING))
        self.portfolioStringVar.set(str(INVALID_STRING))
        self.totalStringVar.set(str(INVALID_STRING))
        self.plStringVar.set(str(INVALID_STRING))
        self.plpcStringVar.set(str(INVALID_STRING))
        self.holdPLStringVar.set(str(INVALID_STRING))
        self.holdPlPcStringVar.set(str(INVALID_STRING))
        self.currentDataTreeView.delete(*self.currentDataTreeView.get_children())
        if resetHistory:
            self.logTreeView.delete(*self.logTreeView.get_children())
            self.trades_cache = []
