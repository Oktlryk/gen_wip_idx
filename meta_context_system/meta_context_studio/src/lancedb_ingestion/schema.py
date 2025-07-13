from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentMetadata(BaseModel):
    """
    A flexible metadata container for documents.
    """
    source: str = Field(description="The origin of the document (e.g., file path, URL).")
    last_modified: Optional[datetime] = Field(default_factory=datetime.utcnow, description="The last modification time of the source.")
    tags: List[str] = Field(default_factory=list, description="A list of tags for categorization and filtering.")
    custom_properties: str = Field(default='{}', description="A JSON string for any other metadata.")

class Document(BaseModel):
    """
    Represents a document to be ingested into the knowledge base.
    """
    text: str = Field(description="The textual content of the document.")
    metadata: DocumentMetadata = Field(description="The metadata associated with the document.")
