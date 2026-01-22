# 🌿 NeoStats AI Booking Assistant

**NeoStats** is an intelligent, hybrid AI assistant designed to streamline service bookings. It combines **RAG (Retrieval-Augmented Generation)** for document-based queries and **Real-Time Web Search** (via Google) to find and book services dynamically.

## 🚀 Live Demo

https://booking-bot-neostats.streamlit.app/

---

## 🌟 Key Features

### 🧠 1. Hybrid Intelligence

- **Document Expert (RAG):** Upload a PDF (e.g., Rate Card, Hotel Brochure, Job Description), and the bot answers questions strictly from that document.
- **Web Agent (Google Search):** If no document is uploaded, the bot searches the live web (using Serper API) to find real-world services, hotels, salons, or doctors with prices and ratings.

### 📅 2. Smart Booking System

- **Intent Detection:** Automatically detects when a user wants to book (e.g., _"I want to book a haircut"_).
- **Data Collection:** Conversational flow to collect Name, Email, Phone, Date, and Time.
- **Dynamic Services:** Can book specific services extracted from a PDF or generic services found on the web.

### 📧 3. Automated Notifications

- **Email Confirmation:** Sends a real-time HTML email confirmation to the user immediately after booking.

### 🔒 4. Admin Dashboard

- **Secure Panel:** A password-protected dashboard for business owners to view, manage, and track all customer bookings.

### 🎨 5. Responsive UI

- **Mobile-Optimized:** Custom CSS ensures perfect visibility on both Desktop and Mobile (Light/Dark modes).

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **LLM:** Llama 3.1-8b (via [Groq API](https://groq.com/))
- **Search Engine:** Google Search API (via [Serper.dev](https://serper.dev/))
- **Vector Store:** FAISS & HuggingFace Embeddings (`all-MiniLM-L6-v2`)
- **Database:** SQLite (Lightweight, local storage)
- **Tools:** LangChain, Python `requests`, `smtplib`

---

## 📂 Project Structure

```text
neostats-booking-bot/
├── app/
│   ├── main.py              # 🚀 Entry Point (UI & Navigation)
│   ├── chat_logic.py        # 🧠 Brain: Routes queries (RAG vs Search vs Booking)
│   ├── rag_pipeline.py      # 📄 PDF Processing & Vector Search
│   ├── booking_flow.py      # 💬 Conversation State Machine for Booking
│   ├── tools.py             # 🛠️ Tools: Google Search & Email Sender
│   ├── admin_dashboard.py   # 🔒 Admin Panel UI
│   └── config.py            # ⚙️ Constants & Configuration
├── db/
│   ├── database.py          # 💾 SQLite Connection & Queries
│   └── bookings.db          # (Created automatically)
├── .streamlit/
│   └── secrets.toml         # 🔑 API Keys (DO NOT COMMIT THIS)
├── requirements.txt         # 📦 Project Dependencies
└── README.md                # 📖 This file
```
