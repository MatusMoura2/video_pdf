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
from app.services.download_service import download_video_from_url

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

class URLUploadRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

def background_download_and_transcribe(url: str, video_path: Path, task_id: str, status_dict: dict):
    try:
        status_dict[task_id] = {"status": "processing", "progress": "Baixando vídeo da URL..."}
        download_video_from_url(url, video_path)
        # Proceed to transcription now that download is complete
        process_video_transcription(video_path, task_id, status_dict)
    except Exception as e:
        status_dict[task_id] = {"status": "error", "detail": f"Erro no download: {str(e)}"}

@app.post("/api/url-upload")
async def upload_url(
    req: URLUploadRequest,
    background_tasks: BackgroundTasks
):
    """
    Download a video from a public URL and start background transcription.
    """
    if not req.url:
        raise HTTPException(status_code=400, detail="URL não fornecida.")
        
    task_id = str(uuid.uuid4())
    video_filename = f"{task_id}_download.mp4"
    video_path = STORAGE_DIR / video_filename
    
    background_tasks.add_task(
        background_download_and_transcribe, 
        req.url,
        video_path, 
        task_id, 
        transcription_tasks
    )
        
    return {
        "status": "started", 
        "task_id": task_id,
        "video_url": f"/storage/{video_filename}"
    }

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
