import streamlit as st
import yfinance as yf
import datetime as dt
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
from IPython.display import display


st.title("Technical Data ")

nation = st.selectbox(
"select a stock market", options=["None","Saudi Arabia","United States"], index=0
)
if nation is None:
    st.warning("Please select a stock market")
    st.stop()
if nation == "None":
    st.warning("Please select a stock market")
    st.stop()


stock = st.text_input("Please insert Ticker")

if stock is None:
    st.warning("Please select a stock")
    st.stop()

if nation == "Saudi Arabia":
    if not stock.upper().endswith(".SR"):
        stock = stock + ".SR"
if nation == "United States":
    stock = stock
if stock == "":
    st.stop()
    


stock= yf.Ticker(stock)
data = stock.history("1y")
name = stock.info.get("longName")

if name is None:
    st.warning("Please select a stock")
    st.stop()
st.write(name + ": Has been selected")

length = st.selectbox(
"select Data length", options=["","1","2","3","4","5"], index=0
)
if length == "":
    st.warning("Please select length")
    st.stop()

if length is None:
    st.warning("Please select a length")
    st.stop()
length = str(length) + "y"
data = stock.history(length)
data.index = data.index.strftime("%Y-%m-%d")
close = data["Close"]






data["ma20"] = data["Close"].rolling(20).mean()
data["ma50"] = data["Close"].rolling(50).mean()

data["returns"] = np.log(close/close.shift(1))
returns_table = data[["returns"]]
cumulative_returns = np.cumsum(returns_table)
ma_table = data[["Close","ma20","ma50"]]
price_table = data["Close"]


ma_data = st.button("click here to see moving average data", key="show_ma_data")
if ma_data:
        with st.expander("Price Graph", expanded=True):
            st.dataframe(ma_table.head(1000))
            

ma_table_graph = st.button("click here to see moving average graph", key="show_ma_graph")
if ma_table_graph:
        with st.expander("Moving Average Graph", expanded=True):
            st.line_chart(ma_table)


price_graph = st.button("click here to see price graph", key="show_price_graph")
if price_graph:
        with st.expander("Price Graph", expanded=True):
            st.line_chart(price_table)


return_graph = st.button("click here to see cumulative return graph", key="show_graphs")
if return_graph:
        with st.expander("Return Graph", expanded=True):
            st.line_chart(cumulative_returns)
