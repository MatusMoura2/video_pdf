let segments = [];
let activeSegmentIndex = -1;

document.addEventListener('transcriptionReady', async (e) => {
    const jsonUrl = e.detail.json_url;
    try {
        const res = await fetch(jsonUrl);
        segments = await res.json();
        renderTranscription();
    } catch (err) {
        console.error("Failed to load transcription JSON", err);
    }
});

function renderTranscription() {
    const container = document.getElementById('transcription-container');
    container.innerHTML = ''; // Clear placeholder
    
    segments.forEach((segment, index) => {
        const div = document.createElement('div');
        div.className = 'transcript-segment';
        div.id = `segment-${index}`;
        
        // Format time (MM:SS) for display
        const startMin = Math.floor(segment.start / 60).toString().padStart(2, '0');
        const startSec = Math.floor(segment.start % 60).toString().padStart(2, '0');
        
        div.innerHTML = `
            <span class="segment-time">[${startMin}:${startSec}]</span>
            <span class="segment-text">${segment.text}</span>
        `;
        
        // Click to seek video
        div.addEventListener('click', () => {
            const videoEl = document.getElementById('main-video');
            videoEl.currentTime = segment.start;
            videoEl.play();
        });
        
        container.appendChild(div);
    });
}

// ---------------------------------------------------
// Sincronização com o Vídeo
// ---------------------------------------------------
const videoEl = document.getElementById('main-video');

videoEl.addEventListener('timeupdate', () => {
    if (segments.length === 0) return;
    
    const currentTime = videoEl.currentTime;
    
    // Find current segment
    let currentIdx = -1;
    for (let i = 0; i < segments.length; i++) {
        if (currentTime >= segments[i].start && currentTime <= segments[i].end) {
            currentIdx = i;
            break;
        }
    }
    
    // Fallback: if we are in a gap between segments, keep the last one active or none
    // (Here we just use exact bounds)
    
    if (currentIdx !== activeSegmentIndex) {
        // Remove highlight from old
        if (activeSegmentIndex !== -1) {
            const oldEl = document.getElementById(`segment-${activeSegmentIndex}`);
            if (oldEl) oldEl.classList.remove('active-segment');
        }
        
        // Add highlight to new
        if (currentIdx !== -1) {
            const newEl = document.getElementById(`segment-${currentIdx}`);
            if (newEl) {
                newEl.classList.add('active-segment');
                
                // Auto-scroll logic:
                // Only scroll if it's playing and we naturally reached it,
                // smooth scrolling ensures a nice experience.
                newEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
        
        activeSegmentIndex = currentIdx;
    }
});
