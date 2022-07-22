from requests import options
from utils import Service, Trade, init_stock_trades, init_options_trades, get_trades_df
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
            
            for value in user_service.open_trades.values():
                st.write(value.symbol , value.status, value.entry_price)
        st.write("---")    
        st.write("## Second, let's handle the options trades")
        st.write("---")
        st.write("### Please select the following columns in this order from the tracker: ")
        st.write("#### Symbol, Option Data, Entry Price")
            
        options = st.text_input("copy and paste options data from the Tracker.")
        if st.button("add stock options"):
            init_options_trades(user_service, options)
            st.write("---")
            st.write("## Okay, here are your open trades:")
            st.write("---")
            trade_df = (get_trades_df(user_service))
            st.table(trade_df)
            # Here I would allow people to verify the table and make sure everything looks okay -- or add an edit trades option
            trade_df.to_csv(f"{user_service.name}_open_trades.csv")


    elif user_action == "View Open Trades":
        # read in csv of open trades
        trade_df = pd.read_csv(f"{user_service.name}_open_trades.csv")
        trades = st.sidebar.selectbox("What would you like to view?", ("Open Stock Trades", "Open Options Trades"))
        # split off into stock and options
        stock_df = trade_df[trade_df['is_option']== False]
        option_df = trade_df[trade_df['is_option']== True]
        # set index
        stock_df.set_index(stock_df.columns[0], inplace=True)
        option_df.set_index(option_df.columns[0], inplace=True)
        # drop unimportant columns from dfs
        cols_stock = ["long_short", "entry_price", "current_price"]
        cols_option = ["long_short", "entry_price", "current_price", "expiration", "strike", "current_price"]
        stock_df = stock_df[[c for c in stock_df.columns if c in cols_stock]]
        option_df = option_df[[c for c in option_df.columns if c in cols_option]]

        def calc_p_l(row):
            if row['long_short'] == "Long":
                return row['current_price'] - row['entry_price']
            else:  
                return row['entry_price'] - row['current_price']
        
        stock_df['P/L'] = stock_df.apply( lambda row: calc_p_l(row), axis=1)
        option_df['P/L'] = option_df.apply( lambda row: calc_p_l(row), axis=1)

        stock_df['P/L%'] = stock_df['P/L']/stock_df['entry_price']
        option_df['P/L%'] = option_df['P/L']/option_df['entry_price']


        if trades == "Open Stock Trades":
            st.dataframe(stock_df)
        elif trades == "Open Options Trades":
            st.dataframe(option_df)