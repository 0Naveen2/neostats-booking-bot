import streamlit as st
from app.rag_pipeline import get_rag_response
from app.booking_flow import handle_booking_conversation

def route_query(user_input, vectorstore):
    state = st.session_state.booking_state
    user_text = user_input.lower()

    # --- 1. IF ALREADY IN BOOKING FLOW ---
    if state.get("booking_active"):
        return handle_booking_conversation(user_input)

    # --- 2. INTENT CONFIRMATION ---
    if state.get("awaiting_intent_confirmation"):
        if any(w in user_text for w in ["yes", "sure", "ok", "confirm", "yeah", "please"]):
            state["booking_active"] = True
            state["awaiting_intent_confirmation"] = False
            return handle_booking_conversation("START_FLOW") 
        else:
            state["awaiting_intent_confirmation"] = False
            return "Okay, I've cancelled that. What else can I help with?"

    # --- 3. DETECT NEW BOOKING INTENT (SMARTER) ---
    booking_keywords = ["book", "schedule", "reserve", "appointment"]
    
    # ❌ IGNORE questions like "how to book", "explain booking", "what is booking"
    informational_triggers = ["how", "explain", "what", "process", "workflow", "can you"]
    
    is_booking_keyword_present = any(k in user_text for k in booking_keywords)
    is_informational_question = any(q in user_text for q in informational_triggers)

    # Only trigger booking if it has a keyword AND it's NOT just asking "how"
    # Exception: "Can you book" is a request, but "How can you book" is a question.
    # We use a simple heuristic: if it says "book" but also "explain", it's likely RAG.
    
    if is_booking_keyword_present and not is_informational_question:
        state["awaiting_intent_confirmation"] = True
        return "It sounds like you want to make a booking. Would you like to proceed? (Yes/No)"
    
    # Explicit exception for "I want to book" (which contains 'what' sometimes in longer sentences, but we catch specific intent)
    if "i want to book" in user_text or "can you book" in user_text:
        state["awaiting_intent_confirmation"] = True
        return "It sounds like you want to make a booking. Would you like to proceed? (Yes/No)"

    # --- 4. GENERAL QUESTIONS / RAG ---
    return get_rag_response(user_input, vectorstore)