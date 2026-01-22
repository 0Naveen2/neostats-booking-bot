import streamlit as st
import re
import random
from datetime import datetime, date, time as dt_time
from app.config import REQUIRED_FIELDS, EMAIL_REGEX, PHONE_REGEX, TIME_REGEX, OPEN_TIME, CLOSE_TIME
from app.tools import search_web_for_services, send_email
from db.database import save_booking_to_db


def validate_input(field, value):
    """Validate user input for each booking field."""
    value = value.strip()

    # --- EMAIL ---
    if field == "email" and not re.match(EMAIL_REGEX, value):
        return False, "❌ Invalid email. Use format: name@example.com"

    # --- PHONE ---
    if field == "phone" and not re.match(PHONE_REGEX, value):
        return False, "❌ Invalid phone. Use 10-15 digits."

    # --- DATE ---
    if field == "date":
        try:
            booking_date = datetime.strptime(value, "%Y-%m-%d").date()
            if booking_date < date.today():
                return False, "❌ Date cannot be in the past."
        except:
            return False, "❌ Invalid date. Use YYYY-MM-DD."

    # --- TIME ---
    if field == "time":
        parsed_time = None
        for fmt in ("%H:%M", "%I:%M %p"):
            try:
                parsed_time = datetime.strptime(value, fmt).time()
                break
            except:
                continue
        if not parsed_time:
            return False, "❌ Invalid time. Use HH:MM (24-hour) or HH:MM AM/PM."

        # Check business hours
        if parsed_time < OPEN_TIME or parsed_time > CLOSE_TIME:
            return False, f"❌ Booking time must be within business hours: {OPEN_TIME.strftime('%I:%M %p')} - {CLOSE_TIME.strftime('%I:%M %p')}"
        value = parsed_time.strftime("%I:%M %p")

    # --- BOOKING TYPE (PDF Matching) ---
    if field == "booking_type":
        pdf_services = st.session_state.get("detected_services", [])
        if pdf_services:
            # Partial / case-insensitive match
            matched_service = next((s for s in pdf_services if value.lower() in s.lower()), None)
            if matched_service:
                return True, matched_service
            else:
                options = "\n".join([f"- {s}" for s in pdf_services])
                return False, f"Service not found in PDF. Available services:\n{options}\n\nYou can also type 'search [service]' to find online options."
        return True, value  # Accept anything if no PDF

    return True, value


def handle_booking_conversation(user_input):
    """Step-by-step booking conversation handler."""
    state = st.session_state.booking_state

    # --- WEB SEARCH ---
    if "search" in user_input.lower() and not state.get("active"):
        results = search_web_for_services(user_input)
        return f"🔎 **Here is what I found:**\n\n{results}\n\n*To book one, just say 'I want to book [Name]'.*"

    # --- VALIDATE CURRENT INPUT ---
    if state["current_field"]:
        is_valid, msg = validate_input(state["current_field"], user_input)
        if is_valid:
            state["data"][state["current_field"]] = msg
            state["current_field"] = None
        else:
            return msg

    # --- ASK NEXT FIELD ---
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

    # --- CONFIRMATION ---
    if not state.get("confirmed"):
        summary = "\n".join([f"- {k.capitalize()}: {v}" for k, v in state["data"].items()])
        state["confirmed"] = True
        return f"Please confirm these details:\n\n{summary}\n\nType **'yes'** to save."

    # --- SAVE & SEND EMAIL ---
    if "yes" in user_input.lower():
        # Save to Database
        save_booking_to_db(state["data"])

        # Send Email
        booking_id = f"BK-{random.randint(1000, 9999)}"
        email_status = send_email(state["data"]["email"], booking_id, state["data"])

        # Reset State
        st.session_state.booking_state = {"active": False, "data": {}, "current_field": None}

        # Return Result
        if email_status:
            return f"✅ **Booking Confirmed!**\n\n📧 Confirmation email sent to **{state['data']['email']}**.\nBooking ID: `{booking_id}`"
        else:
            return f"✅ **Booking Confirmed!**\n\n⚠️ Email failed to send. Check Admin Dashboard."

    return "❌ Booking cancelled."
