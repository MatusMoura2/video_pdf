from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import shutil
import os
import uuid
from pathlib import Path
from typing import Optional

app = FastAPI(title="Video PDF Player API")

# Setup directories
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR.parent / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Expose storage for media access (files will be streamed manually for video)
# For PDF, we can use static file serving
app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")

templates = Jinja2Templates(directory=BASE_DIR / "static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload_files(
    video: UploadFile = File(None),
    pdf: UploadFile = File(None)
):
    """
    Upload video and/or pdf files and save them to storage.
    """
    files_saved = {}
    
    if video:
        video_filename = f"{uuid.uuid4()}_{video.filename}"
        video_path = STORAGE_DIR / video_filename
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        files_saved['video'] = f"/storage/{video_filename}"
        
    if pdf:
        pdf_filename = f"{uuid.uuid4()}_{pdf.filename}"
        pdf_path = STORAGE_DIR / pdf_filename
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(pdf.file, buffer)
        files_saved['pdf'] = f"/storage/{pdf_filename}"
        
    if not files_saved:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")
        
    return {"status": "success", "files": files_saved}
