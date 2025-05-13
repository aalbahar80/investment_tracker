import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="📈 Compare Tickers", layout="wide")
st.title("📈 Multi-Ticker Price Comparison")

st.markdown("Compare the historical stock prices of multiple tickers.")

# --- Form with framed layout ---
with st.form("compare_form"):
    col1, col2 = st.columns([1, 2])  # Wider second column for results

    with col1:
        tickers = st.text_input("Enter stock symbols (comma-separated):", value="AAPL, MSFT, GOOGL")
        start_date = st.date_input("Start date", pd.to_datetime("2022-01-01"))
        end_date = st.date_input("End date", pd.to_datetime("today"))
        submit = st.form_submit_button("Compare")

if submit:
    ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]

    if not ticker_list:
        st.warning("Please enter at least one ticker symbol.")
    else:
        try:
            data = yf.download(ticker_list, start=start_date, end=end_date)["Close"]

            if data.empty:
                st.error("No data found. Please check your symbols or date range.")
            else:
                if isinstance(data, pd.Series):
                    data = data.to_frame(name=ticker_list[0])

                # --- Return Calculation ---
                returns = {}
                for ticker in data.columns:
                    start_price = data[ticker].iloc[0]
                    end_price = data[ticker].iloc[-1]
                    return_percent = ((end_price - start_price) / start_price) * 100
                    returns[ticker] = round(return_percent, 2)

                return_df = pd.DataFrame.from_dict(returns, orient="index", columns=["Return (%)"])
                styled_df = return_df.style.applymap(
                    lambda x: "color: green" if x >= 0 else "color: red"
                )

                with col2:
                    with st.container(border=True):
                        st.subheader("📊 Return Summary")
                        st.dataframe(styled_df, use_container_width=True)

                # --- Chart Container ---
                with st.container(border=True):
                    st.subheader("📈 Price Comparison Chart")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    data.plot(ax=ax)
                    ax.set_title("Closing Prices")
                    ax.set_ylabel("Price ($)")
                    ax.set_xlabel("Date")
                    ax.legend(title="Ticker")
                    st.pyplot(fig)

        except Exception as e:
            st.error(f"⚠️ Error fetching data: {e}")
