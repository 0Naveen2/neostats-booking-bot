from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq
from app.config import GROQ_API_KEY, LLM_MODEL
import streamlit as st

client = Groq(api_key=GROQ_API_KEY)

# --- Process PDF ---
def process_pdf(uploaded_file):
    if not uploaded_file: 
        return None
    
    with open("temp_policy.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    loader = PyPDFLoader("temp_policy.pdf")
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Extract services from PDF
    full_text = " ".join([doc.page_content for doc in documents[:5]]) 
    extract_prompt = f"""
    Analyze the text below and list the specific services, doctors, or booking options available.
    Return ONLY a python list of strings. Example: ["Dr. Smith", "Deluxe Room"]
    Text: {full_text[:3000]}
    """
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": extract_prompt}],
            temperature=0
        )
        services_text = response.choices[0].message.content
        # CLEAN SERVICES
        clean_services = [s.strip(" -[]'\"") for s in services_text.split(",") if s.strip()]
        st.session_state.detected_services = clean_services
    except:
        st.session_state.detected_services = []

    return vectorstore


# --- Intent Classification ---
def classify_intent(query):
    booking_keywords = ["book", "reserve", "appointment", "schedule"]
    info_keywords = ["services", "available", "options", "pricing", "details"]

    query_lower = query.lower()
    if any(word in query_lower for word in booking_keywords):
        return "booking"
    elif any(word in query_lower for word in info_keywords):
        return "info"
    else:
        return "general"


# --- RAG + Response Handling ---
def get_rag_response(query, vectorstore=None):
    intent = classify_intent(query)

    # --- PDF Uploaded Mode ---
    if vectorstore is not None:
        # 1️⃣ Booking Intent → list PDF services
        if intent == "booking":
            services = st.session_state.get("detected_services", [])
            if services:
                return (
                    f"Based on the PDF, you can book: {', '.join(services)}.\n"
                    f"Example: 'I want to book Deluxe Room Booking'."
                )
            else:
                return "I see a PDF, but no services were detected. Please try another query."
        
        # 2️⃣ Info Intent → RAG from PDF
        docs = vectorstore.similarity_search(query, k=5)
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = f"""
        You are NeoStats Assistant.
        Context from PDF: {context}
        User Question: {query}
        Answer ONLY based on the PDF.
        """
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content

    # --- No PDF Uploaded Mode ---
    else:
        # Allow general search
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": query}],
            temperature=0.7
        )
        return response.choices[0].message.content
