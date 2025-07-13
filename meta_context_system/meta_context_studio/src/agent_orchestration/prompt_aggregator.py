"""Dynamically constructs prompts from fragments and context."""
import yaml
import os
from typing import Dict, Any

class PromptAggregator:
    """
    Manages the loading and construction of prompts from templates.
    """

    def __init__(self, prompts_dir: str):
        """
        Initializes the PromptAggregator.

        Args:
            prompts_dir: The directory where prompt templates are stored.
        """
        self.prompts_dir = prompts_dir

    def get_prompt(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Constructs a prompt from a template and a set of variables.

        Args:
            template_name: The name of the prompt template (without the .yaml extension).
            variables: A dictionary of variables to substitute into the template.

        Returns:
            The constructed prompt.
        """
        template_path = os.path.join(self.prompts_dir, f"{template_name}.yaml")
        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)

        # This is a simplified implementation. A real implementation would
        # have a more sophisticated templating engine.
        prompt = f"""# {template['name']}\n\n{template['description']}\n\n"""
        for var in template["variables"]:
            prompt += f"{var}: {variables.get(var, '')}\n"

        return prompt
