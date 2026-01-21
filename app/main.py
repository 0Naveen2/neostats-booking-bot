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
        "booking_active": False,
        "data": {},
        "current_field": None
    }

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "page" not in st.session_state:
    st.session_state.page = "chat"

# ---------------- SIMPLE CSS ----------------
st.markdown(f"""
<style>
.stApp {{
    background-color: #F7F9FB;
}}

[data-testid="stSidebar"] {{
    background-color: {BRAND_COLOR};
}}

[data-testid="stSidebar"] * {{
    color: white !important;
}}

.stChatMessage {{
    border-radius: 12px;
    padding: 12px;
}}

.stChatMessage[data-testid="stChatMessage-user"] {{
    background-color: #E6F4EA;
}}

.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background-color: #FFFFFF;
}}

.stChatMessage p {{
    color: #000000 !important;
}}

.stChatInputContainer {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 1px solid #ddd;
}}

.stButton > button {{
    background-color: {BRAND_COLOR};
    color: white;
    border-radius: 8px;
}}
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

    st.divider()

    if st.session_state.page == "chat":
        uploaded_file = st.file_uploader("Upload Service PDF", type="pdf")
        if uploaded_file and not st.session_state.vectorstore:
            with st.spinner("Processing PDF..."):
                st.session_state.vectorstore = process_pdf(uploaded_file)
                st.success("PDF Loaded")

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
            response = route_query(prompt, st.session_state.vectorstore)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
