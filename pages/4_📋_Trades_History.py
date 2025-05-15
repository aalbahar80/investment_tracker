import os
import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(page_title="📋 Trades History", layout="wide")
st.title("📋 Trades History")

# --- Connect to Supabase ---
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
    cursor.execute("SELECT * FROM trades_history ORDER BY trade_date DESC;")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)

    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ Database connection failed:\n{e}")