from fpdf import FPDF
from pathlib import Path
import json

STORAGE_DIR = Path("storage/transcricoes")

class PDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('helvetica', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Roteiro de Transcricao (Video PDF Player)', 0, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('helvetica', 'I', 8)
        # Page number
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_pdf_from_transcription(task_id: str) -> Path:
    json_path = STORAGE_DIR / f"{task_id}.json"
    pdf_path = STORAGE_DIR / f"{task_id}.pdf"
    
    if not json_path.exists():
        raise FileNotFoundError("Transcricao nao encontrada.")
        
    with open(json_path, 'r', encoding='utf-8') as f:
        segments = json.load(f)
        
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # We use helvetica as a standard font. 
    # For complex unicode (accents), we should use a proper unicode font, 
    # but for basic Portuguese text fpdf2 built-in latin1/helvetica handles most if we just use string.
    pdf.set_font('helvetica', size=11)
    
    for segment in segments:
        # Time format: MM:SS
        start_min = int(segment['start'] // 60)
        start_sec = int(segment['start'] % 60)
        time_str = f"[{start_min:02d}:{start_sec:02d}]"
        
        # We replace some characters that might crash standard helvetica
        text = segment['text'].replace('\u201c', '"').replace('\u201d', '"').replace('\u2019', "'")
        
        # Print Time (Bold)
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(20, 8, time_str, 0, 0)
        
        # Print Text (Regular)
        pdf.set_font('helvetica', '', 11)
        pdf.multi_cell(0, 8, text)
        pdf.ln(2)
        
    pdf.output(str(pdf_path))
    return pdf_path
