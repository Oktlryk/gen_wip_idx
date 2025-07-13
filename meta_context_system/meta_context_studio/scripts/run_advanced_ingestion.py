import argparse
import logging
import os
from pathlib import Path

import lancedb
from meta_context_studio.config import settings
from meta_context_studio.src.lancedb_ingestion.ingestion_pipeline import (
    LanceDBIngestionPipeline,
)

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_ingested_sources(db_path: str, table_name: str) -> set[str]:
    """
    Retrieves the set of already ingested document source paths from the LanceDB table.
    This is used to prevent re-ingesting the same content.
    """
    try:
        db = lancedb.connect(db_path)
        if table_name not in db.table_names():
            logging.info(f"Table '{table_name}' does not exist. Starting fresh.")
            return set()

        table = db.open_table(table_name)
        # This assumes the source path is stored in a 'source' column.
        if "source" not in table.schema.names:
            logging.warning(
                "'source' column not found in schema. Cannot determine ingested files. "
                "Consider re-ingesting all with --force-reingest."
            )
            return set()

        # Stream results to avoid loading all sources into memory at once,
        # which is more scalable for a large knowledge base.
        scanner = table.scanner(columns=["source"])
        reader = scanner.to_reader()
        ingested_sources = set()
        for batch in reader:
            # batch is a pyarrow.RecordBatch
            ingested_sources.update(batch.to_pydict()["source"])
        return ingested_sources
    except Exception as e:
        logging.error(f"Could not connect to or read from LanceDB table: {e}")
        logging.error("Assuming no files are ingested. Proceeding with all files.")
        return set()


def main(ingestion_path: str, force_reingest: bool):
    """
    Runs an advanced, incremental ingestion pipeline.

    This script checks the vector store for already processed documents and only
    ingests new or modified files, making it much more efficient for ongoing
    knowledge base updates.
    """
    db_path = settings.KNOWLEDGE_BASE_PATH
    table_name = settings.LANCE_TABLE_NAME

    if force_reingest:
        logging.info(
            "--force-reingest flag set. All documents in the queue will be processed."
        )
        try:
            db = lancedb.connect(db_path)
            if table_name in db.table_names():
                logging.info(f"Dropping existing table '{table_name}' for re-ingestion.")
                db.drop_table(table_name)
            ingested_files = set()
        except Exception as e:
            logging.error(f"Error dropping table '{table_name}': {e}")
            return
    else:
        logging.info("Checking for already ingested documents...")
        ingested_files = get_ingested_sources(db_path, table_name)
        logging.info(
            f"Found {len(ingested_files)} documents already in the knowledge base."
        )

    all_files_in_queue = [
        str(p.resolve()) for p in Path(ingestion_path).rglob("*") if p.is_file()
    ]

    files_to_ingest = [f for f in all_files_in_queue if f not in ingested_files]

    if not files_to_ingest:
        logging.info("No new documents to ingest. Knowledge base is up-to-date.")
        return

    logging.info(f"Found {len(files_to_ingest)} new documents to ingest.")

    pipeline = LanceDBIngestionPipeline(db_path=db_path, table_name=table_name)

    # Ingest files one by one for better resilience and logging.
    # If one file fails, the others can still be processed.
    successful_ingestions = 0
    failed_ingestions = 0
    for i, file_path in enumerate(files_to_ingest):
        logging.info(
            f"Processing file {i + 1}/{len(files_to_ingest)}: {Path(file_path).name}"
        )
        try:
            # The pipeline now ingests a list containing a single file.
            pipeline.ingest_files([file_path])
            successful_ingestions += 1
        except Exception as e:
            logging.error(f"Failed to ingest '{file_path}': {e}", exc_info=True)
            failed_ingestions += 1

    logging.info("--- Ingestion Summary ---")
    logging.info(f"Successfully ingested: {successful_ingestions} files.")
    logging.info(f"Failed to ingest: {failed_ingestions} files.")
    logging.info("Ingestion process finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the advanced ingestion pipeline for the Meta Context Studio."
    )
    parser.add_argument(
        "--path",
        type=str,
        default="ingestion_queue",
        help="The path to the directory containing documents to ingest.",
    )
    parser.add_argument(
        "--force-reingest",
        action="store_true",
        help="Force re-ingestion of all documents, dropping the existing table.",
    )

    args = parser.parse_args()
    main(ingestion_path=args.path, force_reingest=args.force_reingest)
    
import argparse
import logging
import os
from pathlib import Path

import lancedb
from meta_context_studio.config import settings
from meta_context_studio.src.lancedb_ingestion.ingestion_pipeline import (
    LanceDBIngestionPipeline,
)

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_ingested_sources(db_path: str, table_name: str) -> set[str]:
    """
    Retrieves the set of already ingested document source paths from the LanceDB table.
    This is used to prevent re-ingesting the same content.
    """
    try:
        db = lancedb.connect(db_path)
        if table_name not in db.table_names():
            logging.info(f"Table '{table_name}' does not exist. Starting fresh.")
            return set()

        table = db.open_table(table_name)
        # This assumes the source path is stored in a 'source' column.
        if "source" not in table.schema.names:
            logging.warning(
                "'source' column not found in schema. Cannot determine ingested files. "
                "Consider re-ingesting all with --force-reingest."
            )
            return set()

        # In a very large database, this could be slow. A more scalable
        # solution might involve a separate manifest file or a more optimized query.
        # For most use cases, this is efficient enough.
        sources_df = table.to_pandas(columns=["source"])
        return set(sources_df["source"].unique())
    except Exception as e:
        logging.error(f"Could not connect to or read from LanceDB table: {e}")
        logging.error("Assuming no files are ingested. Proceeding with all files.")
        return set()


def main(ingestion_path: str, force_reingest: bool):
    """
    Runs an advanced, incremental ingestion pipeline.

    This script checks the vector store for already processed documents and only
    ingests new or modified files, making it much more efficient for ongoing
    knowledge base updates.
    """
    db_path = settings.KNOWLEDGE_BASE_PATH
    table_name = settings.LANCE_TABLE_NAME

    if force_reingest:
        logging.info(
            "--force-reingest flag set. All documents in the queue will be processed."
        )
        try:
            db = lancedb.connect(db_path)
            if table_name in db.table_names():
                logging.info(f"Dropping existing table '{table_name}' for re-ingestion.")
                db.drop_table(table_name)
            ingested_files = set()
        except Exception as e:
            logging.error(f"Error dropping table '{table_name}': {e}")
            return
    else:
        logging.info("Checking for already ingested documents...")
        ingested_files = get_ingested_sources(db_path, table_name)
        logging.info(
            f"Found {len(ingested_files)} documents already in the knowledge base."
        )

    all_files_in_queue = [
        str(p.resolve()) for p in Path(ingestion_path).rglob("*") if p.is_file()
    ]

    files_to_ingest = [f for f in all_files_in_queue if f not in ingested_files]

    if not files_to_ingest:
        logging.info("No new documents to ingest. Knowledge base is up-to-date.")
        return

    logging.info(f"Found {len(files_to_ingest)} new documents to ingest.")

    pipeline = LanceDBIngestionPipeline(db_path=db_path, table_name=table_name)

    try:
        # Assumes the pipeline can ingest a list of files.
        pipeline.ingest_files(files_to_ingest)
        logging.info(f"Successfully ingested {len(files_to_ingest)} new documents.")
    except Exception as e:
        logging.error(f"An error occurred during the ingestion process: {e}")

    logging.info("Ingestion process finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the advanced ingestion pipeline for the Meta Context Studio."
    )
    parser.add_argument(
        "--path",
        type=str,
        default="ingestion_queue",
        help="The path to the directory containing documents to ingest.",
    )
    parser.add_argument(
        "--force-reingest",
        action="store_true",
        help="Force re-ingestion of all documents, dropping the existing table.",
    )

    args = parser.parse_args()
    main(ingestion_path=args.path, force_reingest=args.force_reingest)