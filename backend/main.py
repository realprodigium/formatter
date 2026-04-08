from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
import uuid
import os
from pathlib import Path
import time

from processor import BankProcessor
from security import encrypt_data, decrypt_data

app = FastAPI(title="BankFlow API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories for temporary storage
BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "secure_storage"
STORAGE_DIR.mkdir(exist_ok=True)

def cleanup_file(file_path: Path):
    """Wait for 10 minutes and delete the file."""
    time.sleep(600)  
    if file_path.exists():
        os.remove(file_path)

@app.post("/api/process")
async def process_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format. Only Excel files allowed.")
    
    try:
        # Read content
        content = await file.read()
        
        # Process the excel
        processed_content = BankProcessor.process_excel(content)
        
        # We can still encrypt/decrypt for a "secure system" log or transit
        # but for direct response, we return the decrypted content
        # Note: In a real "secure" system, we might want to encrypt before sending,
        # but the frontend needs to handle that. Here we rely on HTTPS for transit security.
        
        return Response(
            content=processed_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": 'attachment; filename="data_procesada.xlsx"'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{file_id}")
async def download_file(file_id: str):
    file_path = STORAGE_DIR / f"{file_id}.enc"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found or link expired.")
    
    try:
        with open(file_path, "rb") as f:
            encrypted_content = f.read()
            
        # Decrypt
        decrypted_content = decrypt_data(encrypted_content)
        
        return Response(
            content=decrypted_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="processed_statement.xlsx"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decrypting file: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
