import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt

st.set_page_config(page_title="\U0001F4B1 Positions", layout="wide")
st.title("\U0001F4B1 Positions")

try:
    # Read secrets from .streamlit/secrets.toml or Streamlit Cloud
    DB_HOST = st.secrets["database"]["host"]
    DB_PORT = st.secrets["database"]["port"]
    DB_NAME = st.secrets["database"]["name"]
    DB_USER = st.secrets["database"]["user"]
    DB_PASSWORD = st.secrets["database"]["password"]
    SSL_MODE = st.secrets["database"].get("sslmode", "require")

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
        exchange_rate = 0.31  # 1 USD = 0.31 KWD
        currency_symbol = "د.ك"  # Dinar symbol
        decimal_places = 3

    # --- Apply exchange rate to numeric columns ---
    numeric_cols = [
        "Avg Cost/Unit", "Last Price", "Cost Basis", "Market Value", "Unrealized Gain ($)"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(float) * exchange_rate

    # --- Apply color to return columns ---
    def color_returns(val):
        color = "green" if val > 0 else "red" if val < 0 else "black"
        return f"color: {color}"

    return_columns = ["Unrealized Gain ($)", "Unrealized Gain (%)"]

    styled_df = (
        df.style
        .hide(axis="index")
        .format({
            "Avg Cost/Unit": f"{{:.{decimal_places}f}}",
            "Last Price": f"{{:.{decimal_places}f}}",
            "Cost Basis": f"{{:.{decimal_places}f}}",
            "Market Value": f"{{:.{decimal_places}f}}",
            "Unrealized Gain ($)": f"{{:.{decimal_places}f}}",
            "Unrealized Gain (%)": "{:.2f}%"
        })
        .applymap(color_returns, subset=return_columns)
    )

    # --- Layout ---
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.container(border=True):
            st.subheader(f"\U0001F4CB Position Table ({selected_currency})")
            st.write(styled_df)

# --- Totals Display ---
            total_cb = df["Cost Basis"].sum()
            total_mv = df["Market Value"].sum()
            total_ug = df["Unrealized Gain ($)"].sum()
            st.markdown("**Totals:**")
            st.markdown(f"- **Total Cost Basis:** {currency_symbol}{total_cb:,.2f}")
            st.markdown(f"- **Total Market Value:** {currency_symbol}{total_mv:,.2f}")
            st.markdown(f"- **Total Unrealized Gain:** {currency_symbol}{total_ug:,.2f}")

    with col2:
        with st.container(border=True):
            st.subheader("\U0001F967 Portfolio Breakdown")
            breakdown = df.groupby("Security Type")["Market Value"].sum()
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            ax2.pie(breakdown, labels=breakdown.index, autopct="%1.1f%%", startangle=90, textprops={"fontsize": 9})
            ax2.axis("equal")
            st.pyplot(fig2, use_container_width=False)

    with st.container(border=True):
        st.subheader("\U0001F4CA Market Value by Symbol")
        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(df["Symbol"], df["Market Value"], color="#4CAF50")
        ax.set_ylabel(f"Market Value ({currency_symbol})")
        ax.set_xlabel("Symbol")
        ax.set_title("My Positions")
        ax.bar_label(bars, fmt='%.0f', padding=3)
        st.pyplot(fig, use_container_width=False)

except Exception as e:
    st.error(f"\u274C Database connection failed:\n{e}")
