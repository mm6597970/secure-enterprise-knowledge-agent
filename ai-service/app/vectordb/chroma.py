from langchain_community.vectorstores import Chroma
from app.embeddings.embedding import get_embeddings_model
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

def get_vector_store():
    embeddings = get_embeddings_model()
    return Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)

def add_documents_to_db(docs):
    vector_store = get_vector_store()
    vector_store.add_documents(docs)
    vector_store.persist()
