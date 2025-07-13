import os
import re
from pathlib import Path


def parse_and_save_monolithic_file(monolithic_content: str, base_dir: str):
    """
    Parses a monolithic string containing multiple files indicated by
    commented headers like '# /path/to/file.py' and saves them.

    Args:
        monolithic_content (str): The single string containing all code.
        base_dir (str): The root directory for the generated application.
    """
    print(f"--- Parsing and saving monolithic file to {base_dir} ---")
    # Split the content by file markers. The pattern looks for lines
    # starting with #, optional whitespace, and then a file-like path.
    # The (?=...) is a positive lookahead to keep the delimiter.
    # This regex is more flexible and handles paths that don't start with '/'.
    file_blocks = re.split(r'(?m)^#\s*([./\w\-\\]+)', monolithic_content)

    if len(file_blocks) < 2:
        print("No file markers found. Saving raw output as fallback.")
        fallback_path = Path(base_dir) / "monolithic_output.py"
        fallback_path.parent.mkdir(parents=True, exist_ok=True)
        fallback_path.write_text(monolithic_content, encoding="utf-8")
        print(f"Saved raw output to {fallback_path}")
        return

    # The first element is usually empty or some preamble, we can ignore it.
    # The list is now [preamble, path1, content1, path2, content2, ...]
    i = 1
    while i < len(file_blocks):
        file_path_str = file_blocks[i].strip()
        content = file_blocks[i+1].strip()
        
        # Sanitize path: remove leading '/' and normalize
        sanitized_path = os.path.normpath(file_path_str.lstrip('/'))
        
        # Prevent directory traversal
        if ".." in file_path_str.split(os.path.sep):
            print(f"Skipping potentially unsafe file path with '..': {file_path_str}")
            i += 2
            continue

        full_path = Path(base_dir) / sanitized_path

        # Final check to ensure we are not writing outside the intended directory.
        if not str(full_path.resolve()).startswith(str(Path(base_dir).resolve())):
            print(f"Skipping unsafe file path outside base directory: {file_path_str}")
            i += 2
            continue

        try:
            print(f"Creating artifact: {full_path}")
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
        except (OSError, Exception) as e:
            print(f"Error creating file {full_path}: {e}")

        i += 2