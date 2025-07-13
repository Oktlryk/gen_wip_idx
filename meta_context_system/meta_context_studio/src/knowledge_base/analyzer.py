import os
import json
from typing import List, Dict, Optional

import lancedb
import google.generativeai as genai
from pydantic import ValidationError

from meta_context_studio.src.ingestion.data_models import ParsedDocument, ReportRequest, DocumentType
from meta_context_studio.src.utils.prompt_loading import load_prompt_template
from meta_context_studio.config import settings

class KnowledgeBaseAnalyzer:
    """
    Analyzes the existing knowledge base to identify gaps, inconsistencies, or
    areas requiring further information, and generates ReportRequest objects.
    """
    def __init__(self, knowledge_base_uri: Optional[str] = None, table_name: Optional[str] = None):
        """
        Initializes the analyzer.

        Args:
            knowledge_base_uri (Optional[str]): Path to the LanceDB database.
                Defaults to the path in the project settings.
            table_name (Optional[str]): Name of the table to analyze.
                Defaults to the table name in the project settings.
        """
        # Use provided values or fall back to central settings for consistency.
        self.knowledge_base_uri = knowledge_base_uri or settings.KNOWLEDGE_BASE_PATH
        self.table_name = table_name or settings.LANCE_TABLE_NAME

        self.db = lancedb.connect(self.knowledge_base_uri)
        self.analyzed_documents: List[ParsedDocument] = []

        # The GEMINI_API_KEY is handled by a compatibility patch in run_kb_analyzer.py,
        # but we still need to configure the genai library.
        # The patch ensures settings.GEMINI_API_KEY exists.
        if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found. Please configure it in your settings or .env file.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Configure the model to use JSON output mode for reliable parsing.
        self.model = genai.GenerativeModel(
            'models/gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"})

    def load_knowledge_base(self) -> None:
        """Loads all documents from the LanceDB table for analysis."""
        print(f"Loading knowledge base from LanceDB at {self.knowledge_base_uri}...")
        try:
            table = self.db.open_table(self.table_name)
            all_docs_df = table.to_pandas()
        except Exception as e:
            # This can happen if the table doesn't exist yet.
            print(f"Could not open or read table '{self.table_name}': {e}. Assuming knowledge base is empty.")
            self.analyzed_documents = []
            return

        # The LanceDB table stores chunks, not whole documents. We need to reconstruct
        # a representation of each unique document for analysis, primarily using its metadata.
        # The `identify_knowledge_gaps` method only needs the metadata.

        documents_map: Dict[str, Dict[str, Any]] = {}
        for _, row in all_docs_df.iterrows():
            # Ingestion pipelines (like Haystack's) often store chunk-level
            # metadata in a single 'meta' column, which is a dictionary.
            meta = row.get('metadata', {}) # LanceDB pandas export uses 'metadata' column
            if not isinstance(meta, dict):
                # If 'meta' column doesn't exist or isn't a dict, skip this row.
                continue

            doc_id = meta.get('document_id')
            if not doc_id or doc_id in documents_map:
                continue # Skip if no ID or if we've already created the document entry

            # Reconstruct a ParsedDocument object for analysis.
            # We only need the metadata for the current analysis logic.
            # The document's own metadata is now directly in the 'meta' field from the chunk.
            document_metadata = meta

            documents_map[doc_id] = ParsedDocument(
                document_id=doc_id,
                document_type=DocumentType(meta.get('document_type', 'unknown')),
                source_path=meta.get('source_path', 'unknown'),
                metadata=document_metadata,
                content_blocks=[] # Content/content_blocks not needed for this analysis
            )

        self.analyzed_documents = list(documents_map.values())
        print(f"Loaded and reconstructed {len(self.analyzed_documents)} unique documents for analysis.")

    def identify_knowledge_gaps(self) -> List[ReportRequest]:
        """
        Uses an LLM to analyze existing document titles and dynamically propose
        a new, relevant research topic to fill a knowledge gap.
        """
        print("Dynamically identifying knowledge gaps using an LLM...")
        report_requests: List[ReportRequest] = []

        if not self.analyzed_documents:
            print("Knowledge base is empty. Cannot identify gaps.")
            return report_requests

        known_titles = [doc.metadata.get("title", doc.source_path) for doc in self.analyzed_documents]
        titles_list_str = "\n - ".join(known_titles)

        # Load the prompt from an external file for better maintainability
        prompt_template = load_prompt_template("knowledge_gap_analyzer.md")
        if not prompt_template:
            return report_requests
        
        prompt = prompt_template.format(titles_list_str=titles_list_str)

        try:
            response = self.model.generate_content(prompt)
            report_data = json.loads(response.text)
            request = ReportRequest(**report_data)
            report_requests.append(request)
            print(f"LLM proposed a new report request: '{request.requested_topic}'")

        except (json.JSONDecodeError, KeyError, ValidationError) as e:
            print(f"Error processing LLM response: {e}")
            print(f"LLM raw response:\n{response.text}")
        except Exception as e:
            print(f"An unexpected error occurred while generating report request: {e}")

        return report_requests

    def generate_report_requests(self) -> List[ReportRequest]:
        """
        Main method to run the analysis and generate report requests.
        """
        self.load_knowledge_base()
        requests = self.identify_knowledge_gaps()
        return requests
