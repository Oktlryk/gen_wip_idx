import hashlib
import os
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from .parser_interface import DocumentParser
from .models import ParsedDocument, ContentBlock, DocumentType

class HTMLParser(DocumentParser):
    """
    Parses HTML documents into a standardized ParsedDocument format.
    """

    def supports_file_type(self, file_path: str) -> bool:
        """
        Checks if the parser supports HTML files.
        """
        return file_path.lower().endswith(('.html', '.htm'))

    def parse(self, file_path: str) -> ParsedDocument:
        """
        Parses an HTML document.
        """
        if not self.supports_file_type(file_path):
            raise ValueError(f"File type not supported by HTMLParser: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
        soup = BeautifulSoup(content, 'html.parser')

        title = self._extract_title(soup)
        document_type = self._determine_document_type(file_path, soup)
        authors = self._extract_authors(soup)
        publication_date = self._extract_publication_date(soup)
        version = self._extract_version(soup)
        metadata = self._extract_metadata(soup)
        content_blocks = self._extract_content_blocks(soup)

        return ParsedDocument(
            document_id=checksum, # Using checksum as document_id for now
            file_path=file_path,
            document_type=document_type,
            title=title,
            authors=authors,
            publication_date=publication_date,
            version=version,
            metadata=metadata,
            content_blocks=content_blocks,
            checksum=checksum
        )

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extracts the title from the HTML document.
        """
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        return None

    def _determine_document_type(self, file_path: str, soup: BeautifulSoup) -> DocumentType:
        """
        Determines the document type based on file path and content.
        This is a placeholder and can be expanded with more sophisticated logic.
        """
        # Example: Check for specific keywords or file names
        if "genesis_engine" in file_path.lower() or "genesis engine" in soup.get_text().lower():
            return DocumentType.GENESIS_PHILOSOPHY
        elif "technical_report" in file_path.lower() or "technical report" in soup.get_text().lower():
            return DocumentType.TECHNICAL_REPORT
        return DocumentType.UNKNOWN

    def _extract_authors(self, soup: BeautifulSoup) -> List[str]:
        """
        Extracts authors from meta tags or other common locations.
        """
        authors = []
        # Example: <meta name="author" content="John Doe">
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta and author_meta.get('content'):
            authors.append(author_meta['content'])
        return authors

    def _extract_publication_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extracts publication date from meta tags or other common locations.
        """
        # Example: <meta name="date" content="2023-10-27">
        date_meta = soup.find('meta', attrs={'name': 'date'})
        if date_meta and date_meta.get('content'):
            return date_meta['content']
        return None

    def _extract_version(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extracts version information.
        """
        # This is highly dependent on document structure. Placeholder.
        return None

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extracts general metadata from meta tags.
        """
        metadata = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        return metadata

    def _extract_content_blocks(self, soup: BeautifulSoup) -> List[ContentBlock]:
        """
        Extracts main content blocks (paragraphs, headings, code, etc.).
        This is a simplified extraction and can be made more robust.
        """
        content_blocks = []
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'li', 'blockquote']):
            block_type = element.name
            content = element.get_text(strip=True)
            if content:
                metadata = {}
                if block_type.startswith('h'):
                    metadata['level'] = int(block_type[1])
                elif block_type == 'pre':
                    metadata['language'] = 'plaintext' # Placeholder, can be improved with syntax highlighting detection
                content_blocks.append(ContentBlock(block_type=block_type, content=content, metadata=metadata))
        return content_blocks
