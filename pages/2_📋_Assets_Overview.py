import streamlit as st
import pandas as pd
import psycopg2

st.set_page_config(page_title="🏦 Assets Overview", layout="wide")
st.title("🏦 Assets Table")

# Database connection (assumes you're using .streamlit/secrets.toml)
try:
    conn = psycopg2.connect(
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        dbname=st.secrets["database"]["name"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"],
        sslmode=st.secrets["database"].get("sslmode", "require")
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets ORDER BY last_updated DESC;")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)

    st.dataframe(df, use_container_width=True)

    # Totals and quick stats
    if "value" in df.columns:
        total_value = df["value"].sum()
        st.markdown(f"### 💰 Total Asset Value: **{total_value:,.2f}**")

except Exception as e:
    st.error(f"❌ Could not connect to database: {e}")