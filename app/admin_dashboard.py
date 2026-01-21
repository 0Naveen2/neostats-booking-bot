import streamlit as st
import pandas as pd
from db.database import fetch_all_bookings
from app.config import BRAND_COLOR, ADMIN_PASSWORD

def render_admin_dashboard():
    # Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"<h1 style='color:{BRAND_COLOR}'>Admin Dashboard</h1>", unsafe_allow_html=True)
    with col2:
        if st.button("⬅️ Back"):
            st.session_state.page = "chat"
            st.rerun()

    # Security Check
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        st.warning("🔒 Restricted Access")
        password = st.text_input("Enter Admin Password", type="password")
        
        if st.button("Login"):
            # CHECK AGAINST SECURE CONFIG, NOT HARDCODED STRING
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.success("Access Granted")
                st.rerun()
            else:
                st.error("Incorrect Password")
        return

    # Dashboard Content
    st.markdown("### 📅 All Bookings")
    if st.button("🔄 Refresh Data"):
        st.rerun()
        
    data = fetch_all_bookings()
    if data:
        df = pd.DataFrame(data, columns=["ID", "Name", "Email", "Service Type", "Date", "Time", "Status"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No bookings found.")
    
    st.divider()
    if st.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()