import sys
from pathlib import Path

def verify_venv():
    """
    Verifies that the correct virtual environment is active, as per GEMINI.md.
    Exits the program with an informative message if the check fails.
    """
    # Find the project root by looking for a marker file, like `setup.py`.
    current_path = Path(__file__).resolve()
    project_root = None
    for parent in current_path.parents:
        if (parent / "setup.py").exists():
            project_root = parent
            break
    
    if not project_root:
        print("Error: Could not determine the project root. The venv check cannot be performed.")
        sys.exit(1)

    expected_venv_path = project_root / '.venv'
    
    # sys.prefix gives the path to the active python interpreter's environment.
    # We resolve both paths to get their canonical representation to avoid
    # issues with symlinks or case-insensitivity on some filesystems.
    is_correct_venv = Path(sys.prefix).resolve() == expected_venv_path.resolve()

    if not is_correct_venv:
        print("Error: Virtual environment not active or not the correct one. Please activate it using:")
        activate_script_win = expected_venv_path / 'Scripts' / 'activate'
        activate_script_nix = expected_venv_path / 'bin' / 'activate'
        print(f"  source {activate_script_nix} (Linux/macOS)")
        print(f"  {activate_script_win} (Windows)")
        sys.exit(1)