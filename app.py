import streamlit as st
from PIL import Image

st.set_page_config(page_title=" Wealth Tracker", layout="centered")

# Load and display the image
image = Image.open("assets/logo.png")
st.image(image, use_container_width=True)

st.title("Track, plan, and grow—wisely.")
st.markdown("""Treviwise offers a clean dashboard for monitoring multi-currency portfolios, dividends, and exchange rates, along with personal finance tools for complete control.
            
**👉 Use the sidebar to navigate between pages.**
            
- 📊 Track your holdings and performance
- 🔎 Explore trades and positions
- 📈 Visualize your portfolio over time
- 🧾 Prepare for audits or taxes
- 💰 Monitor dividends and income

This app was born out of my own need for precise, audit-grade financial records. It pushed me to explore Python, PostgreSQL, API integration, and performance tuning in Streamlit. I continue to refine it as I learn more about financial modeling and app deployment.

""")