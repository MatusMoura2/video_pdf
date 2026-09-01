// PDF.js configuration
if (typeof pdfjsLib !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';
}

document.addEventListener('pdfLoaded', function(e) {
    const url = e.detail.url;
    renderPDF(url);
});

let pdfDoc = null;
let pageNum = 1;
let pageIsRendering = false;
let pageNumIsPending = null;

const scale = 1.2;
const canvas = document.getElementById('pdf-render');
const ctx = canvas.getContext('2d');

function renderPDF(url) {
    document.querySelector('.placeholder-text').style.display = 'none';
    
    pdfjsLib.getDocument(url).promise.then(pdfDoc_ => {
        pdfDoc = pdfDoc_;
        renderPage(pageNum);
    }).catch(err => {
        console.error("Erro ao carregar PDF:", err);
    });
}

function renderPage(num) {
    pageIsRendering = true;
    
    pdfDoc.getPage(num).then(page => {
        const viewport = page.getViewport({ scale });
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        
        const renderCtx = {
            canvasContext: ctx,
            viewport: viewport
        };
        
        page.render(renderCtx).promise.then(() => {
            pageIsRendering = false;
            if (pageNumIsPending !== null) {
                renderPage(pageNumIsPending);
                pageNumIsPending = null;
            }
        });
    });
}

// ---------------------------------------------------
// Sincronização com o Vídeo
// ---------------------------------------------------
const videoEl = document.getElementById('main-video');

// Placeholder for sync logic
// Example: Change page based on video time
videoEl.addEventListener('timeupdate', () => {
    // const currentTime = videoEl.currentTime;
    // Logica futura: mapear `currentTime` para texto / páginas
});
