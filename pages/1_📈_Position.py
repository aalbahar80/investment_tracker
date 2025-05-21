import os
import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt

st.set_page_config(page_title="\U0001F4B1 Positions", layout="wide")
st.title("\U0001F4B1 Positions")

try:
    # --- Render-Only Secrets Reading ---
    DB_HOST = os.environ["DB_HOST"]
    DB_PORT = os.environ["DB_PORT"]
    DB_NAME = os.environ["DB_NAME"]
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    SSL_MODE = os.environ.get("SSL_MODE", "require")  # optional fallback

    # Establish connection
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        sslmode=SSL_MODE
    )
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM positions ORDER BY "Symbol";')
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)

    # --- Currency Selector ---
    selected_currency = st.selectbox("Select Currency:", ["USD", "KWD"])
    exchange_rate = 1.0
    currency_symbol = "$"
    decimal_places = 2

    if selected_currency == "KWD":
        exchange_rate = 0.31
        currency_symbol = "د.ك"
        decimal_places = 3

    numeric_cols = [
        "Avg Cost/Unit", "Last Price", "Cost Basis", "Market Value", "Unrealized Gain ($)", "Total Return %"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(float) * exchange_rate if "Return" not in col else df[col]

    def color_returns(val):
        color = "green" if val > 0 else "red" if val < 0 else "black"
        return f"color: {color}"

    return_columns = ["Unrealized Gain ($)", "Unrealized Gain (%)", "Total Return %"]
    styled_df = df.style.hide(axis="index").applymap(color_returns, subset=return_columns)

    # Layout: 2 rows, 2 columns each
    upper_col1, upper_col2 = st.columns(2)
    lower_col1, lower_col2 = st.columns(2)

    with upper_col1:
        with st.container(border=True):
            st.subheader("📋 Position Table")
            st.dataframe(styled_df, use_container_width=True)

            st.subheader("🧮 Totals")
            total_cb = df["Cost Basis"].sum()
            total_mv = df["Market Value"].sum()
            total_ug = df["Unrealized Gain ($)"].sum()
            st.markdown(f"**• Total Cost Basis:** {currency_symbol}{total_cb:,.2f}")
            st.markdown(f"**• Total Market Value:** {currency_symbol}{total_mv:,.2f}")
            st.markdown(f"**• Total Unrealized Gain:** {currency_symbol}{total_ug:,.2f}")

    with upper_col2:
        with st.container(border=True):
            st.subheader("🥧 Portfolio Breakdown")
            breakdown = df.groupby("Security Type")["Market Value"].sum()
            fig1, ax1 = plt.subplots(figsize=(5, 5))
            ax1.pie(breakdown, labels=breakdown.index, autopct="%1.1f%%", startangle=90, textprops={"fontsize": 9})
            ax1.axis("equal")
            st.pyplot(fig1, use_container_width=True)

    with lower_col1:
        with st.container(border=True):
            st.subheader("📈 Market Value by Symbol")
            df_sorted_mv = df.sort_values("Market Value", ascending=True)
            fig2, ax2 = plt.subplots(figsize=(6, len(df) * 0.5))
            bars = ax2.barh(df_sorted_mv["Symbol"], df_sorted_mv["Market Value"], color="#4CAF50")
            ax2.set_xlabel(f"Market Value ({currency_symbol})")
            ax2.set_title("Market Value Distribution")
            ax2.bar_label(bars, fmt='%.0f', padding=3)
            st.pyplot(fig2, use_container_width=True)

    with lower_col2:
        with st.container(border=True):
            st.subheader("📊 Total Return by Symbol")
            df_sorted_ret = df.sort_values("Total Return %", ascending=True)
            fig3, ax3 = plt.subplots(figsize=(6, len(df) * 0.5))
            bars_ret = ax3.barh(df_sorted_ret["Symbol"], df_sorted_ret["Total Return %"], color="#2196F3")
            ax3.set_xlabel("Total Return (%)")
            ax3.set_title("Total Return per Symbol")
            ax3.bar_label(bars_ret, fmt='%.2f%%', padding=3)
            st.pyplot(fig3, use_container_width=True)

except Exception as e:
    st.error(f"❌ Database connection failed:\n{e}")
