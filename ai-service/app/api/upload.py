from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
from app.services.rag_service import process_document

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_docs")

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.docx', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"message": "File uploaded successfully", "filename": file.filename}

@router.post("/process")
async def process_documents():
    try:
        processed_files = process_document(UPLOAD_DIR)
        return {"message": "Documents processed successfully", "files": processed_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
