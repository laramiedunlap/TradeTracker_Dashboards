from requests import options
from utils import Service, Trade, init_stock_trades, init_options_trades
import streamlit as st
import pandas as pd






service = st.selectbox(
    "Which service would you like?",
    (['Select',"Money Flows Elite", "Link Trades"])
)

if service != 'Select':
    st.write(f"You selected: {service}")
    @st.cache(allow_output_mutation=True) 
    def user_service_set(name):
        return Service(name=name, KPI= {}, open_trades={})
    user_service = user_service_set(service) 
    user_action = st.selectbox(label = "What would you like to do?",options =["Select","Input New Open Trades", "View Open Trades", "Close Open Trades"])


    if user_action == "Input New Open Trades":
        st.write("---")
        st.write("## First, let's handle the stock trades")
        st.write("---")
        st.write("### Please select the following columns in this order from the tracker: ")
        st.write("#### Symbol, Long/Short, Entry Price")

        stocks = st.text_input("copy and paste from the Tracker.")
        if st.button("add stock trades"):
            init_stock_trades(user_service, stocks)
            st.write(user_service.open_trades.keys())
        st.write("---")    
        st.write("## Second, let's handle the options trades")
        st.write("---")
        st.write("### Please select the following columns in this order from the tracker: ")
        st.write("#### Symbol, Option Data, Entry Price")
            
        options = st.text_input("copy and paste options data from the Tracker.")
        if st.button("add stock options"):
            init_options_trades(user_service, options)
            st.write(user_service.open_trades.keys())

        for value in user_service.open_trades.values():
            st.write(value.symbol , value.status, value.entry_price, value.is_option, value.expiration)