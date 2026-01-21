import streamlit as st
import os

# --- Secrets ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    EMAIL_SENDER = st.secrets["EMAIL_SENDER"]
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"] # Load Securely
except FileNotFoundError:
    st.error("Critical: .streamlit/secrets.toml file is missing.")
    st.stop()

# --- NEOSTATS BRANDING ---
APP_TITLE = "NEOSTATS"
APP_TAGLINE = "Empowering Talent & Industry"
BRAND_COLOR = "#103918"

DB_NAME = "bookings.db"
DB_PATH = os.path.join("db", DB_NAME)

# --- AI Models ---
LLM_MODEL = "llama-3.1-8b-instant" 

# --- Booking Settings ---
REQUIRED_FIELDS = ["name", "email", "phone", "booking_type", "date", "time"]

SERVICE_TYPES = [
    "General Appointment",
    "Doctor Consultation", 
    "Salon/Spa Service", 
    "Technical Interview", 
    "Event Reservation", 
    "Customer Support Call"
]

# --- Validation ---
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_REGEX = r"^\+?[0-9]{10,15}$"
TIME_REGEX = r"^\d{2}:\d{2}$"