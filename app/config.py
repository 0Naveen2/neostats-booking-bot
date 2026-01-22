import streamlit as st
import os
from datetime import time, datetime

# --- SECRETS ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except FileNotFoundError:
    st.error("Critical: .streamlit/secrets.toml file is missing.")
    st.stop()

# --- BRANDING ---
APP_TITLE = "NEOSTATS"
APP_TAGLINE = "Empowering Talent & Industry"
BRAND_COLOR = "#0E3B18"

# --- DATABASE ---
DB_NAME = "bookings.db"
DB_PATH = os.path.join("db", DB_NAME)

# --- LLM MODEL ---
LLM_MODEL = "llama-3.1-8b-instant"

# --- REQUIRED BOOKING FIELDS ---
REQUIRED_FIELDS = ["name", "email", "phone", "booking_type", "date", "time"]

# --- DEFAULT SERVICES ---
DEFAULT_SERVICES = ["General Inquiry"]

# --- REGEX VALIDATION ---
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_REGEX = r"^\+?[0-9]{10,15}$"
# Accepts 12-hour format with AM/PM
TIME_REGEX = r"^(0?[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM|am|pm)$"

# --- BUSINESS HOURS ---
OPEN_TIME = time(9, 0)    # 9:00 AM
CLOSE_TIME = time(18, 0)  # 6:00 PM

# --- UTILITY FUNCTIONS ---
def format_time_12hr(t: time):
    """Format a datetime.time object to 12-hour format."""
    return t.strftime("%I:%M %p")

def validate_future_date(input_date: str):
    """Check if date is today or in the future."""
    try:
        d = datetime.strptime(input_date, "%Y-%m-%d").date()
        if d < datetime.today().date():
            return False, "❌ Date cannot be in the past."
        return True, d
    except:
        return False, "❌ Invalid date. Use YYYY-MM-DD."
