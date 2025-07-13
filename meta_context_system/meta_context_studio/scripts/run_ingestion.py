import os
import shutil
from meta_context_studio.src.lancedb_ingestion.ingestion_pipeline import LanceDBIngestionPipeline

def main():
    """Main function to run the ingestion pipeline."""

    # The directory where the documents to be ingested are located.
    ingestion_queue_path = "ingestion_queue"
    db_path = "lancedb_data"

    # Clean up previous database for a fresh start
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
        print(f"Cleaned up existing '{db_path}' directory.")

    # Initialize the LanceDB ingestion pipeline.
    pipeline = LanceDBIngestionPipeline(db_path=db_path)

    # Run the ingestion process.
    pipeline.ingest_from_directory(ingestion_queue_path)

    print("Ingestion process finished.")

if __name__ == "__main__":
    main()
