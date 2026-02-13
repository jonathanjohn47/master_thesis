
from pdf2docx import Converter
from docx import Document
import os

def convert_results():
    pdf_file = "Results_Section.pdf"
    docx_file = "Results_Section.docx"
    
    print(f"Converting {pdf_file} to {docx_file}...")
    try:
        cv = Converter(pdf_file)
        cv.convert(docx_file, start=0, end=None)
        cv.close()
        print("Conversion successful.")
        
        # Apply Arial Font
        print("Applying Arial font...")
        doc = Document(docx_file)
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        
        for p in doc.paragraphs:
            for r in p.runs:
                r.font.name = 'Arial'
                
        doc.save(docx_file)
        print(f"Saved {docx_file} with Arial font.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    convert_results()
