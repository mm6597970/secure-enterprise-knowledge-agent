import os
from app.loaders.pdf_loader import load_pdf
from app.loaders.docx_loader import load_docx
from app.chunking.splitter import get_chunks
from app.vectordb.chroma import add_documents_to_db, get_vector_store
from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

def process_document(upload_dir: str):
    processed_files = []
    docs_to_add = []
    
    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        text = ""
        
        if filename.endswith('.pdf'):
            text = load_pdf(file_path)
        elif filename.endswith('.docx'):
            text = load_docx(file_path)
        elif filename.endswith('.txt'):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            continue
            
        if text:
            metadata = {"source": filename}
            chunks = get_chunks(text, metadata)
            docs_to_add.extend(chunks)
            processed_files.append(filename)
            
    if docs_to_add:
        add_documents_to_db(docs_to_add)
        
    return processed_files

def answer_question(question: str, user: dict = None):
    # 1. Input Guardrails (Prompt Injection / Malicious Inputs)
    lower_q = question.lower()
    blocked_keywords = ["ignore", "override", "bypass", "jailbreak", "confidential"]
    if any(word in lower_q for word in blocked_keywords):
        return "Blocked: Input violates security guardrails."

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is not set in the environment. Please add it to your .env file.")
        
    llm = ChatGroq(model_name="llama-3.1-8b-instant", groq_api_key=api_key)
    
    vector_store = get_vector_store()
    
    # 2. Secure RAG Retrieval (RBAC)
    search_kwargs = {"k": 5}
    if user and user.get("role"):
        role = user.get("role")
        # In a complete implementation, this filter would match the document's required_role.
        # For simplicity, if they aren't CEO or HR or Manager, we enforce a filter
        if role not in ["CEO", "Manager", "HR"]:
            search_kwargs["filter"] = {"role": role}
            
    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
    
    system_prompt = (
        "You are an AI assistant for a company. Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know. Use three sentences maximum and keep the answer concise.\n\n"
        "{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    response = rag_chain.invoke({"input": question})
    answer = response.get("answer", "")
    
    # 3. Output Guardrails
    if not answer or answer.strip() == "":
        return "Information not found."
    
    # Basic hallucination check (e.g. refusing if too generic)
    if "i don't know" in answer.lower():
        return "Information not found."
        
    return answer
