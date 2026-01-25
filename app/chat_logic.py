import streamlit as st
from app.rag_pipeline import get_rag_response
from app.booking_flow import handle_booking_conversation
from app.tools import search_web_for_services
from groq import Groq
from app.config import LLM_MODEL

def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def detect_intent_with_ai(user_input):
    """
    Asks the LLM to decide if the user wants to book something.
    Returns: 'BOOKING', 'SEARCH', or 'CHAT'
    """
    client = get_client()
    prompt = f"""
    Classify the user's intent based on this message: "{user_input}"
    
    1. BOOKING: If the user wants to schedule, reserve, or book something (e.g., "Book a room", "I want an appointment", "Can you get me a slot?", "Reserve the deluxe room").
    2. SEARCH: If the user is asking to find/look for/search for places (e.g., "Find hotels", "Search for salons").
    3. CHAT: If the user is asking a question or just chatting (e.g., "What is the price?", "Is the gym open?", "Hello").
    
    Return ONLY one word: BOOKING, SEARCH, or CHAT.
    """
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip().upper()
    except:
        return "CHAT"

def route_query(user_input, vectorstore, chat_history):
    state = st.session_state.booking_state
    
    # 1. IF ALREADY BOOKING -> CONTINUE
    if state.get("active"):
        return handle_booking_conversation(user_input)

    # 2. IF WAITING FOR CONFIRMATION -> HANDLE YES/NO
    if state.get("awaiting_intent_confirmation"):
        if any(w in user_input.lower() for w in ["yes", "sure", "ok", "please", "go ahead"]):
            state["active"] = True
            state["awaiting_intent_confirmation"] = False
            return handle_booking_conversation("START_FLOW") 
        else:
            state["awaiting_intent_confirmation"] = False

    # 3. ASK AI: WHAT DOES THE USER WANT?
    intent = detect_intent_with_ai(user_input)
    
    if intent == "SEARCH":
        with st.spinner(f"Searching web for '{user_input}'..."):
            results = search_web_for_services(user_input)
        # FIX: Explicit instruction here too
        return f"🔎 **Web Results:**\n\n{results}\n\n👉 *To book any of these, just type: 'I want to book [Name]'*"

    if intent == "BOOKING":
        pdf_services = st.session_state.get("detected_services", [])
        
        if pdf_services:
            return f"I can definitely help with that. I found these options: **{', '.join(pdf_services)}**.\n\n👉 *Which one would you like? (You can say 'Book [Service Name]')*"
        else:
            state["active"] = True
            return handle_booking_conversation("START_FLOW")

    # 4. GENERAL CHAT (Default)
    return get_rag_response(user_input, vectorstore)