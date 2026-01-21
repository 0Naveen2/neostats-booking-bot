import smtplib
import requests
import json
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import EMAIL_SENDER, EMAIL_PASSWORD

# --- GOOGLE SEARCH TOOL (Powered by Serper.dev) ---
def search_web_for_services(query):
    """
    Searches Google using Serper.dev API.
    Returns real restaurants, hotels, and services.
    """
    # 1. Get Key
    try:
        api_key = st.secrets["SERPER_API_KEY"]
    except:
        return "❌ Error: Missing 'SERPER_API_KEY' in secrets.toml. Please get one from serper.dev."

    # 2. Call API
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": f"{query} price booking",
        "num": 5  # Get top 5 results
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        
        results_list = []
        
        # 3. Parse 'Organic' Results (Standard Web Links)
        if "organic" in data:
            for item in data["organic"]:
                title = item.get("title", "No Title")
                link = item.get("link", "#")
                snippet = item.get("snippet", "No details available.")
                results_list.append(f"🔹 **{title}**\n   {snippet}\n   [View Website]({link})")
        
        # 4. Parse 'Places' (Maps/Restaurants) - GREAT for "Restaurants in Bangalore"
        if "places" in data:
            for item in data["places"]:
                title = item.get("title", "No Title")
                address = item.get("address", "No address")
                rating = item.get("rating", "N/A")
                results_list.append(f"📍 **{title}** (⭐ {rating})\n   Address: {address}")

        if not results_list:
            return "⚠️ No relevant results found."

        return "\n\n".join(results_list[:5])

    except Exception as e:
        return f"❌ Search API Error: {e}"

# --- EMAIL TOOL ---
def send_email(to_email, booking_id, details):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = f"Booking Confirmation #{booking_id}"
        
        body = f"""
        Booking Confirmed!
        ID: {booking_id}
        Service: {details.get('booking_type')}
        Date: {details.get('date')}
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False