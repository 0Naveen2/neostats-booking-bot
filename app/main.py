import streamlit as st
import sys
import os

# Path Fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import APP_TITLE, APP_TAGLINE, BRAND_COLOR
from app.chat_logic import route_query
from app.rag_pipeline import process_pdf
from db.database import init_db
from app.admin_dashboard import render_admin_dashboard

# Page Config (IMPORTANT for mobile)
st.set_page_config(page_title="NeoStats", page_icon="🌿", layout="centered")

# Init DB
init_db()

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Welcome to **NeoStats**. How can I help you today?"
    }]

if "booking_state" not in st.session_state:
    st.session_state.booking_state = {
        "active": False,
        "data": {},
        "current_field": None
    }

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "page" not in st.session_state:
    st.session_state.page = "chat"

# ---------------- SIMPLE CSS ----------------
st.markdown("""
<style>

/* ===============================
   BULLETPROOF FILE UPLOADER FIX
   =============================== */

[data-testid="stFileUploader"] {
    background-color: #FFFFFF !important;
    border: 2px dashed #2F6B3F !important;
    border-radius: 14px !important;
    padding: 16px !important;
}

/* FORCE VISIBILITY OF ALL CHILD ELEMENTS */
[data-testid="stFileUploader"] * {
    color: #000000 !important;
    opacity: 1 !important;
    filter: none !important;
    visibility: visible !important;
}

/* INNER DROP ZONE */
[data-testid="stFileUploader"] section {
    background-color: #F5F7F9 !important;
    border-radius: 10px !important;
    padding: 14px !important;
}

/* BROWSE FILES BUTTON */
[data-testid="stFileUploader"] button {
    background-color: #2F6B3F !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    border: none !important;
}

/* MOBILE SAFETY */
@media (max-width: 768px) {
    [data-testid="stFileUploader"] {
        min-height: 130px !important;
    }
}

</style>
""", unsafe_allow_html=True)



# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown(f"## {APP_TITLE}")
    st.caption(APP_TAGLINE)
    st.divider()

    if st.button("💬 Chat", use_container_width=True):
        st.session_state.page = "chat"
        st.rerun()

    if st.button("🔒 Admin", use_container_width=True):
        st.session_state.page = "admin"
        st.rerun()
    
    # Only one file uploader
    uploaded_file = st.file_uploader("Upload Service PDF", type="pdf")
    if uploaded_file:
        if not st.session_state.get("vectorstore"):
            with st.spinner("Processing PDF..."):
                st.session_state.vectorstore = process_pdf(uploaded_file)
                st.success("PDF Loaded")
    else:
        # PDF removed → clear all PDF-related memory
        st.session_state.vectorstore = None
        st.session_state.detected_services = []

    st.divider()

# ---------------- ROUTING ----------------
if st.session_state.page == "admin":
    render_admin_dashboard()

else:
    st.markdown(f"<h1 style='color:{BRAND_COLOR}'>{APP_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(f"**{APP_TAGLINE}**")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = route_query(prompt,st.session_state.vectorstore,st.session_state.messages)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
