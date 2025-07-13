from haystack.components.writers.document_writer import DocumentWriter
from typing import List, Optional
from haystack.dataclasses import Document
from haystack.document_stores.types import DuplicatePolicy
from haystack.core.component import component

class CustomDocumentWriter(DocumentWriter):
    """
    A custom wrapper for the Haystack DocumentWriter to fix an issue with the
    run_async method's signature and output type specification, which causes
    ComponentError in the validation logic.
    """

    @component.output_types(documents_written=int)
    def run(self, documents: List[Document], policy: Optional[DuplicatePolicy] = None):
        """
        The synchronous run method. It calls the parent class's run method.
        """
        return super().run(documents=documents, policy=policy)

    @component.output_types(documents_written=int)
    async def run_async(self, documents: List[Document], policy: Optional[DuplicatePolicy] = None):
        """
        The asynchronous run method. It mirrors the synchronous method's
        signature and output types to satisfy Haystack's component validation.
        It calls the synchronous run method internally.
        """
        return self.run(documents=documents, policy=policy)