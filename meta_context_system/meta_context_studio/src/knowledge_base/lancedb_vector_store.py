import lancedb
from lancedb.db import LanceDBConnection
from lancedb.table import LanceTable
from typing import List, Dict, Any, Optional
import os

class LanceDBVectorStore:
    """
    A wrapper class for LanceDB to manage vector store operations.
    """
    def __init__(self, uri: str = "~/.lancedb", table_name: str = "genesis_documents"):
        """
        Initializes the LanceDB connection and table.

        Args:
            uri (str): The connection URI for LanceDB. Defaults to "~/.lancedb" for a local DB.
            table_name (str): The name of the table to use for documents.
        """
        self.uri = os.path.expanduser(uri)
        self.table_name = table_name
        self.db: Optional[LanceDBConnection] = None
        self.table: Optional[LanceTable] = None
        self._connect()

    def _connect(self):
        """Establishes a connection to LanceDB and gets the table."""
        print(f"Attempting to connect to LanceDB at {self.uri}")
        try:
            self.db = lancedb.connect(self.uri)
            print(f"Successfully connected to LanceDB at {self.uri}")
            # Check if the table exists, if not, create it with a dummy schema
            if self.table_name not in self.db.table_names():
                print(f"Table '{self.table_name}' not found. It will be created on first document addition.")
                self.table = None # Will be set on first add or if table already exists
            else:
                self.table = self.db.open_table(self.table_name)
                print(f"Opened existing LanceDB table: {self.table_name}")
        except Exception as e:
            print(f"Error connecting to LanceDB at {self.uri}: {e}")
            self.db = None
            self.table = None

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Adds documents to the LanceDB table.
        If the table does not exist, it will be created with the schema inferred from the first document.

        Args:
            documents (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
                                               represents a document. Each document must contain
                                               at least a 'vector' field (list of floats) and a 'text' field.
        """
        if not self.db:
            print("LanceDB connection not established. Cannot add documents.")
            return

        if not documents:
            print("No documents to add.")
            return

        # Ensure documents have a 'vector' field for LanceDB
        for doc in documents:
            if 'vector' not in doc or not isinstance(doc['vector'], list):
                print(f"Skipping document due to missing or invalid 'vector' field: {doc}")
                continue
            if 'text' not in doc or not isinstance(doc['text'], str):
                print(f"Skipping document due to missing or invalid 'text' field: {doc}")
                continue

        # Filter out invalid documents before insertion attempt
        valid_documents = [doc for doc in documents if 'vector' in doc and isinstance(doc['vector'], list) and 'text' in doc and isinstance(doc['text'], str)]

        if not valid_documents:
            print("No valid documents to add after filtering.")
            return

        try:
            if self.table is None:
                # Create table with inferred schema from the first valid document
                # LanceDB's add method can create the table if it doesn't exist
                self.table = self.db.create_table(self.table_name, data=valid_documents)
                print(f"Table '{self.table_name}' created and documents added.")
            else:
                self.table.add(valid_documents)
                print(f"Added {len(valid_documents)} documents to LanceDB table '{self.table_name}'.")
        except Exception as e:
            print(f"Error adding documents to LanceDB: {e}")

    def count_documents(self) -> int:
        """
        Counts the number of documents in the LanceDB table.

        Returns:
            int: The number of documents. Returns 0 if the table does not exist or an error occurs.
        """
        if not self.db or self.table is None:
            print("LanceDB connection not established or table does not exist. Document count is 0.")
            return 0
        try:
            return self.table.count_rows()
        except Exception as e:
            print(f"Error counting documents in LanceDB: {e}")
            return 0

    def clear_collection(self):
        """
        Deletes the LanceDB table (collection).
        """
        if not self.db:
            print("LanceDB connection not established. Cannot clear collection.")
            return
        try:
            if self.table_name in self.db.table_names():
                self.db.drop_table(self.table_name)
                self.table = None
                print(f"LanceDB table '{self.table_name}' cleared.")
            else:
                print(f"LanceDB table '{self.table_name}' does not exist. Nothing to clear.")
        except Exception as e:
            print(f"Error clearing LanceDB collection: {e}")

    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a vector similarity search on the LanceDB table.

        Args:
            query_vector (List[float]): The vector to query with.
            limit (int): The maximum number of results to return.

        Returns:
            List[Dict[str, Any]]: A list of matching documents, each as a dictionary.
        """
        if not self.table:
            print("LanceDB table not available. Cannot perform search.")
            return []
        try:
            results = self.table.search(query_vector).limit(limit).to_list()
            return results
        except Exception as e:
            print(f"Error during LanceDB search: {e}")
            return []

    def get_all_content_blocks(self) -> List[Dict[str, Any]]:
        """
        Retrieves all content blocks from the LanceDB table.
        Note: This can be memory intensive for very large datasets.

        Returns:
            List[Dict[str, Any]]: A list of all content blocks, each as a dictionary.
        """
        if not self.table:
            print("LanceDB table not available. Cannot retrieve all content blocks.")
            return []
        try:
            # LanceDB does not have a direct 'get all' method like some other vector stores.
            # We can read the entire table as a pandas DataFrame and then convert to a list of dicts.
            # This might be inefficient for very large tables.
            all_data = self.table.to_pandas().to_dict(orient='records')
            return all_data
        except Exception as e:
            print(f"Error retrieving all content blocks from LanceDB: {e}")
            return []

if __name__ == '__main__':
    # Example Usage:
    # Ensure the LanceDB directory is clean for testing
    test_uri = "~/.lancedb_test"
    test_table_name = "test_documents"
    if os.path.exists(os.path.expanduser(test_uri)):
        import shutil
        shutil.rmtree(os.path.expanduser(test_uri))
        print(f"Cleaned up existing test DB at {test_uri}")

    lancedb_store = LanceDBVectorStore(uri=test_uri, table_name=test_table_name)

    # Test adding documents
    docs_to_add = [
        {"vector": [0.1, 0.2, 0.3], "text": "This is the first document."},
        {"vector": [0.4, 0.5, 0.6], "text": "This is the second document."},
        {"vector": [0.7, 0.8, 0.9], "text": "Another document here."},
    ]
    lancedb_store.add_documents(docs_to_add)
    print(f"Documents in store after adding: {lancedb_store.count_documents()}")

    # Test searching
    query_vec = [0.15, 0.25, 0.35]
    search_results = lancedb_store.search(query_vec, limit=2)
    print("Search Results:")
    for res in search_results:
        print(res)

    # Test clearing collection
    lancedb_store.clear_collection()
    print(f"Documents in store after clearing: {lancedb_store.count_documents()}")

    # Test adding more documents after clearing
    more_docs = [
        {"vector": [1.0, 1.1, 1.2], "text": "New document after clear."},
    ]
    lancedb_store.add_documents(more_docs)
    print(f"Documents in store after adding more: {lancedb_store.count_documents()}")

    # Clean up test DB
    if os.path.exists(os.path.expanduser(test_uri)):
        import shutil
        shutil.rmtree(os.path.expanduser(test_uri))
        print(f"Cleaned up test DB at {test_uri}")
