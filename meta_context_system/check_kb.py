import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from meta_context_studio.src.knowledge_base.vector_store import VectorStore

def check_kb_count():
    try:
        # Initialize VectorStore with the correct path to the ChromaDB instance
        # This path should match the default in VectorStore or the one used during ingestion
        vector_store = VectorStore(path="meta_context_studio/knowledge_base/chroma_db")
        
        count = vector_store.count_documents()
        print(f"Number of documents in the knowledge base: {count}")
    except Exception as e:
        print(f"Error checking knowledge base: {e}")

if __name__ == "__main__":
    check_kb_count()
