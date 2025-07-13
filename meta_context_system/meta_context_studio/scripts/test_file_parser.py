"""
A test script to verify the functionality of the monolithic file parser
located in `src/utils/file_utils.py`.
"""

import tempfile
from pathlib import Path
import sys

# Add project root to the Python path to resolve the ModuleNotFoundError.
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from meta_context_studio.src.utils.file_utils import parse_and_save_monolithic_file



# A representative sample of raw output from a code generation agent.
# It contains multiple files, different path formats, and preamble text.
SAMPLE_MONOLITHIC_OUTPUT = """
Here is the generated Flask application.

# /app.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "Hello from the generated app!"})

if __name__ == '__main__':
    app.run(debug=True)

# requirements.txt
Flask

# ./.env
FLASK_APP=app.py
FLASK_ENV=development

# /config/settings.py
# A simple config file
class Config:
    DEBUG = True
"""

def run_parser_test():
    """
    Tests the monolithic file parser by creating a temporary directory,
    running the parser, and verifying the output files and their contents.
    """
    # Use a temporary directory to avoid creating files in the project.
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"--- Created temporary directory for test: {tmpdir} ---")
        base_dir = Path(tmpdir)

        # Run the parser on the sample output.
        parse_and_save_monolithic_file(SAMPLE_MONOLITHIC_OUTPUT, str(base_dir))

        print("\n--- Verifying created files and directories ---")
        created_files = sorted([p.relative_to(base_dir) for p in base_dir.rglob("*") if p.is_file()])

        if not created_files:
            print("\n❌ Failure: No files were created.")
            return

        print("✅ Success: The following files were created:")
        for f_path in created_files:
            print(f"  - {f_path}")

        print("\n--- Verifying file contents ---")
        for f_path in created_files:
            print(f"\n--- Contents of: {f_path} ---")
            content = (base_dir / f_path).read_text().strip()
            print(content)
            print("-" * (20 + len(str(f_path))))

if __name__ == "__main__":
    run_parser_test()