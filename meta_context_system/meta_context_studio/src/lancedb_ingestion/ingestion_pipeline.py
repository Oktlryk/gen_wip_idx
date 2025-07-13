import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Dict, List

import lancedb
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
)
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from lancedb.pydantic import LanceModel, Vector
from pydantic import Field

from meta_context_studio.config import settings

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# --- Pydantic Schema for LanceDB ---
# This defines the structure of our data, ensuring consistency.
# It can be moved to a central schema.py file as the project grows.
class LanceDBSchema(LanceModel):
    # Based on Google's 'embedding-001' model, which has 768 dimensions.
    vector: Vector(768) = Field(doc="The vector embedding of the text chunk.")
    text: str = Field(doc="The text content of the document chunk.")
    source: str = Field(doc="The source file path of the document.")


class LanceDBIngestionPipeline:
    """
    A high-performance, extensible pipeline for ingesting documents into LanceDB.

    Features:
    - Extensible loader registry for various file types (.html, .md, .txt, etc.).
    - Parallel processing for file loading and chunking to maximize performance.
    - Batching for embedding generation and database writes to improve efficiency.
    - Pydantic-based schema for data validation and consistency.
    """

    def __init__(
        self,
        db_path: str,
        table_name: str,
        embedding_model_name: str = "models/embedding-001",
    ):
        self.db_path = db_path
        self.table_name = table_name
        self.db = lancedb.connect(db_path)

        # Create or open the LanceDB table with the defined schema
        try:
            self.table = self.db.open_table(table_name)
        except FileNotFoundError:
            logging.info(f"Table '{table_name}' not found. Creating new table.")
            self.table = self.db.create_table(table_name, schema=LanceDBSchema)

        # Setup text splitter for intelligent chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

        # Initialize the embedding model
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name, google_api_key=settings.LLM_API_KEYS["gemini"]
        )

        # --- Extensible Loader Registry ---
        # Easily add support for new file types here.
        self.loader_registry: Dict[str, Callable[..., Any]] = {
            ".html": UnstructuredHTMLLoader,
            ".htm": UnstructuredHTMLLoader,
            ".md": UnstructuredMarkdownLoader,
            ".txt": TextLoader,
            ".py": TextLoader,  # Treat code as plain text
            # Add more loaders as needed, e.g., for .pdf, .docx
        }

    def _get_loader(self, file_path: str) -> Callable | None:
        """Returns the appropriate loader based on the file extension."""
        ext = Path(file_path).suffix.lower()
        return self.loader_registry.get(ext)

    def _process_file(self, file_path: str) -> List[Dict]:
        """
        Loads a single file, chunks it, and prepares it for embedding.
        This function is designed to be run in a separate process.
        """
        loader_cls = self._get_loader(file_path)
        if not loader_cls:
            logging.warning(f"No loader found for '{Path(file_path).name}', skipping.")
            return []

        try:
            loader = loader_cls(file_path, autodetect_encoding=True)
            docs = loader.load()
            chunks = self.text_splitter.split_documents(docs)

            # Prepare data for batch embedding
            chunk_data = [
                {"text": chunk.page_content, "source": str(Path(file_path).resolve())}
                for chunk in chunks
            ]
            return chunk_data
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}", exc_info=True)
            return []

    def ingest_files(self, file_paths: List[str], batch_size: int = 100):
        """
        Ingests a list of files into the LanceDB knowledge base.
        """
        all_chunks = []
        logging.info(f"Starting ingestion for {len(file_paths)} files...")

        # Use a process pool to load and chunk files in parallel
        with ProcessPoolExecutor() as executor:
            future_to_file = {
                executor.submit(self._process_file, fp): fp for fp in file_paths
            }
            for future in as_completed(future_to_file):
                try:
                    chunks = future.result()
                    if chunks:
                        all_chunks.extend(chunks)
                except Exception as e:
                    logging.error(f"A file processing task failed: {e}")

        if not all_chunks:
            logging.info("No new document chunks were generated.")
            return

        logging.info(f"Generated {len(all_chunks)} chunks. Starting embedding...")

        # Batch embed all chunks
        texts_to_embed = [chunk["text"] for chunk in all_chunks]
        embeddings = self.embedding_model.embed_documents(texts_to_embed)

        # Add embeddings to chunks
        for i, chunk in enumerate(all_chunks):
            chunk["vector"] = embeddings[i]

        logging.info("Embedding complete. Writing to LanceDB...")

        # Batch write to LanceDB
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            try:
                self.table.add(batch)
            except Exception as e:
                logging.error(f"Failed to add batch to LanceDB: {e}")

        logging.info(f"Successfully ingested {len(all_chunks)} chunks into the KB.")