import hashlib
from typing import List
from bs4 import BeautifulSoup
from meta_context_studio.src.ingestion.data_models import ParsedDocument, ContentBlock, DocumentType, ContentBlockType

def generate_document_id(content: str) -> str:
    """Generates a unique SHA256 hash for the document content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def parse_html_document(
    file_path: str,
    document_type: DocumentType,
    source_content: str
) -> ParsedDocument:
    """
    Parses an HTML document and extracts its content into a structured ParsedDocument.
    """
    soup = BeautifulSoup(source_content, 'html.parser')
    content_blocks: List[ContentBlock] = []

    # Extract title for metadata
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else 'Untitled Document'

    # Basic content extraction (can be expanded)
    # Look for common text-containing tags and specific div classes
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'table', 'li', 'div']):
        block_type = None
        if element.name.startswith('h'):
            block_type = ContentBlockType.HEADING
        elif element.name == 'p':
            block_type = ContentBlockType.PARAGRAPH
        elif element.name == 'pre':
            block_type = ContentBlockType.CODE_BLOCK
        elif element.name == 'table':
            block_type = ContentBlockType.TABLE
        elif element.name == 'li':
            block_type = ContentBlockType.LIST_ITEM
        elif element.name == 'div':
            # Check if the div contains significant text content
            text_content = element.get_text(separator=' ', strip=True)
            if len(text_content) > 50: # Heuristic to avoid empty or very short divs
                block_type = ContentBlockType.PARAGRAPH # Treat as a general text block

        if block_type and element.get_text(strip=True):
            content_blocks.append(ContentBlock(
                block_type=block_type,
                content=element.get_text(separator=' ', strip=True),
                block_index=len(content_blocks), # Assign a sequential index
                metadata={'tag': element.name, 'class': element.get('class', [])}
            ))
    print(f"HTMLParser: Extracted {len(content_blocks)} content blocks.")

    document_id = generate_document_id(source_content)

    return ParsedDocument(
        document_id=document_id,
        document_type=document_type,
        source_path=file_path,
        metadata={'title': title},
        content_blocks=content_blocks
    )
