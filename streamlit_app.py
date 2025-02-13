import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import time

# Define currency pairs to monitor
ASSETS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", 
    "USDCHF=X", "NZDUSD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X","GBPUSD=X"
]  # Add more currency pairs as needed
REFRESH_INTERVAL = 300  # 5 minutes in seconds

# Function to fetch forex data
def get_stock_data(symbol, interval="1d", period="30d"):
    df = yf.download(symbol, interval=interval, period=period)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df.dropna(inplace=True) 
    return df

# Function to calculate technical indicators
def add_indicators(df):
    df["SMA_50"] = ta.sma(df["Close"], length=50)
    df["SMA_200"] = ta.sma(df["Close"], length=200)
    df["RSI"] = ta.rsi(df["Close"], length=14)
    bbands = ta.bbands(df["Close"], length=20)
    bbands = ta.bbands(df["Close"], length=20)
    df["BB_Upper"] = bbands["BBU_20_2.0"]
    df["BB_Lower"] = bbands["BBL_20_2.0"]
    df["BB_Mid"] = bbands["BBM_20_2.0"]
    
    return df

# Function to generate buy/sell signals
def generate_signals(df):
    df["Buy_Signal"] = (
        (df["RSI"] <= 45) & 
        (df["Close"] < df["BB_Mid"]) & 
        (df["SMA_50"] > df["SMA_200"]) )
           
       
    
    
    
    df["Sell_Signal"] = (
        (df["RSI"] >= 55) & 
        (df["Close"] > df["BB_Mid"]) & 
        ((df["SMA_50"] < df["SMA_200"])))
    
    return df

# Streamlit app
st.title("Live Forex Trading Signals")
st.write("This app updates every 5 minutes with Buy/Sell signals for major currency pairs.")

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
st.dataframe(signal_df[(signal_df['Buy Signal']==True )])
st.subheader("Sell Signals")
st.dataframe(signal_df[(signal_df['Sell Signal']==True )])
st.write("Refreshing in 5 minutes...")
    
    
    
