import os
import yaml
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ValidationError


# --- 1. Define a Pydantic model for our structured prompts ---
# This ensures every prompt we load has a consistent, validated structure.
class PromptTemplate(BaseModel):
    """A Pydantic model for a structured prompt template."""
    id: str
    type: str
    input_variables: List[str] = Field(default_factory=list)
    system_message: Optional[str] = None
    user_message: str

    def format(self, **kwargs: Any) -> Dict[str, str]:
        """
        Formats the prompt with the given context variables.

        Args:
            **kwargs: The values for the input variables in the template.

        Returns:
            A dictionary containing the formatted system and user messages,
            ready to be sent to an LLM.

        Raises:
            ValueError: If any of the required input_variables are missing from kwargs.
        """
        missing_keys = [key for key in self.input_variables if key not in kwargs]
        if missing_keys:
            raise ValueError(f"Missing required context variables: {', '.join(missing_keys)}")

        formatted_user_message = self.user_message.format(**kwargs)
        formatted_prompt = {
            "user": formatted_user_message
        }
        if self.system_message:
            formatted_prompt["system"] = self.system_message.format(**kwargs)

        return formatted_prompt


# --- 2. Create the PromptManager to act as a central registry ---
class PromptManager:
    """
    Manages loading, validation, and formatting of all prompt templates.
    Acts as a central registry for prompts defined in YAML files.
    """

    def __init__(self, prompts_dir: Optional[str] = None):
        if prompts_dir is None:
            # Default to a 'prompts' directory assumed to be at the project root.
            # This makes the path resolution more robust than relative paths.
            current_dir = os.path.dirname(__file__)
            project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
            self.prompts_dir = os.path.join(project_root, 'prompts')
        else:
            self.prompts_dir = prompts_dir

        self._templates: Dict[str, PromptTemplate] = self._load_all_templates()

    def _load_all_templates(self) -> Dict[str, PromptTemplate]:
        """Loads and validates all YAML prompt templates from the directory."""
        templates = {}
        if not os.path.isdir(self.prompts_dir):
            print(f"Warning: Prompts directory not found at {self.prompts_dir}")
            return templates

        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(('.yaml', '.yml')):
                template_path = os.path.join(self.prompts_dir, filename)
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if 'id' not in data:
                            print(f"Warning: Skipping {filename}, missing 'id' field.")
                            continue

                        template = PromptTemplate(**data)
                        templates[template.id] = template
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML in {filename}: {e}")
                except ValidationError as e:
                    print(f"Validation error for {filename} (id: {data.get('id', 'N/A')}): {e}")
                except Exception as e: # Catch any other unexpected errors
                    print(f"An unexpected error occurred while loading {filename}: {e}")

        print(f"Successfully loaded {len(templates)} prompt templates.")
        return templates

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        Retrieves a validated prompt template by its ID.

        Args:
            template_id (str): The unique ID of the prompt (e.g., 'course_content_generator_prompt').

        Returns:
            Optional[PromptTemplate]: The Pydantic model for the template, or None if not found.
        """
        template = self._templates.get(template_id)
        if not template:
            print(f"Error: Prompt template with ID '{template_id}' not found.")
        return template


# --- 3. Instantiate a singleton for easy access across the system ---
# This creates a module-level instance that acts as a singleton in practice
# for most Python applications, as modules are cached upon first import.
prompt_manager = PromptManager()


# Example of how an agent would use this new system:
def example_agent_usage():
    """Demonstrates how an agent would use the PromptManager."""

    # The agent gets the template by its logical ID, not a filename.
    template = prompt_manager.get_template("course_content_generator_prompt")

    if template:
        # The agent gathers the required context
        context = {
            "course_topic": "Introduction to Quantum Computing",
            "learning_objectives": "- Explain superposition\n- Describe entanglement",
            "target_audience_profile": "Beginner with a background in classical computing.",
            "pedagogical_guidelines": "Use analogies and avoid deep math.",
            "existing_content_style_guide": "Friendly and encouraging tone.",
            "content_format": "markdown"
        }

        # The manager handles the formatting.
        formatted_prompt = template.format(**context)

        print("--- Formatted Prompt for LLM ---")
        print(formatted_prompt)
        # This `formatted_prompt` dictionary can now be passed directly to the LLM client.


if __name__ == '__main__':
    example_agent_usage()
