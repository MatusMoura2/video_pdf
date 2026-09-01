import yt_dlp
import os
from pathlib import Path

def download_video_from_url(url: str, output_path: Path) -> Path:
    """
    Downloads a video from a public URL (e.g. YouTube) and saves it to output_path.
    Returns the path to the downloaded video file.
    """
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # yt-dlp options: best format that has both video and audio, ideally mp4
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': str(output_path),
        'noplaylist': True,
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
    return output_path
