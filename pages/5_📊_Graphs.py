import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2

st.set_page_config(page_title="📊 Graphs", layout="wide")
st.title("📊 Portfolio Visualizations")

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
    cursor.execute("SELECT * FROM holdings_summary ORDER BY symbol;")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)

    with st.container():
        st.subheader("📊 Portfolio Overview")

        tab1, tab2, tab3 = st.tabs(["📊 My Positions", "🥧 Portfolio Breakdown", "🧪 Placeholder"])

        with tab1:
            fig, ax = plt.subplots(figsize=(5, 5))
            bars = ax.bar(df["symbol"], df["market_value"], color="#4CAF50")
            ax.set_ylabel("Market Value ($)")
            ax.set_xlabel("Symbol")
            ax.set_title("My Positions")
            ax.bar_label(bars, fmt='%.0f', padding=3)
            st.pyplot(fig, use_container_width=False)
            st.markdown("<div style='height:550px; width:750px'></div>", unsafe_allow_html=True)

        with tab2:
            breakdown = df.groupby("security_type")["market_value"].sum()
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            ax2.pie(breakdown, labels=breakdown.index, autopct="%1.1f%%", startangle=90, textprops={"fontsize": 9})
            ax2.axis("equal")
            ax2.set_title("Portfolio Breakdown")
            st.pyplot(fig2, use_container_width=False)
            st.markdown("<div style='height:750px; width:750px'></div>", unsafe_allow_html=True)

        with tab3:
            st.info("This is a placeholder tab for future use.")

except Exception as e:
    st.error(f"❌ Database connection failed:\n{e}")