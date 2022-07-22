import os
import regex as re
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime


def options_chain(symbol):
    """Returns the entire option chain for a symbol to a dataframe"""
    
    tk = yf.Ticker(symbol)
    # Expiration dates
    exps = tk.options

    # Get options for each expiration
    options = pd.DataFrame()
    for e in exps:
        opt = tk.option_chain(e)
        opt = pd.DataFrame().append(opt.calls).append(opt.puts)
        opt['expirationDate'] = e
        options = options.append(opt, ignore_index=True)

    # Get expiration Date
    options['expirationDate'] = pd.to_datetime(options['expirationDate'])
    options['dte'] = (options['expirationDate'] - dt.datetime.today()).dt.days / 365
    
    # Boolean column if the option is a CALL
    options['CALL'] = options['contractSymbol'].str[4:].apply(
        lambda x: "C" in x)
    
    # Calculate the midpoint of the bid-ask
    options[['bid', 'ask', 'strike']] = options[['bid', 'ask', 'strike']].apply(pd.to_numeric)
    options['mark'] = (options['bid'] + options['ask']) / 2 
    
    # Drop unnecessary columns
    options = options.drop(columns = ['contractSize', 'currency', 'lastTradeDate'])

    return options


class Service:
    def __init__(self, name, KPI, open_trades):
        self.name = name
        self.KPI = {}
        self.open_trades = open_trades

    def open_trades_df(self):
        rows = {}
        for key in self.open_trades.keys():
            rows[key] =(self.open_trades[key].__dict__)
        return pd.DataFrame(rows).transpose()

class Trade:
    def __init__(self, service_name, status, symbol, long_short, size, is_option, entry_price):
        self.service_name = service_name
        self.status = status
        self.symbol = symbol
        self.long_short = long_short
        self.size = 1
        self.entry_price = entry_price   
        self.is_option = is_option

    def set_opt_details(self, expry, strike, opt_tp):
        if self.is_option:
            self.expiration = expry
            self.strike = strike
            self.opt_type = opt_tp
        else:
            self.expiration = expry
            self.strike = strike
            self.opt_type = opt_tp

    def set_current_price(self):
        self.current_price = round(float(yf.Ticker(self.symbol).history(period="1d")['Close']),2)
    
    def set_current_opt_price(self):
        """Get the mark for an options trade"""
        # 1) Create an options chain dataframe
        chain = options_chain(str(self.symbol).capitalize())
        # 2) Match expiration date col and expry format
        expry = pd.to_datetime(self.expiration).date()
        chain['expirationDate'] = pd.DatetimeIndex(chain['expirationDate']).date
        # 3) Slice to the matching expiration date
        _slice = chain[chain['expirationDate'] == expry ]
        # 4) Slice to the matching option type
        if self.opt_type == 'CALL':
            _slice = _slice[_slice['CALL']==True]
        else: 
            _slice = _slice[_slice['CALL']==False]
        # 5) Slice to the matching strike price, find the current mark
        self.current_price = round(float(_slice[_slice['strike']==self.strike]['mark']),2)
        return self.current_price


def init_stock_trades(service, user_string):
    """Takes a string copied from google sheets and creates trade objects inside of a Service"""
    user_list = re.findall(r'\S+\s\S+\s\S+', user_string)
    user_list = [x.replace('\t',';') for x in user_list]
    for elem in user_list:
        trd_details = elem.split(';')
        tk = trd_details[0]
        l_s = trd_details[1]
        e_p = trd_details[2][1:]
        expry = None
        strike = None
        opt_tp = None

        service.open_trades[tk] = Trade(service_name=service.name, status= "open", symbol=tk, long_short=l_s, size=1, entry_price=float(e_p), is_option = False)
        service.open_trades[tk].set_opt_details(expry, strike, opt_tp)

        service.open_trades[tk].set_current_price()
    
    return None

def init_options_trades(service, user_string):
    """Takes a string copied from google sheets and creates options trade objects inside of a Service"""
    user_list = user_list = re.findall(r'\S+\s\S+\s\S+\s\S+', user_string)
    user_list = [x.replace('\t',';') for x in user_list]
    for elem in user_list:
        trd_details = elem.split(';')
        tk = trd_details[0]
        l_s = "Long"
        e_p = trd_details[2][1:]

        expry = trd_details[1].split(' ')[0]
        strike = float(trd_details[1].split(' ')[1][1:])

        opt_tp = str(trd_details[1].split(' ')[1][0])

        if opt_tp.capitalize() == "C":
            opt_tp = "CALL"
        else:
            opt_tp = "PUT"

        service.open_trades[f"{tk}--{opt_tp}"] = Trade(service_name=service.name, status= "open",symbol=(tk),long_short=l_s,size=1, entry_price=float(e_p), is_option= True)
        service.open_trades[f"{tk}--{opt_tp}"].set_opt_details(expry, strike, opt_tp)

        service.open_trades[f"{tk}--{opt_tp}"].set_current_opt_price()

    return None



def get_trades_df(service):
        rows = {}
        for key in service.open_trades.keys():
            rows[key] =(service.open_trades[key].__dict__)
        return pd.DataFrame(rows).transpose()