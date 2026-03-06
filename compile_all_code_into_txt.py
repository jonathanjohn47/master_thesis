import os

# Root directory to scan (change if needed)
ROOT_DIR = "."

# Output file
OUTPUT_FILE = "compiled_text_output.txt"

# File extensions considered text
TEXT_EXTENSIONS = {
    ".py", ".txt", ".md", ".json", ".csv", ".yaml", ".yml",
    ".xml", ".html", ".css", ".js", ".ts",
    ".java", ".c", ".cpp", ".h", ".hpp",
    ".sh", ".bat", ".ini", ".cfg", ".conf"
}

def is_text_file(filepath):
    _, ext = os.path.splitext(filepath)
    return ext.lower() in TEXT_EXTENSIONS


def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"[ERROR READING FILE: {e}]"


def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as output:

        for root, dirs, files in os.walk(ROOT_DIR):

            # Skip common unwanted folders
            dirs[:] = [d for d in dirs if d not in {
                ".git", "__pycache__", "node_modules", ".idea", ".vscode"
            }]

            for file in files:

                filepath = os.path.join(root, file)

                if is_text_file(filepath):

                    print(f"Processing: {filepath}")

                    content = read_file(filepath)

                    output.write("\n")
                    output.write("=" * 80 + "\n")
                    output.write(f"FILE: {filepath}\n")
                    output.write("=" * 80 + "\n\n")

                    output.write(content)
                    output.write("\n\n")

    print(f"\nCompilation complete.")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()