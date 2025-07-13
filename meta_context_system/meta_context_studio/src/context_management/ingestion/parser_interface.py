from abc import ABC, abstractmethod
from typing import List
from .models import ParsedDocument

class DocumentParser(ABC):
    """
    Abstract base class for document parsers.
    Defines the interface for parsing different document types into a standardized ParsedDocument format.
    """

    @abstractmethod
    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parses a document from the given file path into a ParsedDocument object.

        Args:
            file_path (str): The absolute path to the document file.

        Returns:
            ParsedDocument: The parsed document object.

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If there is an issue reading the file.
            Exception: For any other parsing-related errors.
        """
        pass

    @abstractmethod
    def supports_file_type(self, file_path: str) -> bool:
        """
        Checks if the parser supports the given file type based on its extension or content.

        Args:
            file_path (str): The absolute path to the document file.

        Returns:
            bool: True if the parser supports the file type, False otherwise.
        """
        pass
