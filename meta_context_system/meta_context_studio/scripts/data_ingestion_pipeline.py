import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from meta_context_studio.config import settings

# Haystack Imports
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.core.component import component # Import component decorator
from haystack import Document # Import Document class
from typing import List # Import List
from meta_context_studio.src.knowledge_base.vector_store import VectorStore
from meta_context_studio.src.knowledge_base.lancedb_haystack_writer import LanceDBWriter
from meta_context_studio.src.ingestion.data_models import ParsedDocument # New import

@component
class ParsedDocumentConverter:
    @component.output_types(documents=List[Document])
    def run(self, parsed_documents: List[ParsedDocument]):
        haystack_documents = []
        for doc in parsed_documents:
            for block in doc.content_blocks:
                if block.embedding is not None and block.content is not None:
                    haystack_doc = Document(
                        content=block.content,
                        embedding=block.embedding,
                        meta={
                            "document_id": doc.document_id,
                            "document_type": doc.document_type.value,
                            "source_path": doc.source_path,
                            "block_type": block.block_type.value,
                            "block_index": block.block_index,
                            "metadata": block.metadata # Keep original metadata structure
                        }
                    )
                    haystack_documents.append(haystack_doc)
        return {"documents": haystack_documents}

def run_ingestion_pipeline(documents_to_ingest: List[ParsedDocument], document_store: VectorStore):
    print("Initializing Haystack Ingestion Pipeline for LanceDB...")

    # 2. Initialize Haystack components
    # This component converts ParsedDocument objects into Haystack Document objects
    parsed_doc_converter = ParsedDocumentConverter()

    # This writes the final, embedded documents to LanceDB.
    lancedb_writer = LanceDBWriter()

    # 3. Build the ingestion pipeline
    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component("parsed_doc_converter", parsed_doc_converter)
    indexing_pipeline.add_component("lancedb_writer", lancedb_writer)

    # Connect the components
    indexing_pipeline.connect("parsed_doc_converter.documents", "lancedb_writer.documents")

    print(f"LanceDB store initialized. Documents in collection: {document_store.count_documents()}")

    # 4. Run the ingestion pipeline
    if documents_to_ingest:
        print(f"Found {len(documents_to_ingest)} ParsedDocuments to ingest. Starting pipeline...")
        try:
            indexing_pipeline.run({"parsed_doc_converter": {"parsed_documents": documents_to_ingest}})
            print("Ingestion pipeline finished successfully.")
        except Exception as e:
            print(f"Error during ingestion pipeline execution: {e}")
            _log_unresolved_issue("ingestion_pipeline_failure", str(e), "pipeline_execution")
    else:
        print("No ParsedDocuments found for ingestion.")

if __name__ == "__main__":
    # This block is for standalone testing of this script if needed.
    # In normal operation, run_ingestion.py will call run_ingestion_pipeline.
    print("This script is typically called by run_ingestion.py. Running standalone for testing purposes.")
    
    # Dummy setup for standalone testing
    from meta_context_studio.src.ingestion.data_models import ContentBlockType, DocumentType
    
    dummy_docs = [
        ParsedDocument(
            document_id="test_doc_1",
            document_type=DocumentType.TECHNICAL_REPORT,
            source_path="/tmp/test_doc_1.html",
            metadata={"title": "Test Document 1"},
            content_blocks=[
                ContentBlock(block_type=ContentBlockType.PARAGRAPH, content="This is a test paragraph.", block_index=0, embedding=[0.1, 0.2, 0.3]),
                ContentBlock(block_type=ContentBlockType.PARAGRAPH, content="Another test paragraph.", block_index=1, embedding=[0.4, 0.5, 0.6])
            ]
        )
    ]
    
    document_store = VectorStore(
        uri=str(Path(os.getcwd()) / "meta_context_studio" / "knowledge_base" / "lancedb_test_standalone"),
        table_name="genesis_documents_test"
    )
    document_store.clear_collection() # Clear for clean test run
    run_ingestion_pipeline(dummy_docs, document_store)
    print(f"Total documents in test store: {document_store.count_documents()}")
