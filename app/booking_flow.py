import streamlit as st
import re
from datetime import datetime
from app.config import REQUIRED_FIELDS, EMAIL_REGEX, PHONE_REGEX, TIME_REGEX, SERVICE_TYPES
from app.tools import send_email
from db.database import save_booking_to_db

def validate_input(field, value):
    value = value.strip()
    
    # 1. Email Validation
    if field == "email" and not re.match(EMAIL_REGEX, value):
        return False, "❌ Invalid email format."
    
    # 2. Phone Validation
    if field == "phone" and not re.match(PHONE_REGEX, value):
        return False, "❌ Invalid phone (10-15 digits)."
    
    # 3. Date Validation (Real Calendar Check)
    if field == "date":
        try:
            # Tries to convert to a real date object. Fails if Month is 21.
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return False, "❌ Invalid date. Please use YYYY-MM-DD (e.g., 2024-01-30)."

    # 4. Time Validation
    if field == "time" and not re.match(TIME_REGEX, value):
        return False, "❌ Invalid time. Use HH:MM."

    # 5. Booking Type Validation (The Fix for your error)
    if field == "booking_type":
        # Check if user input roughly matches one of our services
        # or if it looks like a question
        if "?" in value or value.lower() in ["what", "list", "options", "help"]:
             services_list = "\n".join([f"- {s}" for s in SERVICE_TYPES])
             return False, f"Here are the available services:\n\n{services_list}\n\nPlease type one of the above."
        
        # Exact/Fuzzy match check
        valid_match = next((s for s in SERVICE_TYPES if s.lower() in value.lower()), None)
        if valid_match:
            return True, valid_match # Save the clean name (e.g. "Technical Interview")
        else:
            return False, "❌ Unknown service. Please choose from: " + ", ".join(SERVICE_TYPES)

    return True, value

def handle_booking_conversation(user_input):
    state = st.session_state.booking_state

    # 1. PROCESS PREVIOUS INPUT
    # (We skip this if the input was just "Yes" to start the flow)
    if state["current_field"]:
        is_valid, msg = validate_input(state["current_field"], user_input)
        if is_valid:
            state["data"][state["current_field"]] = msg
            state["current_field"] = None
        else:
            return f"{msg}"

    # 2. ASK NEXT MISSING FIELD
    for field in REQUIRED_FIELDS:
        if field not in state["data"]:
            state["current_field"] = field
            clean_name = field.replace('_', ' ').capitalize()
            
            # Custom Prompts
            if field == "date": return "Please enter the **Date** (YYYY-MM-DD)."
            if field == "time": return "Please enter the **Time** (HH:MM)."
            if field == "booking_type": 
                 # List services immediately to help the user
                 options = ", ".join(SERVICE_TYPES)
                 return f"What service would you like to book?\n(Options: {options})"
            
            return f"Please provide your **{clean_name}**."

    # 3. CONFIRMATION
    if not state.get("waiting_for_final_confirmation"):
        summary = "\n".join([f"- **{k.capitalize()}**: {v}" for k, v in state["data"].items()])
        state["waiting_for_final_confirmation"] = True
        return f"Please confirm details:\n\n{summary}\n\nType **'yes'** to book."

    # 4. FINALIZE
    if state.get("waiting_for_final_confirmation"):
        if "yes" in user_input.lower():
            booking_id = save_booking_to_db(state["data"])
            if booking_id:
                send_email(state["data"]["email"], booking_id, state["data"])
                st.session_state.booking_state = {"booking_active": False, "data": {}, "current_field": None}
                return f"✅ Booking #{booking_id} Confirmed! Email sent."
        else:
            st.session_state.booking_state = {"booking_active": False, "data": {}, "current_field": None}
            return "❌ Booking cancelled."

    return "Error. Resetting."