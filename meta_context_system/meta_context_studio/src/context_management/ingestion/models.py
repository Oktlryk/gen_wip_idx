from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DocumentType(str, Enum):
    """
    Defines the types of documents that can be ingested into the system.
    """
    TECHNICAL_REPORT = "technical_report"
    GENESIS_PHILOSOPHY = "genesis_philosophy"
    UNKNOWN = "unknown"

class ContentBlock(BaseModel):
    """
    Represents a block of content within a document.
    """
    block_type: str = Field(..., description="Type of the content block (e.g., 'paragraph', 'heading', 'code', 'table').")
    content: str = Field(..., description="The textual content of the block.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the content block (e.g., 'level' for headings, 'language' for code).")

class ParsedDocument(BaseModel):
    """
    Represents a document after it has been parsed into a standardized format.
    This model acts as the "Document Processing Contract" between the Parsing and Interpretation layers.
    """
    document_id: str = Field(..., description="A unique identifier for the document, typically a hash of its content.")
    file_path: str = Field(..., description="The original file path of the document.")
    document_type: DocumentType = Field(..., description="The categorized type of the document.")
    title: Optional[str] = Field(None, description="The title of the document.")
    authors: List[str] = Field(default_factory=list, description="List of authors of the document.")
    publication_date: Optional[str] = Field(None, description="The publication date of the document (e.g., 'YYYY-MM-DD').")
    version: Optional[str] = Field(None, description="Version of the document, if applicable.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="General metadata for the entire document.")
    content_blocks: List[ContentBlock] = Field(default_factory=list, description="Ordered list of content blocks extracted from the document.")
    checksum: str = Field(..., description="SHA256 checksum of the raw document content for idempotency.")

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "document_id": "a1b2c3d4e5f67890abcdef1234567890abcdef",
                "file_path": "/path/to/document.html",
                "document_type": "technical_report",
                "title": "The Genesis Engine: A Technical Report",
                "authors": ["AI Agent", "Human Collaborator"],
                "publication_date": "2025-07-11",
                "version": "1.0",
                "metadata": {"source": "internal_report"},
                "content_blocks": [
                    {"block_type": "heading", "content": "1. Introduction", "metadata": {"level": 1}},
                    {"block_type": "paragraph", "content": "This document outlines the Genesis Engine...", "metadata": {}},
                ],
                "checksum": "abcdef1234567890abcdef1234567890abcdef"
            }
        }
