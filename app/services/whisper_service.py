from faster_whisper import WhisperModel
import uuid
import os
from pathlib import Path
import json

STORAGE_DIR = Path("storage")
TRANSCRIPTIONS_DIR = STORAGE_DIR / "transcricoes"
TRANSCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)

# Using a smaller default model for speed without GPU, can be 'medium' if desired
MODEL_SIZE = "base"

# Global model instance
model = None

def get_model():
    global model
    if model is None:
        # Load the model with CPU (or GPU if available)
        model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return model

def formatar_tempo(segundos):
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segundos_inteiros = int(segundos % 60)
    milissegundos = int((segundos % 1) * 1000)

    return f"{horas:02d}:{minutos:02d}:{segundos_inteiros:02d},{milissegundos:03d}"

def process_video_transcription(video_path: Path, task_id: str, status_dict: dict):
    """
    Processes the video transcription using faster-whisper and saves the SRT.
    """
    try:
        status_dict[task_id] = {"status": "processing", "progress": "Loading model..."}
        current_model = get_model()
        
        status_dict[task_id]["progress"] = "Transcribing audio..."
        # Transcribe
        segments, info = current_model.transcribe(str(video_path), beam_size=5, language="pt")
        
        # We need to exhaust the generator to get all segments
        segments_data = []
        srt_content = ""
        
        for i, segment in enumerate(segments, start=1):
            start_fmt = formatar_tempo(segment.start)
            end_fmt = formatar_tempo(segment.end)
            text = segment.text.strip()
            
            segments_data.append({
                "id": i,
                "start": segment.start,
                "end": segment.end,
                "text": text
            })
            
            srt_content += f"{i}\n{start_fmt} --> {end_fmt}\n{text}\n\n"
            
            # Update status occasionally (simplified)
            if i % 10 == 0:
                status_dict[task_id]["progress"] = f"Transcribed segment {i} ({start_fmt})"
        
        # Save SRT
        srt_path = TRANSCRIPTIONS_DIR / f"{task_id}.srt"
        srt_path.write_text(srt_content, encoding="utf-8")
        
        # Save JSON for frontend rendering
        json_path = TRANSCRIPTIONS_DIR / f"{task_id}.json"
        json_path.write_text(json.dumps(segments_data, ensure_ascii=False), encoding="utf-8")
        
        status_dict[task_id] = {
            "status": "completed", 
            "json_url": f"/storage/transcricoes/{task_id}.json",
            "srt_url": f"/storage/transcricoes/{task_id}.srt"
        }
        
    except Exception as e:
        status_dict[task_id] = {"status": "error", "detail": str(e)}
