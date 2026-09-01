document.addEventListener('DOMContentLoaded', () => {
    // 1. Resizer Logic
    const resizer = document.getElementById('dragMe');
    const leftSide = document.getElementById('left-panel');
    const rightSide = document.getElementById('right-panel');

    let x = 0;
    let leftWidth = 0;

    const mouseDownHandler = function(e) {
        x = e.clientX;
        leftWidth = leftSide.getBoundingClientRect().width;
        
        document.addEventListener('mousemove', mouseMoveHandler);
        document.addEventListener('mouseup', mouseUpHandler);
        
        document.body.style.cursor = 'col-resize';
        leftSide.style.userSelect = 'none';
        leftSide.style.pointerEvents = 'none';
        rightSide.style.userSelect = 'none';
        rightSide.style.pointerEvents = 'none';
    };

    const mouseMoveHandler = function(e) {
        const dx = e.clientX - x;
        const newLeftWidth = ((leftWidth + dx) * 100) / resizer.parentNode.getBoundingClientRect().width;
        
        if(newLeftWidth > 20 && newLeftWidth < 80) {
            leftSide.style.width = `${newLeftWidth}%`;
        }
    };

    const mouseUpHandler = function() {
        document.body.style.removeProperty('cursor');
        leftSide.style.removeProperty('user-select');
        leftSide.style.removeProperty('pointer-events');
        rightSide.style.removeProperty('user-select');
        rightSide.style.removeProperty('pointer-events');
        
        document.removeEventListener('mousemove', mouseMoveHandler);
        document.removeEventListener('mouseup', mouseUpHandler);
    };

    resizer.addEventListener('mousedown', mouseDownHandler);

    // 2. File Upload & Transcription Polling
    const videoUpload = document.getElementById('video-upload');
    const videoEl = document.getElementById('main-video');
    const statusIndicator = document.getElementById('status-indicator');
    const urlInput = document.getElementById('url-input');
    const btnImportUrl = document.getElementById('btn-import-url');
    let pollingInterval = null;

    // Handle Local File Upload
    videoUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if(!file) return;
        
        const localUrl = URL.createObjectURL(file);
        videoEl.src = localUrl;
        
        statusIndicator.innerText = "Fazendo upload...";
        statusIndicator.style.color = "#3b82f6";
        
        const formData = new FormData();
        formData.append("video", file);
        
        try {
            const uploadRes = await fetch("/api/upload", { method: "POST", body: formData });
            handleUploadResponse(uploadRes);
        } catch(err) {
            handleError(err);
        }
    });

    // Handle URL Import
    btnImportUrl.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if(!url) {
            alert("Por favor, insira uma URL válida.");
            return;
        }
        
        statusIndicator.innerText = "Iniciando download...";
        statusIndicator.style.color = "#3b82f6";
        
        try {
            const uploadRes = await fetch("/api/url-upload", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url })
            });
            handleUploadResponse(uploadRes, true);
        } catch(err) {
            handleError(err);
        }
    });

    async function handleUploadResponse(response, isUrl = false) {
        const data = await response.json();
        if (data.status === "started") {
            statusIndicator.innerText = "IA iniciada...";
            if (isUrl) {
                // If it's a URL, wait to set the video source until it's ready, 
                // or just set it to the backend streaming path. 
                // For simplicity, we just point the video player to the static file path immediately.
                // It might not play until downloaded, but timeupdate will sync when it does.
                videoEl.src = data.video_url;
            }
            pollStatus(data.task_id);
        } else {
            statusIndicator.innerText = "Erro ao iniciar IA";
            statusIndicator.style.color = "#ef4444";
        }
    }

    function handleError(err) {
        console.error("Upload error:", err);
        statusIndicator.innerText = "Erro de conexão";
        statusIndicator.style.color = "#ef4444";
    }
    
    function pollStatus(taskId) {
        if(pollingInterval) clearInterval(pollingInterval);
        
        pollingInterval = setInterval(async () => {
            try {
                const res = await fetch(`/api/transcribe/status/${taskId}`);
                const data = await res.json();
                
                if (data.status === "processing") {
                    statusIndicator.innerText = `🔄 ${data.progress}`;
                } else if (data.status === "completed") {
                    clearInterval(pollingInterval);
                    statusIndicator.innerText = "✅ Transcrição Concluída";
                    statusIndicator.style.color = "#22c55e"; // Green
                    
                    // Show PDF download button
                    const pdfBtn = document.getElementById('btn-download-pdf');
                    pdfBtn.style.display = "inline-block";
                    pdfBtn.href = `/api/export/pdf/${taskId}`;
                    
                    // Trigger sync engine to load subtitles
                    const event = new CustomEvent('transcriptionReady', { detail: { json_url: data.json_url } });
                    document.dispatchEvent(event);
                    
                } else if (data.status === "error") {
                    clearInterval(pollingInterval);
                    statusIndicator.innerText = `❌ Erro: ${data.detail}`;
                    statusIndicator.style.color = "#ef4444"; // Red
                }
            } catch(err) {
                console.error("Polling error:", err);
            }
        }, 2000); // Poll every 2 seconds
    }
});
