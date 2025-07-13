import re
import logging

class CodeCleanupAgent:
    """
    An agent responsible for cleaning the raw output from LLM code generation.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def clean_code(self, raw_code: str) -> str:
        """
        Strips markdown code fences and other generation artifacts.

        Args:
            raw_code: The raw string output from the LLM.

        Returns:
            The cleaned code content as a single string.
        """
        self.logger.info("Cleaning raw code output.")
        # Regex to find a code block, possibly with a language hint
        match = re.search(r"```(?:python|bash|sh|typescript|javascript|html|css)?\n(.*?)\n```", raw_code, re.DOTALL)
        if match:
            cleaned_code = match.group(1).strip()
            self.logger.debug("Stripped markdown fences.")
            return cleaned_code
        
        self.logger.warning("No markdown fences found in raw code. Stripping whitespace only.")
        return raw_code.strip()