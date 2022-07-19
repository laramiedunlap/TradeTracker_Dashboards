import os
import regex as re
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime



class Service:
    def __init__(self, name, KPI, open_trades):
        self.name = name
        self.KPI = {}
        self.open_trades = {}

class Trade:
    def __init__(self, service_name, status, symbol, long_short, size, is_option, entry_price):
        self.service_name = service_name
        self.status = status
        self.symbol = symbol
        self.long_short = long_short
        self.size = 1
        self.is_option = is_option
        if str(status).capitalize() == 'OPEN':
            self.entry_date = dt.datetime.now().strftime('%m/%d/%Y')
        else:
            self.entry_date = np.NaN
        self.entry_price = entry_price
        self.exit_date = np.NaN
       
        self.exit_price = np.array([])
        if is_option:
            self.expiration = np.NaN
            self.strike = np.NaN
            self.opt_type = np.NaN

def init_stock_trades(service, ticker_string):
    """Takes a string copied from google sheets and creates trade objects inside of a Service"""
    user_list = re.findall(r'\S+\s\S+\s\S+', ticker_string)
    user_list = [x.replace('\t',';') for x in user_list]
    for elem in user_list:
        trd_details = elem.split(';')
        tk = trd_details[0]
        l_s = trd_details[1]
        e_p = trd_details[2][1:]
        service.open_trades[trd_details[0]] = Trade(service_name=service.name, status= "open",symbol=tk,long_short=l_s,size=1,is_option=False,entry_price=float(e_p))
    return None

def update_long_short(service, long_short_str):
    """Takes a string of long short statuses from google sheets and assigns them to their respective trades"""
    return None