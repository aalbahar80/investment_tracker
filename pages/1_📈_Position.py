import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt

st.set_page_config(page_title="📈 Positions", layout="wide")
st.title("📈 Positions")

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

    col1, col2 = st.columns([2, 1])

    with col1:
        with st.container(border=True):
            st.subheader("📋 Position Table")
            st.dataframe(df.style.hide(axis="index"), use_container_width=True)

    with col2:
        with st.container(border=True):
            st.subheader("🥇 Portfolio Breakdown")
            breakdown = df.groupby("Security Type")["Market Value"].sum()
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            ax2.pie(breakdown, labels=breakdown.index, autopct="%1.1f%%", startangle=90, textprops={"fontsize": 9})
            ax2.axis("equal")
            st.pyplot(fig2, use_container_width=False)

    with st.container(border=True):
        st.subheader("📊 Market Value by Symbol")
        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(df["Symbol"], df["Market Value"], color="#4CAF50")
        ax.set_ylabel("Market Value ($)")
        ax.set_xlabel("Symbol")
        ax.set_title("My Positions")
        ax.bar_label(bars, fmt='%.0f', padding=3)
        st.pyplot(fig, use_container_width=False)

except Exception as e:
    st.error(f"❌ Database connection failed:\n{e}")
