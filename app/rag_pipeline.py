from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq
from app.config import GROQ_API_KEY, LLM_MODEL
import streamlit as st

client = Groq(api_key=GROQ_API_KEY)

def process_pdf(uploaded_file):
    if not uploaded_file: return None
    
    with open("temp_policy.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    loader = PyPDFLoader("temp_policy.pdf")
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Auto-Extract Services
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
        clean_services = [s.strip('- "[]') for s in services_text.split(',')]
        st.session_state.detected_services = clean_services
    except:
        st.session_state.detected_services = []

    return vectorstore

def get_rag_response(query, vectorstore):
    available_services = st.session_state.get("detected_services", [])
    services_str = ", ".join(available_services) if available_services else "General Services"

    # SCENARIO 1: NO PDF (General Chat)
    if vectorstore is None:
        try:
            # Be helpful, don't just say "I can search".
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are NeoStats. You help users find and book services. If they ask to search, you will do it."},
                    {"role": "user", "content": query}
                ],
                temperature=0.7 
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    # SCENARIO 2: PDF MODE
    docs = vectorstore.similarity_search(query, k=5)
    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
    You are the NeoStats Assistant.
    Context from PDF: {context}
    Available Services: {services_str}
    User Question: {query}
    
    Answer based on the PDF. If the user wants to book, guide them to use one of the Available Services.
    """
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content