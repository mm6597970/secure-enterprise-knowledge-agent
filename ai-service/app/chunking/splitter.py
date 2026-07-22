from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_chunks(text: str, metadata: dict):
    # Clean text first
    lines = (line.strip() for line in text.splitlines())
    clean_text = '\n'.join(line for line in lines if line)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    docs = splitter.create_documents([clean_text], metadatas=[metadata])
    return docs
