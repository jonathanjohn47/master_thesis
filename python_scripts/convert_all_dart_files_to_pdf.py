import os

def create_txt_from_content(combined_content, txt_file_path):
    """Creates a text file from the given content.

    Args:
        combined_content (str): The combined text content of the Dart files.
        txt_file_path (str): Absolute path where the text file should be saved.
    """
    try:
        # Create the text file
        with open(txt_file_path, 'w', encoding='utf-8') as f:
            f.write(combined_content)

        print(f"Successfully created text file: '{os.path.basename(txt_file_path)}'")

    except Exception as e:
        print(f"Error creating text file '{os.path.basename(txt_file_path)}': {e}")

def main(lib_directory_path, output_path):
    """Walks through the lib directory, concatenates Dart files, and creates a single text file.

    Args:
        lib_directory_path (str): Absolute path to the 'lib' directory.
        output_path (str): Absolute path to the folder where the text file should be saved.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    combined_dart_code = ""
    dart_files_found = False

    for root, _, files in os.walk(lib_directory_path):
        for file in files:
            if file.endswith('.dart') or file.endswith('.php') or file.endswith('.md') or file.endswith('.py') or file.endswith('.json') or file.endswith('.csv'):
                dart_file_path = os.path.join(root, file)
                try:
                    with open(dart_file_path, 'r', encoding='utf-8') as f:
                        dart_code = f.read()
                        combined_dart_code += f"```\nContent of {os.path.relpath(dart_file_path, lib_directory_path)}\n```\n"
                        combined_dart_code += dart_code + "\n\n"  # Add separator
                        dart_files_found = True
                except Exception as e:
                    print(f"Error reading '{dart_file_path}': {e}")

    if dart_files_found:
        txt_file_name = input("Enter the name of the text file (without extension): ")
        txt_file_path = os.path.join(output_path, f"{txt_file_name}.txt")
        create_txt_from_content(combined_dart_code, txt_file_path)
    else:
        print(f"No Dart files found in '{lib_directory_path}' or its subdirectories.")

if __name__ == "__main__":
    lib_directory = input("Enter the absolute path to the 'lib' directory: ")
    text_output_directory = input("Enter the absolute path to the folder where you want to save the text file: ")

    if not os.path.isdir(lib_directory):
        print(f"Error: '{lib_directory}' is not a valid directory.")
    elif not os.path.isdir(text_output_directory):
        print(f"Error: '{text_output_directory}' is not a valid directory.")
    else:
        main(lib_directory, text_output_directory)