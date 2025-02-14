import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import time
import requests

# Define currency pairs to monitor
ASSETS = [
    "USDJPY=X", "EURUSD=X","GBPJPY=X","EURJPY=X","AUDUSD=X","GBPUSD=X","AUDJPY=X","USDCAD=X","EURAUD=X","NZDJPY=X","CADJPY=X","EURAUD=X","NZDJPY=X","CADJPY=X","EURGBP=X","CHFJPY=X","USDCHF=X","GBPCHF=X",
    "GBPCHF=X","EURCAD=X","AUDCAD=X","AUDCHF=X","NZDCAD=X","NZDCHF=X","GBPAUD=X","AUDNZD=X","GBPNZD=X","EURNZD=X","CADCHF=X","GBPCAD=X"
]  # Add more currency pairs as needed
REFRESH_INTERVAL = 1800  # 5 minutes in seconds
TELEGRAM_TOKEN = "7801392960:AAHApxpHlv5SDBtjAb2qYuXKE6wZEQlTIdU"
CHAT_ID = "7921155520"
# Function to fetch forex data
def get_stock_data(symbol, interval="1d", period="30d"):
    df = yf.download(symbol, interval=interval, period=period)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df.dropna(inplace=True) 
    return df

# Function to calculate technical indicators

def add_indicators(df):
    df["SMA_50"] = ta.sma(df["Close"], length=50).fillna(0)
    df["SMA_200"] = ta.sma(df["Close"], length=200).fillna(0)
    df["RSI"] = ta.rsi(df["Close"], length=14).fillna(0)
    bbands = ta.bbands(df["Close"], length=20).fillna(0)
    bbands = ta.bbands(df["Close"], length=20).fillna(0)
    df["BB_Upper"] = bbands["BBU_20_2.0"].fillna(0)
    df["BB_Lower"] = bbands["BBL_20_2.0"].fillna(0)
    df["BB_Mid"] = bbands["BBM_20_2.0"].fillna(0)
    
    return df

# Function to generate buy/sell signals
def generate_signals(df):
    df["Buy_Signal"] = (
        (df["RSI"] <= 30) )
           
       
    
    
    
    df["Sell_Signal"] = (
        (df["RSI"] >= 70) )
    
    return df

# Streamlit app
st.title("Live Forex Trading Signals")

while True:
    signals = []
    for asset in ASSETS:
            df = get_stock_data(asset, interval="1d", period="1y")
            if df.empty:
                continue
            df = add_indicators(df)
            df = generate_signals(df)
            latest = df.iloc[-1]
            signals.append([asset, latest["Close"], latest["Buy_Signal"], latest["Sell_Signal"],latest['RSI']])
        
    # Convert to DataFrame and display
    signal_df = pd.DataFrame(signals, columns=["Asset", "Latest Price", "Buy Signal", "Sell Signal","RSI"])
    
    st.subheader("Buy Signals")
    buy_df = signal_df[(signal_df['Buy Signal']==True )]
    st.dataframe(buy_df)
    st.subheader("Sell Signals")
    sell_df= signal_df[(signal_df['Sell Signal']==True )]
    st.dataframe(sell_df)
    if (len(buy_df)>0 or len(sell_df)>0):
        notification = ','.join(buy_df['Asset'].unique())
        notification = "BUY SIGNAL GENERATED-\n"+notification
        notification = notification+"\n\nSELL SIGNAL GENERATED-"+','.join(sell_df['Asset'].unique())
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": notification}
        requests.post(url, data=data)
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

    
    
    
