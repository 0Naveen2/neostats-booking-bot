# 🌿 NeoStats AI Booking Assistant

An intelligent, hybrid AI assistant designed to handle service bookings and answer questions from uploaded documents (RAG). Built for the **AI Engineer Assessment**.

## 🚀 Live Demo

**[Insert Your Streamlit Cloud Link Here]** _(e.g., https://neostats-booking.streamlit.app)_

---

## 📋 Features

- **Hybrid Intent Detection:** Smartly distinguishes between general questions (RAG) and booking requests.
- **RAG Pipeline:** Upload PDF documents (e.g., service policies, job descriptions) and ask questions about them.
- **Conversational Booking:** Multi-turn dialogue to collect Name, Email, Phone, Date, and Time.
- **Validation:** Regex-based validation for Email, Phone, and Dates (rejects past dates/invalid formats).
- **Admin Dashboard:** Password-protected panel (`admin123`) to view and manage bookings.
- **Email Integration:** Sends real confirmation emails using SMTP.
- **NeoStats Branding:** Custom Green theme with Dark/Light mode support.

---

## 🛠️ Project Structure

```text
project_root/
├── app/
│   ├── main.py              # Application Entry Point & UI
│   ├── chat_logic.py        # Intent Router (Booking vs RAG)
│   ├── rag_pipeline.py      # PDF Processing & Hybrid Logic
│   ├── booking_flow.py      # State Machine for Slot Filling
│   ├── admin_dashboard.py   # Protected Admin Interface
│   ├── config.py            # Configuration & Constants
│   └── tools.py             # Email & Utility Functions
├── db/
│   ├── database.py          # SQLite Connection Manager
│   └── models.py            # Data Classes
├── .streamlit/
│   └── secrets.toml         # API Keys (Not uploaded to GitHub)
├── requirements.txt         # Project Dependencies
└── README.md                # Documentation

```
