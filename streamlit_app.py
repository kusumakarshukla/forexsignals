import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import time
import requests
import numpy as np

# Define currency pairs to monitor
ASSETS = ['EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X', 'NZDUSD=X',
 'EURGBP=X', 'EURAUD=X', 'EURCAD=X', 'EURNZD=X', 'EURJPY=X', 'EURCHF=X', 'GBPAUD=X',
 'GBPCAD=X', 'GBPCHF=X', 'GBPJPY=X', 'GBPNZD=X', 'AUDJPY=X', 'CADJPY=X', 'CHFJPY=X',
 'NZDJPY=X', 'AUDCAD=X', 'AUDCHF=X', 'AUDNZD=X', 'CADCHF=X', 'NZDCAD=X', 'NZDCHF=X',
 'USDSGD=X', 'USDHKD=X', 'USDSEK=X', 'USDNOK=X', 'USDDKK=X', 'USDMXN=X', 'USDZAR=X',
 'USDTRY=X', 'USDCNH=X', 'USDRUB=X', 'USDINR=X', 'USDTHB=X', 'USDIDR=X', 'EURSEK=X',
 'EURNOK=X', 'EURDKK=X', 'EURTRY=X', 'EURHUF=X', 'EURPLN=X', 'GBPSGD=X', 'GBPZAR=X',
 'AUDSGD=X', 'CHFSGD=X', 'SGDJPY=X']

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
           
    df["Prev_SMA_50"] = df["SMA_50"].shift(1)  # Previous day's 50 SMA
    df["Prev_SMA_200"] = df["SMA_200"].shift(1)  # Previous day's 200 SMA

    df["SMA_Signal"] = np.where(
        (df["Prev_SMA_50"] < df["Prev_SMA_200"]) & (df["SMA_50"] > df["SMA_200"]),
        "BUY",
        np.where(
            (df["Prev_SMA_50"] > df["Prev_SMA_200"]) & (df["SMA_50"] < df["SMA_200"]),
            "SELL",
            "HOLD"
        )
    )
    return df

# Streamlit app
st.title("Live Forex Trading Signals")

while True:
    signals = []
    for asset in ASSETS:
            df = get_stock_data(asset, interval="1d", period="1y")
            if len(df)<10:
                continue
            df = add_indicators(df)
            df = generate_signals(df)
            df.dropna(inplace=True)
            latest = df.iloc[-1]
            signals.append([asset, latest["Close"], latest["Buy_Signal"], latest["Sell_Signal"],latest['RSI'],latest["SMA_Signal"]])
        
    # Convert to DataFrame and display
    signal_df = pd.DataFrame(signals, columns=["Asset", "Latest Price", "Buy Signal", "Sell Signal","RSI","SMA_Signal"])
    print(signal_df)
    st.subheader("Buy Signals")
    buy_df = signal_df[(signal_df['Buy Signal']==True ) | (signal_df[signal_df['SMA_Signal']=='BUY'])]
    st.dataframe(buy_df)
    st.subheader("Sell Signals")
    sell_df= signal_df[(signal_df['Sell Signal']==True ) | (signal_df[signal_df['SMA_Signal']=='SELL'])]
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

    
    
    
