from typing import List
from sentence_transformers import SentenceTransformer
from meta_context_studio.src.ingestion.data_models import ParsedDocument, ContentBlock

class DocumentInterpreter:
    """
    Interprets a ParsedDocument to extract structured information and potentially enrich it.
    This class is designed to be extended for more complex interpretation tasks,
    such as entity extraction, relationship extraction, and embedding generation.
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        print(f"DocumentInterpreter: Initializing SentenceTransformer model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        print("DocumentInterpreter: SentenceTransformer model loaded.")

    def interpret_document(self, parsed_document: ParsedDocument) -> ParsedDocument:
        """
        Processes a ParsedDocument to extract and enrich information.
        This method now generates embeddings for each content block.
        """
        print(f"DocumentInterpreter: Interpreting document {parsed_document.document_id} with {len(parsed_document.content_blocks)} content blocks.")
        for i, block in enumerate(parsed_document.content_blocks):
            if not block.content or not block.content.strip():
                print(f"Warning: Skipping embedding generation for empty content block {i} in document {parsed_document.document_id}.")
                block.embedding = None
                continue
            try:
                block.embedding = self._generate_embeddings(block.content)
                print(f"Debug: Generated embedding for block {i} (content length: {len(block.content)}). Embedding is not None: {block.embedding is not None}")
            except Exception as e:
                print(f"Warning: Could not generate embedding for block {i} in document {parsed_document.document_id}. Error: {e}")
                block.embedding = None
        
        # In a real scenario, you might also:
        # 2. Perform Named Entity Recognition (NER)
        # 3. Extract relationships between entities
        # 4. Classify content blocks further

        return parsed_document

    def _generate_embeddings(self, text: str) -> List[float]:
        """
        Generates embeddings for the given text using the loaded SentenceTransformer model.
        """
        # The encode method returns a numpy array, convert to list for Pydantic compatibility
        return self.embedding_model.encode(text).tolist()
