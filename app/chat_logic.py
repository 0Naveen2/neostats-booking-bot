import streamlit as st
from app.rag_pipeline import get_rag_response
from app.booking_flow import handle_booking_conversation
from app.tools import search_web_for_services

def route_query(user_input, vectorstore):
    state = st.session_state.booking_state
    user_text = user_input.lower()

    # 1. BOOKING FLOW (Priority)
    if state.get("active"):
        return handle_booking_conversation(user_input)

    # 2. CONFIRMATION HANDLING
    if state.get("awaiting_intent_confirmation"):
        if any(w in user_text for w in ["yes", "sure", "ok", "confirm", "proceed"]):
            state["active"] = True
            state["awaiting_intent_confirmation"] = False
            return handle_booking_conversation("START_FLOW") 
        else:
            state["awaiting_intent_confirmation"] = False
            return "Okay, cancelled. What else can I help with?"

    # 3. WEB SEARCH TRIGGER (Broadened)
    # Now triggers for ANY search request, not just hotels.
    search_keywords = ["search", "find", "show", "list", "available", "near me", "suggest", "looking for"]
    
    # Check if user wants to search
    if any(k in user_text for k in search_keywords):
        # We assume if they say "search" or "find", they want real data.
        with st.spinner(f"Searching Google for '{user_input}'..."):
            results = search_web_for_services(user_input)
        return f"🔎 **Here are the results:**\n\n{results}\n\n*To book one, just say 'I want to book [Name]'.*"

    # 4. BOOKING INTENT
    # Triggers if they say "book" without a prior search
    if "book" in user_text or "appointment" in user_text or "reservation" in user_text:
        state["awaiting_intent_confirmation"] = True
        return "It sounds like you want to make a booking. Shall we proceed? (Yes/No)"

    # 5. GENERAL CHAT / PDF RAG
    return get_rag_response(user_input, vectorstore)