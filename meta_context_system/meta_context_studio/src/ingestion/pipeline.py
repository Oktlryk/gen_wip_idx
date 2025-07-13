import os
import hashlib
from typing import Optional, List
import inspect
import sys

from meta_context_studio.src.ingestion.data_models import ParsedDocument, DocumentType
from meta_context_studio.src.ingestion.parsers.html_parser import parse_html_document
from meta_context_studio.src.ingestion.interpreters.document_interpreter import DocumentInterpreter
from meta_context_studio.src.utils.error_reporting import generate_error_report

from meta_context_studio.src.knowledge_base.graph_store import GraphStore
from meta_context_studio.src.agent_orchestration.knowledge_graph_update_agent import KnowledgeGraphUpdateAgent
from meta_context_studio.src.lancedb_ingestion.ingestion_pipeline import LanceDBIngestionPipeline # New import

class IngestionPipeline:
    """
    Orchestrates the document ingestion process, including parsing, interpretation,
    idempotency checks, and managing a staging area.
    """
    def __init__(self, ingestion_queue_path: str, processed_files_log: str, staging_area_path: str):
        print("IngestionPipeline: __init__ called.")
        self.ingestion_queue_path = ingestion_queue_path
        self.processed_files_log = processed_files_log
        self.staging_area_path = staging_area_path
        self.document_interpreter = DocumentInterpreter()
        self.lancedb_pipeline = LanceDBIngestionPipeline() # Initialize LanceDBIngestionPipeline
        self.graph_store = GraphStore() # Initialize GraphStore
        self.knowledge_graph_update_agent = KnowledgeGraphUpdateAgent(graph_store=self.graph_store) # Initialize KnowledgeGraphUpdateAgent

    def _calculate_document_hash(self, file_path: str) -> str:
        """Calculates the SHA256 hash of a file's content, ensuring consistent encoding."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _is_document_processed(self, document_hash: str) -> bool:
        """
        Checks if a document with the given hash has already been processed.
        This is a simplified check; a real system might use a database.
        """
        if not os.path.exists(self.processed_files_log):
            return False
        with open(self.processed_files_log, 'r') as f:
            for line in f:
                if document_hash in line:
                    return True
        return False

    def _mark_document_as_processed(self, document_hash: str, file_path: str):
        """Records the hash and path of a processed document."""
        with open(file_path, 'a') as f:
            f.write(f"{document_hash},{file_path}\n")

    def ingest_document(self, file_path: str, document_type: DocumentType) -> Optional[ParsedDocument]:
        """
        Ingests a single document, processes it, and returns a ParsedDocument.
        Returns None if the document has already been processed.
        """
        print(f"Attempting to ingest: {file_path}")
        document_hash = self._calculate_document_hash(file_path)

        if self._is_document_processed(document_hash):
            print(f"Document {file_path} (hash: {document_hash}) already processed. Skipping.")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            source_content = f.read()

        # Parse the document
        if document_type == DocumentType.TECHNICAL_REPORT or document_type == DocumentType.PHILOSOPHY_GUIDELINE:
            parsed_document = parse_html_document(file_path, document_type, source_content)
        else:
            raise ValueError(f"Unsupported document type: {document_type}")

        # Interpret the document
        interpreted_document = self.document_interpreter.interpret_document(parsed_document)

        # Add to graph store
        self.graph_store.add_document_to_graph(interpreted_document)

        # Ingest into LanceDB
        self.lancedb_pipeline.ingest_documents([{"text": block.content, "vector": block.embedding, "metadata": block.metadata} for block in interpreted_document.content_blocks if block.embedding is not None])

        # Mark as processed
        self._mark_document_as_processed(document_hash, file_path)

        # Move to staging area (simplified: in a real system, this would involve writing to a DB)
        # For now, we'll just print a message.
        print(f"Document {file_path} successfully ingested and moved to staging area.")

        return interpreted_document

    def run_ingestion_pipeline(self, file_paths: List[str]) -> List[ParsedDocument]:
        """
        Runs the ingestion pipeline, processing the provided file paths.
        Returns a list of ParsedDocument objects with embeddings.
        """
        print("IngestionPipeline: run_ingestion_pipeline called.")
        print(f"Starting ingestion pipeline for {len(file_paths)} files.")
        
        processed_documents: List[ParsedDocument] = [] # List to collect ParsedDocuments for graph update and LanceDB

        for file_path in file_paths:
            if os.path.isfile(file_path):
                # Determine document type based on filename or other heuristics
                filename = os.path.basename(file_path)
                if "genesis_engine_philosophy" in filename.lower() or "orchestral_conductors" in filename.lower() or "context_engineering_dev_studio" in filename.lower():
                    doc_type = DocumentType.PHILOSOPHY_GUIDELINE
                else:
                    doc_type = DocumentType.TECHNICAL_REPORT

                try:
                    interpreted_document = self.ingest_document(file_path, doc_type)
                    if interpreted_document:
                        processed_documents.append(interpreted_document) # For graph update and LanceDB

                except Exception as e:
                    # Get code context for error reporting
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    # Get the filename where the exception occurred
                    frame = exc_tb.tb_frame
                    while frame.f_code.co_filename != os.path.abspath(__file__):
                        frame = frame.f_back
                        if frame is None: # Should not happen if error is within this file
                            break
                    
                    if frame: # Ensure frame is not None
                        lineno = frame.f_lineno
                        lines, start_lineno = inspect.getsourcelines(frame.f_code)
                        snippet = "".join(lines[max(0, lineno - start_lineno - 3):lineno - start_lineno + 2])
                        function_name = frame.f_code.co_name
                    else:
                        lineno = "N/A"
                        snippet = "N/A"
                        function_name = "N/A"

                    error_report_path = generate_error_report(
                        summary=f"Ingestion pipeline failed for {filename} due to {type(e).__name__}",
                        error=e,
                        code_context={
                            "file": os.path.abspath(__file__),
                            "function": function_name,
                            "snippet": snippet,
                            "agent_name": "IngestionAgent"
                        },
                        reproduction_steps={
                            "command": f"python {os.path.join(os.getcwd(), 'meta_context_studio/scripts/run_ingestion.py')}",
                            "input_file": os.path.abspath(file_path),
                            "intended_vs_actual": f"The ingestion pipeline was intended to process {filename} but encountered an error."
                        },
                        key_dependencies=[
                            "haystack-ai", "lancedb", "pyarrow", "sentence-transformers",
                            "markdown-it-py", "beautifulsoup4", "lxml", "fastapi",
                            "uvicorn", "langchain", "pydantic", "rdflib"
                        ]
                    )
                    print(f"Error processing {filename}. A detailed report has been generated at: {error_report_path}")
        
        # After processing all documents, validate and merge them into the knowledge graph
        self.knowledge_graph_update_agent.validate_and_merge(processed_documents)
        print("Ingestion pipeline finished.")
        return processed_documents # Return processed documents for further use (e.g., Haystack pipeline)
