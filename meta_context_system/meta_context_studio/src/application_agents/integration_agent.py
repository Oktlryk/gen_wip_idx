"""Specialized agent for integrating generated components into a cohesive application."""

import re
import logging
from pathlib import Path

from meta_context_studio.src.utils.file_utils import parse_and_save_monolithic_file


class IntegrationAgent:
    """
    The Integration Agent is responsible for assembling the generated code,
    tests, and configurations into a functional application structure.
    It expects cleaned, monolithic code blocks from other agents.
    """

    def __init__(self):
        """
        Initializes the IntegrationAgent.
        """
        self.logger = logging.getLogger(__name__)

    def build_application(self, goal: str, generated_outputs: dict) -> str:
        """
        Builds the complete application structure from generated outputs.

        Args:
            goal: The original high-level goal, used for the directory name.
            generated_outputs: A dictionary containing outputs from other agents.

        Returns:
            A message indicating the success or failure of the build process.
        """
        self.logger.info("IntegrationAgent: Assembling application for goal: '%s'", goal)
        
        # Sanitize the goal to create a valid directory name
        sanitized_goal = re.sub(r'[<>:"/\\|?*]', '_', goal)
        current_file_dir = Path(__file__).resolve().parent
        base_dir = current_file_dir.parent.parent / 'generated_apps' / sanitized_goal

        try:
            for agent_name, monolithic_content in generated_outputs.items():
                if monolithic_content and isinstance(monolithic_content, str):
                    self.logger.info("Parsing output from %s", agent_name)
                    parse_and_save_monolithic_file(monolithic_content, str(base_dir))
            
            status_message = f"Application '{goal}' built successfully in {base_dir.resolve()}"
            self.logger.info(status_message)
            return status_message
        except Exception as e:
            self.logger.error("Error building application: %s", e, exc_info=True)
            return f"IntegrationAgent: Error building application: {e}"