import streamlit as st
import re
import random
from datetime import datetime
from app.config import REQUIRED_FIELDS, EMAIL_REGEX, PHONE_REGEX, TIME_REGEX
from app.tools import search_web_for_services, send_email  # Ensure send_email is imported
from db.database import save_booking_to_db

def validate_input(field, value):
    value = value.strip()
    if field == "email" and not re.match(EMAIL_REGEX, value): return False, "❌ Invalid email. Use format: name@example.com"
    if field == "phone" and not re.match(PHONE_REGEX, value): return False, "❌ Invalid phone. Use 10-15 digits."
    if field == "date":
        try: datetime.strptime(value, "%Y-%m-%d")
        except: return False, "❌ Invalid date. Use YYYY-MM-DD."
    if field == "time" and not re.match(TIME_REGEX, value): return False, "❌ Invalid time. Use HH:MM (24-hour)."
    
    # DYNAMIC SERVICE CHECK
    if field == "booking_type":
        pdf_services = st.session_state.get("detected_services", [])
        if pdf_services:
            if any(s.lower() in value.lower() for s in pdf_services):
                return True, value
            else:
                options = "\n".join([f"- {s}" for s in pdf_services])
                return False, f"Please choose a service from the document:\n{options}"
        return True, value # Accept anything if no PDF

    return True, value

def handle_booking_conversation(user_input):
    state = st.session_state.booking_state
    
    # 1. WEB SEARCH TRIGGER
    if "search" in user_input.lower() and not state.get("active"):
        results = search_web_for_services(user_input)
        return f"🔎 **Here is what I found:**\n\n{results}\n\n*To book one, just say 'I want to book [Name]'.*"

    # 2. VALIDATE CURRENT INPUT
    if state["current_field"]:
        is_valid, msg = validate_input(state["current_field"], user_input)
        if is_valid:
            state["data"][state["current_field"]] = msg
            state["current_field"] = None
        else:
            return msg

    # 3. ASK FOR NEXT FIELD
    for field in REQUIRED_FIELDS:
        if field not in state["data"]:
            state["current_field"] = field
            
            if field == "booking_type":
                pdf_services = st.session_state.get("detected_services", [])
                if pdf_services:
                    options = ", ".join(pdf_services[:5])
                    return f"Which service would you like to book? (From PDF: {options})"
                else:
                    return "What service or hotel are you booking? (Type the name)"
            
            return f"Please provide your **{field.capitalize()}**."

    # 4. CONFIRMATION
    if not state.get("confirmed"):
        summary = "\n".join([f"- {k.capitalize()}: {v}" for k,v in state["data"].items()])
        state["confirmed"] = True
        return f"Please confirm these details:\n\n{summary}\n\nType **'yes'** to save."
    
    # 5. SAVE & SEND EMAIL (THE FIX)
    if "yes" in user_input.lower():
        # A. Save to Database
        save_booking_to_db(state["data"])
        
        # B. Send Email (This was missing!)
        booking_id = f"BK-{random.randint(1000, 9999)}"
        email_status = send_email(state["data"]["email"], booking_id, state["data"])
        
        # C. Reset State
        st.session_state.booking_state = {"active": False, "data": {}, "current_field": None}
        
        # D. Return Result
        if email_status:
            return f"✅ **Booking Confirmed!**\n\n📧 A confirmation email has been sent to **{state['data']['email']}**.\nBooking ID: `{booking_id}`"
        else:
            return f"✅ **Booking Confirmed!**\n\n⚠️ However, the email failed to send. Please check the Admin Dashboard or Server Logs."
        
    return "❌ Booking cancelled."