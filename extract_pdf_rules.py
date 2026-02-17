
import pypdf
import re

def extract_rules(pdf_path):
    print(f"Extracting text from {pdf_path}...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
            
        # Search for keywords
        keywords = ["caption", "figure", "diagram", "image", "label", "table"]
        
        print("\n--- Usage of Keywords ---")
        lines = full_text.split('\n')
        for i, line in enumerate(lines):
            if any(k in line.lower() for k in keywords):
                # Print context
                print(f"[{i}] {line.strip()}")
                
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    extract_rules("Guidelines_Written Assignment.pdf")
