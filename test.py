from requests import options
from utils import Service, Trade, init_stock_trades
import streamlit as st

service = st.selectbox(
    "Which service would you like?",
    (['Select',"Money Flows Elite", "Link Trades"])
)

if service != 'Select':
    st.write(f"You selected: {service}")
    user_service = Service(name=service, KPI= {}, open_trades={})
    user_action = st.selectbox(label = "What would you like to do?",options =["Select","Input New Open Trades", "View Open Trades", "Close Open Trades"])

    if user_action == "Input New Open Trades":
        stocks = st.text_input("copy and paste tickers from the Tracker")
        init_stock_trades(user_service, stocks)
        for k in user_service.open_trades.keys():
            st.write(user_service.open_trades[k].entry_price)
