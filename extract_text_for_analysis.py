
import os
import sys

def extract_pdf(pdf_path, output_path):
    text = ""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except ImportError:
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(pdf_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except ImportError:
            print(f"Error: Neither pypdf nor PyPDF2 is installed.")
            return False
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Successfully extracted PDF to {output_path}")
    return True

def extract_docx(docx_path, output_path):
    try:
        from docx import Document
        document = Document(docx_path)
        text = "\n".join([para.text for para in document.paragraphs])
    except ImportError:
        print("Error: python-docx is not installed.")
        return False
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return False

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Successfully extracted DOCX to {output_path}")
    return True

if __name__ == "__main__":
    base_dir = "/Users/jonathanjohn/StudioProjects/master_thesis"
    pdf_file = "Guidelines_Written Assignment.pdf"
    docx_file = "Empirical Analysis of Accuracy.docx"
    
    pdf_path = os.path.join(base_dir, pdf_file)
    docx_path = os.path.join(base_dir, docx_file)
    
    pdf_out = "guidelines_content.txt"
    docx_out = "thesis_content.txt"
    
    print(f"Processing {pdf_path}...")
    extract_pdf(pdf_path, pdf_out)
    
    print(f"Processing {docx_path}...")
    extract_docx(docx_path, docx_out)
