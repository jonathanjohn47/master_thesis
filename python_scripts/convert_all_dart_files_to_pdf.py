import argparse
import os
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: reportlab. Install it with `pip install reportlab` and try again."
    ) from exc

SUPPORTED_EXTENSIONS = {
    ".dart", ".py", ".json", ".csv", ".md"
}

SKIP_DIRECTORIES = {
    ".git", "__pycache__", "node_modules", ".idea", ".vscode",
    ".venv", "venv", "build", "dist"
}

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 40
RIGHT_MARGIN = 40
TOP_MARGIN = 50
BOTTOM_MARGIN = 40
TITLE_FONT = "Helvetica-Bold"
BODY_FONT = "Courier"
TITLE_FONT_SIZE = 14
HEADING_FONT_SIZE = 10
BODY_FONT_SIZE = 8
LINE_HEIGHT = 10


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Export all supported code/text files in a folder to a single PDF."
    )
    parser.add_argument(
        "source_directory",
        nargs="?",
        help="Absolute or relative path to the folder containing code files.",
    )
    parser.add_argument(
        "output_directory",
        nargs="?",
        help="Directory where the generated PDF should be saved.",
    )
    parser.add_argument(
        "--output-name",
        default=None,
        help="Name of the generated PDF file without extension.",
    )
    return parser.parse_args()


def prompt_for_missing_values(args):
    source_directory = args.source_directory or input(
        "Enter the absolute path to the folder containing the code files: "
    ).strip()
    output_directory = args.output_directory or input(
        "Enter the absolute path to the folder where you want to save the PDF: "
    ).strip()
    output_name = args.output_name or input(
        "Enter the name of the PDF file (without extension): "
    ).strip()
    return source_directory, output_directory, output_name


def normalize_output_name(output_name):
    cleaned_name = output_name.strip() or "combined_code_export"
    return cleaned_name if cleaned_name.lower().endswith(".pdf") else f"{cleaned_name}.pdf"


def iter_supported_files(source_directory):
    for root, dirs, files in os.walk(source_directory):
        dirs[:] = sorted(directory for directory in dirs if directory not in SKIP_DIRECTORIES)

        for file_name in sorted(files):
            file_path = Path(root) / file_name
            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield file_path, file_path.relative_to(source_directory)


def read_file_content(file_path):
    with open(file_path, "r", encoding="utf-8", errors="replace") as file_handle:
        return file_handle.read()


def wrap_text_line(text, font_name, font_size, max_width):
    expanded_text = text.expandtabs(4)
    if not expanded_text:
        return [""]

    wrapped_lines = []
    current_line = ""

    for character in expanded_text:
        candidate = f"{current_line}{character}"
        if current_line and stringWidth(candidate, font_name, font_size) > max_width:
            wrapped_lines.append(current_line)
            current_line = character
        else:
            current_line = candidate

    if current_line:
        wrapped_lines.append(current_line)

    return wrapped_lines


def start_page(pdf_canvas, page_number, pdf_title):
    pdf_canvas.setFont(TITLE_FONT, TITLE_FONT_SIZE)
    pdf_canvas.drawString(LEFT_MARGIN, PAGE_HEIGHT - TOP_MARGIN + 12, pdf_title)
    pdf_canvas.setFont("Helvetica", 9)
    pdf_canvas.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, PAGE_HEIGHT - TOP_MARGIN + 12, f"Page {page_number}")
    pdf_canvas.line(LEFT_MARGIN, PAGE_HEIGHT - TOP_MARGIN + 6, PAGE_WIDTH - RIGHT_MARGIN, PAGE_HEIGHT - TOP_MARGIN + 6)
    return PAGE_HEIGHT - TOP_MARGIN - 8


MAX_PDF_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB
MAX_PAGES_PER_PDF = 40  # ~5MB depending on content (adjust if needed)
def create_pdf_from_files(file_entries, pdf_file_path, source_directory):
    pdf_title = f"Code Export: {Path(source_directory).name}"

    base_name = pdf_file_path.stem
    output_dir = pdf_file_path.parent

    TOTAL_PARTS = 19
    total_files = len(file_entries)

    if total_files == 0:
        return

    # Compute chunk size (balanced split)
    chunk_size = (total_files + TOTAL_PARTS - 1) // TOTAL_PARTS  # ceil division

    usable_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

    for part_number in range(TOTAL_PARTS):
        start_idx = part_number * chunk_size
        end_idx = min(start_idx + chunk_size, total_files)

        if start_idx >= total_files:
            break  # no more files

        part_entries = file_entries[start_idx:end_idx]

        part_path = output_dir / f"{base_name}_part{part_number + 1}.pdf"
        pdf_canvas = canvas.Canvas(str(part_path), pagesize=A4)
        pdf_canvas.setTitle(f"{pdf_title} (Part {part_number + 1})")

        page_number = 1
        y_position = start_page(pdf_canvas, page_number, pdf_title)

        # Header
        pdf_canvas.setFont("Helvetica", 9)
        pdf_canvas.drawString(LEFT_MARGIN, y_position, f"Source folder: {Path(source_directory).resolve()}")
        y_position -= LINE_HEIGHT
        pdf_canvas.drawString(LEFT_MARGIN, y_position, f"Files in this part: {len(part_entries)}")
        y_position -= LINE_HEIGHT * 2

        for file_path, relative_path in part_entries:

            if y_position <= BOTTOM_MARGIN + (LINE_HEIGHT * 4):
                pdf_canvas.showPage()
                page_number += 1
                y_position = start_page(pdf_canvas, page_number, pdf_title)

            pdf_canvas.setFont(TITLE_FONT, HEADING_FONT_SIZE)
            pdf_canvas.drawString(LEFT_MARGIN, y_position, f"File: {relative_path}")
            y_position -= LINE_HEIGHT

            pdf_canvas.setFont("Helvetica", 8)
            pdf_canvas.drawString(LEFT_MARGIN, y_position, "-" * 110)
            y_position -= LINE_HEIGHT

            pdf_canvas.setFont(BODY_FONT, BODY_FONT_SIZE)

            file_content = read_file_content(file_path)
            content_lines = file_content.splitlines() or [""]

            for line in content_lines:
                for wrapped_line in wrap_text_line(line, BODY_FONT, BODY_FONT_SIZE, usable_width):

                    if y_position <= BOTTOM_MARGIN + LINE_HEIGHT:
                        pdf_canvas.showPage()
                        page_number += 1
                        y_position = start_page(pdf_canvas, page_number, pdf_title)
                        pdf_canvas.setFont(BODY_FONT, BODY_FONT_SIZE)

                    pdf_canvas.drawString(LEFT_MARGIN, y_position, wrapped_line)
                    y_position -= LINE_HEIGHT

            y_position -= LINE_HEIGHT

        pdf_canvas.save()
        print(f"Created: {part_path}")


def main(source_directory, output_directory, output_name):
    source_directory = Path(source_directory).expanduser().resolve()
    output_directory = Path(output_directory).expanduser().resolve()

    if not source_directory.is_dir():
        print(f"Error: '{source_directory}' is not a valid directory.")
        return 1

    output_directory.mkdir(parents=True, exist_ok=True)

    file_entries = list(iter_supported_files(source_directory))
    if not file_entries:
        print(f"No supported code or text files found in '{source_directory}'.")
        return 1

    pdf_file_path = output_directory / normalize_output_name(output_name)
    create_pdf_from_files(file_entries, pdf_file_path, source_directory)
    print(f"Successfully created PDF: '{pdf_file_path}'")
    return 0


if __name__ == "__main__":
    cli_args = parse_arguments()
    source_dir, output_dir, output_name = prompt_for_missing_values(cli_args)
    raise SystemExit(main(source_dir, output_dir, output_name))
