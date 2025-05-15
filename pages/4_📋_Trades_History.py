import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(page_title="📋 Trades History", layout="wide")
st.title("📋 Trades History")

# --- Connect to Supabase ---
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
    cursor.execute("SELECT * FROM trades_history ORDER BY trade_date DESC;")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)

    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ Database connection failed:\n{e}")