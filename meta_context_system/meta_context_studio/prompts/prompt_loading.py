import os
from typing import Optional

def load_prompt_template(template_name: str) -> Optional[str]:
    """
    Loads a prompt template from the 'prompts' directory.

    Args:
        template_name (str): The filename of the prompt template (e.g., 'my_prompt.md').

    Returns:
        Optional[str]: The content of the prompt template, or None if not found.
    """
    # Assuming a 'prompts' directory at the same level as 'src' or within it.
    # Adjust the path as per your project structure.
    # For this example, let's assume it's in 'meta_context_studio/prompts/'
    prompts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'prompts')
    template_path = os.path.join(prompts_dir, template_name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt template not found at {template_path}")
        return None