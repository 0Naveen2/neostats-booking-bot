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

# 1. Page Config
st.set_page_config(page_title="NeoStats", page_icon="🌿", layout="wide")

# 2. Init DB
init_db()

# 3. Session State Init
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to **NeoStats**. I can help you book services or answer questions about our offerings."}]
if "booking_state" not in st.session_state:
    st.session_state.booking_state = {"booking_active": False, "data": {}, "current_field": None}
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "page" not in st.session_state:
    st.session_state.page = "chat" 

# 4. CUSTOM CSS (FIXED VISIBILITY)
st.markdown(f"""
    <style>
    /* Main Background */
    .stApp {{
        background-color: #FAFAFA;
    }}
    
    /* Sidebar Background & Text */
    [data-testid="stSidebar"] {{
        background-color: {BRAND_COLOR};
    }}
    [data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}
    
    /* Chat Bubbles - Fix Text Color */
    .stChatMessage {{
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
    }}
    
    /* FORCE TEXT COLOR TO BLACK INSIDE CHAT */
    .stChatMessage p, .stChatMessage div {{
        color: #000000 !important;
    }}
    
    /* Input Box */
    .stChatInputContainer textarea {{
        color: #000000 !important; 
        background-color: #FFFFFF !important;
    }}
    
    /* Buttons */
    .stButton>button {{
        background-color: {BRAND_COLOR} !important;
        color: white !important;
        border: none;
    }}
    </style>
""", unsafe_allow_html=True)

# 5. SIDEBAR
with st.sidebar:
    st.markdown(f"## {APP_TITLE}")
    st.caption(APP_TAGLINE)
    st.divider()
    
    if st.button("💬 Chat Agent", use_container_width=True):
        st.session_state.page = "chat"
        st.rerun()
        
    if st.button("🔒 Admin Panel", use_container_width=True):
        st.session_state.page = "admin"
        st.rerun()
    
    st.divider()
    
    if st.session_state.page == "chat":
        uploaded_file = st.file_uploader("Upload Service PDF", type="pdf")
        if uploaded_file and not st.session_state.vectorstore:
            with st.spinner("Analyzing NeoStats services..."):
                st.session_state.vectorstore = process_pdf(uploaded_file)
                st.success("Services Loaded")

# 6. ROUTING
if st.session_state.page == "admin":
    render_admin_dashboard()
else:
    # Header
    st.markdown(f"<h1 style='color:{BRAND_COLOR}'>{APP_TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(f"**{APP_TAGLINE}**")

    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("How can I assist you today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = route_query(prompt, st.session_state.vectorstore)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})