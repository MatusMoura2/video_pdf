from fastapi import FastAPI, UploadFile, File, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import shutil
import os
import uuid
from pathlib import Path
from typing import Optional

from app.services.whisper_service import process_video_transcription

app = FastAPI(title="Video PDF Player API")

# Setup directories
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR.parent / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")

templates = Jinja2Templates(directory=BASE_DIR / "static")

# Dictionary to hold task statuses (for a production app, use Redis/Celery)
transcription_tasks = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/upload")
async def upload_files(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(None)
):
    """
    Upload video and start background transcription.
    """
    if not video:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")
        
    task_id = str(uuid.uuid4())
    video_filename = f"{task_id}_{video.filename}"
    video_path = STORAGE_DIR / video_filename
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
        
    # Start background task for long-running whisper process
    background_tasks.add_task(
        process_video_transcription, 
        video_path, 
        task_id, 
        transcription_tasks
    )
        
    return {
        "status": "started", 
        "task_id": task_id,
        "video_url": f"/storage/{video_filename}"
    }

@app.get("/api/transcribe/status/{task_id}")
async def get_transcription_status(task_id: str):
    """
    Poll this endpoint to get the status of the background transcription.
    """
    if task_id not in transcription_tasks:
        return {"status": "pending"}
    return transcription_tasks[task_id]

from app.services.pdf_export_service import generate_pdf_from_transcription

@app.get("/api/export/pdf/{task_id}")
async def export_pdf(task_id: str):
    """
    Generates and returns a PDF of the transcription.
    """
    try:
        pdf_path = generate_pdf_from_transcription(task_id)
        return FileResponse(
            path=pdf_path, 
            filename=f"transcricao_{task_id[:8]}.pdf",
            media_type="application/pdf"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcrição não encontrada.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
