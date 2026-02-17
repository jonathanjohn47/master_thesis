
import pypdf

def dump_text(pdf_path, output_path):
    print(f"Dumping text from {pdf_path} to {output_path}...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        full_text = ""
        for i, page in enumerate(reader.pages):
            full_text += f"\n--- Page {i+1} ---\n"
            full_text += page.extract_text() + "\n"
            
        with open(output_path, "w") as f:
            f.write(full_text)
            
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    dump_text("Guidelines_Written Assignment.pdf", "pdf_content.txt")
