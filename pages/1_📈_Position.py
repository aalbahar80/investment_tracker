# ✅ Currency conversion version of positions page
import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
from decimal import Decimal

st.set_page_config(page_title="📈 Positions", layout="wide")
st.title(":currency_exchange: Positions")

try:
    # Read secrets
    DB_HOST = st.secrets["database"]["host"]
    DB_PORT = st.secrets["database"]["port"]
    DB_NAME = st.secrets["database"]["name"]
    DB_USER = st.secrets["database"]["user"]
    DB_PASSWORD = st.secrets["database"]["password"]
    SSL_MODE = st.secrets["database"].get("sslmode", "require")

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

    # --- Currency Dropdown ---
    selected_currency = st.selectbox("Select Currency:", ["USD", "KWD"])
    exchange_rate = Decimal("1.0")
    currency_symbol = "$"

    if selected_currency == "KWD":
        exchange_rate = Decimal("0.31")
        currency_symbol = "كي‏"  # Arabic KWD Symbol

    # --- Currency Conversion on numeric columns ---
    convert_cols = [
        "Avg Cost/Unit", "Last Price", "Cost Basis", "Market Value", "Unrealized Gain ($)"
    ]
    for col in convert_cols:
        df[col] = df[col].apply(lambda x: round(Decimal(x) * exchange_rate, 2))

    # --- Layout ---
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.container(border=True):
            st.subheader(f"📋 Position Table ({selected_currency})")
            st.dataframe(df, use_container_width=True)

    with col2:
        with st.container(border=True):
            st.subheader("🥧 Portfolio Breakdown")
            breakdown = df.groupby("Security Type")["Market Value"].sum()
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            ax2.pie(breakdown, labels=breakdown.index, autopct="%1.1f%%", startangle=90, textprops={"fontsize": 9})
            ax2.axis("equal")
            st.pyplot(fig2, use_container_width=False)

    with st.container(border=True):
        st.subheader("📊 Market Value by Symbol")
        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(df["Symbol"], df["Market Value"], color="#4CAF50")
        ax.set_ylabel(f"Market Value ({currency_symbol})")
        ax.set_xlabel("Symbol")
        ax.set_title("My Positions")
        ax.bar_label(bars, fmt='%.0f', padding=3)
        st.pyplot(fig, use_container_width=False)

except Exception as e:
    st.error(f"❌ Database connection failed:\n{e}")
