from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq
from app.config import LLM_MODEL
import streamlit as st
import ast

def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def process_pdf(uploaded_file):
    if not uploaded_file: return None
    
    with open("temp_doc.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    loader = PyPDFLoader("temp_doc.pdf")
    documents = loader.load()
    
    # Store full text
    if len(documents) < 20:
        st.session_state.pdf_full_text = "\n\n".join([doc.page_content for doc in documents])
    else:
        st.session_state.pdf_full_text = None

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Extract Services (Best Effort)
    full_text = " ".join([doc.page_content for doc in documents[:10]]) 
    extract_prompt = f"""
    List any bookable services (rooms, appointments, treatments) found in this text as a Python list.
    Example: ["Deluxe Room", "Consultation"]
    If none, return [].
    Text: {full_text[:3000]}
    """
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": extract_prompt}],
            temperature=0
        )
        content = response.choices[0].message.content
        if "[" in content and "]" in content:
            list_str = content[content.find("["):content.rfind("]")+1]
            st.session_state.detected_services = ast.literal_eval(list_str)
        else:
            st.session_state.detected_services = []
    except:
        st.session_state.detected_services = []

    return vectorstore

def get_rag_response(query, vectorstore=None):
    if vectorstore is None:
        return "I can search the web for that. What do you need?"

    if st.session_state.get("pdf_full_text"):
        context = st.session_state.pdf_full_text
    else:
        docs = vectorstore.similarity_search(query, k=5)
        context = "\n\n".join(doc.page_content for doc in docs)

    # --- THE FIX: MANDATORY INSTRUCTION IN PROMPT ---
    role = """
    You are a helpful AI Booking Assistant.
    1. Answer the user's question based on the text.
    2. If the user asks about services, rooms, or doctors, describe them.
    3. CRITICAL: Whenever you mention a service, YOU MUST add this instruction at the end: 
       "To book this, simply type: 'I want to book [Service Name]'."
    4. Never refuse a booking request.
    """
    
    prompt = f"""
    {role}
    
    Context:
    {context}
    
    User Question: {query}
    """
    
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"