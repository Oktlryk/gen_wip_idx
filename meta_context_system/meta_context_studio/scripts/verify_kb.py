# meta_context_studio/scripts/verify_kb.py
"""A simple script to verify the state of the LanceDB knowledge base."""

import lancedb
from meta_context_studio.config import settings


def verify_knowledge_base():
    """Connects to LanceDB and prints a status report."""
    try:
        db = lancedb.connect(settings.KNOWLEDGE_BASE_PATH)
        # Assumes LANCE_TABLE_NAME is defined in your settings
        table = db.open_table(settings.LANCE_TABLE_NAME)
        print(f"Successfully connected to table '{settings.LANCE_TABLE_NAME}'.")
        print(f"Table contains {len(table)} rows.")
        if len(table) > 0:
            print("\nSample record:\n", table.limit(1).to_pandas())
    except Exception as e:
        print(f"Error: Could not connect to or read the LanceDB table: {e}")
        print("This likely means the ingestion process has not been run or has failed.")


if __name__ == "__main__":
    verify_knowledge_base()