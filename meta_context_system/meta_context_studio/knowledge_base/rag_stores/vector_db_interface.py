"""Interface to vector databases (e.g., Milvus, Weaviate)."""
import chromadb
from typing import List, Dict

class VectorDBInterface:
    """
    Provides an interface to a vector database (ChromaDB).
    """

    def __init__(self, path: str = "./chroma_db"):
        """
        Initializes the VectorDBInterface.

        Args:
            path: The path to the ChromaDB persistent directory.
        """
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name="knowledge_embeddings")
        print(f"VectorDBInterface: Connected to ChromaDB at {path}")

    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadatas: List[Dict] = None, ids: List[str] = None):
        """
        Adds documents and their embeddings to the vector database.

        Args:
            documents: A list of document texts.
            embeddings: A list of embedding vectors corresponding to the documents.
            metadatas: Optional list of metadata dictionaries for each document.
            ids: Optional list of unique IDs for each document.
        """
        if ids is None:
            ids = [f"doc{i}" for i in range(len(documents))]
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"VectorDBInterface: Added {len(documents)} documents.")

    def query_documents(self, query_embeddings: List[List[float]], n_results: int = 5) -> List[Dict]:
        """
        Queries the vector database for similar documents.

        Args:
            query_embeddings: A list of embedding vectors for the query.
            n_results: The number of nearest neighbors to return.

        Returns:
            A list of dictionaries, each containing document, embedding, metadata, and distance.
        """
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            include=['documents', 'distances', 'metadatas']
        )
        return results['documents']