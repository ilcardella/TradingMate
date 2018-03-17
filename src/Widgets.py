import tkinter as tk
from tkinter import ttk

class DatePicker(tk.Frame):

    def __init__(self, master, dateSelected):
        tk.Frame.__init__(self, master)
        self.parent = master
        self.dateSelected = dateSelected
        self.create_UI()

    def create_UI(self):
        tk.Label(self, text="dd").grid(row=0, column=0, sticky="w")
        self.day = tk.StringVar()
        self.day.trace_add('write', self.on_day_change_event)
        self.eDay = ttk.Entry(self, width=3, textvariable=self.day, validate="focusout", validatecommand=self.set_date)
        self.eDay.grid(row=1, column=0, sticky="w")

        tk.Label(self, text="/").grid(row=1, column=1, sticky="w")

        tk.Label(self, text="mm").grid(row=0, column=2, sticky="w")
        self.month = tk.StringVar()
        self.month.trace_add('write', self.on_month_change_event)
        self.eMonth = ttk.Entry(self, width=3, textvariable=self.month, validate="focusout", validatecommand=self.set_date)
        self.eMonth.grid(row=1, column=2, sticky="w")

        tk.Label(self, text="/").grid(row=1, column=3, sticky="w")

        tk.Label(self, text="yyyy").grid(row=0, column=4, sticky="w")
        self.year = tk.StringVar()
        self.year.trace_add('write', self.on_year_change_event)
        self.eYear = ttk.Entry(self, width=5, textvariable=self.year, validate="focusout", validatecommand=self.set_date)
        self.eYear.grid(row=1, column=4, sticky="w")

    def set_date(self):
        self.dateSelected.set(self.build_date(self.day.get(), self.month.get(), self.year.get()))

    def build_date(self, day, month, year):
        return "{0}/{1}/{2}".format(day, month, year)

    def on_day_change_event(self, *args):
        value = self.day.get()
        if len(value) > 2: 
            self.day.set(value[:2])
        elif len(value) == 2:
            self.eMonth.focus_set()
        self.set_date()
    
    def on_month_change_event(self, *args):
        value = self.month.get()
        if len(value) > 2:
            self.month.set(value[:2])
        elif len(value) == 2:
            self.eYear.focus_set()
        self.set_date()

    def on_year_change_event(self, *args):
        value = self.year.get()
        if len(value) > 4: 
            self.year.set(value[:4])
        self.set_date()

    def focus_set(self):
        tk.Frame.focus_set(self)
        self.eDay.focus_set()

