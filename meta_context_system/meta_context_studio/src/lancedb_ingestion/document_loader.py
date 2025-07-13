import os
from typing import List
from bs4 import BeautifulSoup
from .schema import Document, DocumentMetadata

class DocumentLoader:
    """
    Loads and parses documents from various sources.
    """

    def load_from_directory(self, directory_path: str) -> List[Document]:
        """
        Loads all supported documents from a directory.

        Args:
            directory_path (str): The path to the directory containing the documents.

        Returns:
            List[Document]: A list of loaded and parsed documents.
        """
        documents = []
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if filename.endswith(".html"):
                documents.append(self.load_html(file_path))
        return documents

    def load_html(self, file_path: str) -> Document:
        """
        Loads and parses an HTML file.

        Args:
            file_path (str): The path to the HTML file.

        Returns:
            Document: The parsed document.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            metadata = DocumentMetadata(source=file_path)
            return Document(text=text, metadata=metadata)

