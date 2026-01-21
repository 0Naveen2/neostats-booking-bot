from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq
from app.config import GROQ_API_KEY, LLM_MODEL, SERVICE_TYPES

client = Groq(api_key=GROQ_API_KEY)

def process_pdf(uploaded_file):
    if not uploaded_file: return None
    
    # Save temp file
    with open("temp_policy.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    loader = PyPDFLoader("temp_policy.pdf")
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore

def get_rag_response(query, vectorstore):
    # Format services as a string to give the AI context about itself
    services_str = ", ".join(SERVICE_TYPES)

    # --- SCENARIO 1: NO PDF UPLOADED ---
    # It relies purely on its identity as the NeoStats Booking Bot
    if vectorstore is None:
        try:
            system_msg = f"""
            You are the NeoStats AI Booking Assistant.
            Your goal is to help users with:
            1. Answering questions about our services.
            2. Guiding them to book an appointment.
            
            Our Available Services: {services_str}.
            """
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": query}
                ],
                temperature=0.7 
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    # --- SCENARIO 2: PDF UPLOADED (HYBRID MODE) ---
    # Retrieve relevant chunks from PDF
    docs = vectorstore.similarity_search(query, k=5)
    context = "\n\n".join(doc.page_content for doc in docs)

    # The Prompt now combines PDF Context + Business Knowledge
    prompt = f"""
    You are the NeoStats AI Assistant. You have two sources of knowledge:
    1. The context from the uploaded PDF document (provided below).
    2. Your built-in knowledge that you offer these specific booking services: {services_str}.

    INSTRUCTIONS:
    - If the user asks about the **PDF content** (e.g., "Summarize the file", "What is the job description?"), answer using the PDF Context.
    - If the user asks about **booking services** (e.g., "What services do you have?", "I want to book"), IGNORE the PDF and list the "Available Services" mentioned above.
    - If the answer is in neither, apologize politely.

    PDF CONTEXT:
    {context}
    
    USER QUESTION:
    {query}
    """

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3 # Balanced creativity
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"