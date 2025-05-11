import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="📉 Stock Return Calculator", layout="centered")
st.title("📉 Stock Return Calculator")

# --- User Inputs ---
with st.form("stock_form"):
    symbol = st.text_input("Enter stock symbol (e.g., AAPL, TSLA, VTI)", "AAPL").upper()
    start_date = st.date_input("Start date")
    end_date = st.date_input("End date")
    submit = st.form_submit_button("Calculate Return")

# --- Process After Submit ---
if submit:
    # Download stock data
    data = yf.download(symbol, start=start_date, end=end_date)

    if not data.empty:
        start_price = float(data["Close"].iloc[0])
        end_price = float(data["Close"].iloc[-1])
        return_percent = ((end_price - start_price) / start_price) * 100

        st.subheader(f"📈 Return for {symbol} from {start_date} to {end_date}")
        st.metric(label="Return (%)", value=f"{return_percent:.2f}%")

        st.line_chart(data["Close"])
    else:
        st.warning("⚠️ No data returned. Please check the symbol or date range.")