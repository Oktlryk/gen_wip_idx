"""Stores KG embeddings for RAG."""
from typing import List, Dict
from meta_context_studio.src.context_management.modeling.knowledge_graph_engine import KnowledgeGraphEngine
from meta_context_studio.src.context_management.modeling.embedding_generator import EmbeddingGenerator
from meta_context_studio.knowledge_base.rag_stores.vector_db_interface import VectorDBInterface

class KnowledgeGraphStore:
    """
    Manages the storage and retrieval of knowledge graph data for RAG.
    """

    def __init__(self, kg_engine: KnowledgeGraphEngine, embedding_generator: EmbeddingGenerator, vector_db: VectorDBInterface):
        """
        Initializes the KnowledgeGraphStore.

        Args:
            kg_engine: An instance of KnowledgeGraphEngine.
            embedding_generator: An instance of EmbeddingGenerator.
            vector_db: An instance of VectorDBInterface.
        """
        self.kg_engine = kg_engine
        self.embedding_generator = embedding_generator
        self.vector_db = vector_db
        print("KnowledgeGraphStore: Initialized.")

    def add_knowledge(self, text: str, metadata: Dict = None):
        """
        Adds text-based knowledge to the store, generating embeddings and storing in vector DB.

        Args:
            text: The text content to add.
            metadata: Optional metadata associated with the text.
        """
        embedding = self.embedding_generator.generate_embedding(text)
        self.vector_db.add_documents(documents=[text], embeddings=[embedding], metadatas=[metadata or {}])
        print(f"KnowledgeGraphStore: Added knowledge: {text[:50]}...")

    def retrieve_relevant_knowledge(self, query: str, n_results: int = 5) -> List[str]:
        """
        Retrieves relevant knowledge from the store based on a query.

        Args:
            query: The query string.
            n_results: Number of relevant documents to retrieve.

        Returns:
            A list of relevant text snippets.
        """
        query_embedding = self.embedding_generator.generate_embedding(query)
        results = self.vector_db.query_documents(query_embeddings=[query_embedding], n_results=n_results)
        return [doc for doc in results[0]]