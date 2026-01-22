import streamlit as st
from app.rag_pipeline import get_rag_response
from app.booking_flow import handle_booking_conversation
from app.tools import search_web_for_services

def build_chat_context(chat_history, limit=20):
    """
    Builds short conversational memory for the LLM.
    Keeps last N messages to avoid token explosion.
    """
    history = chat_history[-limit:]
    context = ""

    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        context += f"{role}: {msg['content']}\n"

    return context


def route_query(user_input, vectorstore, chat_history):
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
            return get_rag_response(user_input, vectorstore)
            # state["awaiting_intent_confirmation"] = False
            # return "Okay, cancelled. What else can I help with?"

    # 3. WEB SEARCH
    search_keywords = ["search", "find", "show", "list", "available", "near me", "suggest", "looking for"]
    if any(k in user_text for k in search_keywords):
        with st.spinner(f"Searching Google for '{user_input}'..."):
            results = search_web_for_services(user_input)
        return f"🔎 **Here are the results:**\n\n{results}\n\n*To book one, just say 'I want to book [Name]'.*"

    # 4. BOOKING INTENT
    if any(k in user_text for k in ["book", "appointment", "reservation"]):
        state["awaiting_intent_confirmation"] = True
        return "It sounds like you want to make a booking. Shall we proceed? (Yes/No)"

    # 5. GENERAL CHAT / PDF RAG (WITH MEMORY)
    context = build_chat_context(chat_history)

    final_query = f"""
You are NeoStats Assistant.
Use the conversation history to answer naturally.

Conversation so far:
{context}

User: {user_input}
Assistant:
"""
    return get_rag_response(final_query, vectorstore)
