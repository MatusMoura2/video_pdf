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

    // 2. File Upload Handling
    const videoUpload = document.getElementById('video-upload');
    const pdfUpload = document.getElementById('pdf-upload');
    const videoEl = document.getElementById('main-video');

    videoUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if(!file) return;
        
        // For local quick load without server upload for demo:
        const url = URL.createObjectURL(file);
        videoEl.src = url;
    });

    pdfUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if(!file) return;
        
        const url = URL.createObjectURL(file);
        // Dispatch custom event to sync engine
        const event = new CustomEvent('pdfLoaded', { detail: { url } });
        document.dispatchEvent(event);
    });
});
