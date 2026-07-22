from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

def get_embeddings_model():
    # Groq does not provide embedding models, so we use a fast local open-source model
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
