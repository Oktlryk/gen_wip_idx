import os
import sys
import shutil
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import os
import sys
import shutil
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from meta_context_studio.scripts.data_ingestion_pipeline import _log_unresolved_issue, run_ingestion_pipeline
from haystack_integrations.document_stores.chroma import ChromaDocumentStore
from meta_context_studio.config import settings

@pytest.fixture(autouse=True)
def setup_and_teardown_ingestion_queue():
    ingestion_queue_path = Path(os.getcwd()) / "meta_context_studio" / "ingestion_queue"
    chroma_persist_path = str(Path(os.getcwd()) / "meta_context_studio" / "knowledge_base" / "chroma_db")

    # Initialize ChromaDB Document Store for persistence
    document_store = ChromaDocumentStore(
        collection_name="genesis_documents",
        persist_path=chroma_persist_path
    )

    # Setup: Create a temporary ingestion queue directory
    os.makedirs(ingestion_queue_path, exist_ok=True)
    
    # Clear unresolved_issues directory
    unresolved_dir = Path(os.getcwd()) / "unresolved_issues"
    if os.path.exists(unresolved_dir):
        shutil.rmtree(unresolved_dir)
    os.makedirs(unresolved_dir, exist_ok=True)

    # Ensure ChromaDB collection is empty before each test
    all_doc_ids = [doc.id for doc in document_store.filter_documents()]
    if all_doc_ids:
        document_store.delete_documents(document_ids=all_doc_ids)

    yield ingestion_queue_path, document_store

    # Teardown: Remove the temporary ingestion queue directory
    if os.path.exists(ingestion_queue_path):
        shutil.rmtree(ingestion_queue_path)
    
    # Clear ChromaDB collection after each test
    all_doc_ids = [doc.id for doc in document_store.filter_documents()]
    if all_doc_ids:
        document_store.delete_documents(document_ids=all_doc_ids)
    
    # Clean up unresolved_issues directory after tests
    if os.path.exists(unresolved_dir):
        shutil.rmtree(unresolved_dir)

def test_log_unresolved_issue():
    """
    Test the _log_unresolved_issue function.
    """
    issue_type = "test_error"
    error_message = "This is a test error message."
    file_path = "/test/path/to/file.txt"

    _log_unresolved_issue(issue_type, error_message, file_path)

    unresolved_dir = Path(os.getcwd()) / "unresolved_issues"
    assert unresolved_dir.exists()

    # Check if a log file was created (we can't predict the timestamp)
    log_files = list(unresolved_dir.glob(f"{issue_type}_{os.path.basename(file_path)}*.log"))
    assert len(log_files) == 1

    with open(log_files[0], 'r') as f:
        content = f.read()
        assert "Timestamp:" in content
        assert f"File Path: {file_path}" in content
        assert f"Error: {error_message}" in content
        assert f"Action: {issue_type} failed." in content

def test_ingestion_pipeline_empty_queue(setup_and_teardown_ingestion_queue):
    """
    Test the ingestion pipeline with an empty queue.
    """
    ingestion_queue_path, document_store = setup_and_teardown_ingestion_queue
    with patch('builtins.print') as mock_print:
        run_ingestion_pipeline(ingestion_queue_path, document_store)
        mock_print.assert_any_call("No new files found in ingestion queue.")
        assert document_store.count_documents() == 0

def test_ingestion_pipeline_html_file(setup_and_teardown_ingestion_queue):
    """
    Test ingestion of a single HTML file.
    """
    ingestion_queue_path, document_store = setup_and_teardown_ingestion_queue
    dummy_html_file = ingestion_queue_path / "dummy.html"
    with open(dummy_html_file, 'w') as f:
        f.write("<html><body><h1>Test HTML</h1><p>This is a test HTML document.</p></body></html>")

    with patch('builtins.print') as mock_print:
        run_ingestion_pipeline(ingestion_queue_path, document_store)
        mock_print.assert_any_call(f"Found 1 files to ingest. Starting pipeline...")
        mock_print.assert_any_call("Ingestion pipeline finished successfully.")
        assert document_store.count_documents() > 0
        # Further assertions could check content of ingested documents in ChromaDB

def test_ingestion_pipeline_markdown_file(setup_and_teardown_ingestion_queue):
    """
    Test ingestion of a single Markdown file.
    """
    ingestion_queue_path, document_store = setup_and_teardown_ingestion_queue
    dummy_md_file = ingestion_queue_path / "dummy.md"
    with open(dummy_md_file, 'w') as f:
        f.write("# Test Markdown\n\nThis is a test Markdown document.")

    with patch('builtins.print') as mock_print:
        run_ingestion_pipeline(ingestion_queue_path, document_store)
        mock_print.assert_any_call(f"Found 1 files to ingest. Starting pipeline...")
        mock_print.assert_any_call("Ingestion pipeline finished successfully.")
        assert document_store.count_documents() > 0

def test_ingestion_pipeline_mixed_files(setup_and_teardown_ingestion_queue):
    """
    Test ingestion of mixed HTML and Markdown files.
    """
    ingestion_queue_path, document_store = setup_and_teardown_ingestion_queue
    dummy_html_file = ingestion_queue_path / "dummy1.html"
    with open(dummy_html_file, 'w') as f:
        f.write("<html><body><h1>Test HTML 1</h1></body></html>")

    dummy_md_file = ingestion_queue_path / "dummy1.md"
    with open(dummy_md_file, 'w') as f:
        f.write("# Test Markdown 1")

    with patch('builtins.print') as mock_print:
        run_ingestion_pipeline(ingestion_queue_path, document_store)
        mock_print.assert_any_call(f"Found 2 files to ingest. Starting pipeline...")
        mock_print.assert_any_call("Ingestion pipeline finished successfully.")
        assert document_store.count_documents() > 0

def test_ingestion_pipeline_error_handling(setup_and_teardown_ingestion_queue):
    """
    Test error handling in the ingestion pipeline.
    """
    ingestion_queue_path, document_store = setup_and_teardown_ingestion_queue
    # Simulate an error by making a component fail
    # Simulate an error by making a component fail
    with patch('haystack.components.writers.DocumentWriter.run') as mock_run:
        mock_run.side_effect = Exception("Simulated write error")
        dummy_md_file = ingestion_queue_path / "error.md"
        with open(dummy_md_file, 'w') as f:
            f.write("# This will cause an error")

        with patch('builtins.print') as mock_print:
            run_ingestion_pipeline(ingestion_queue_path, document_store)
            unresolved_dir = Path(os.getcwd()) / "unresolved_issues"
            assert unresolved_dir.exists()
            log_files = list(unresolved_dir.glob(f"ingestion_pipeline_failure_error.md*.log"))
            assert len(log_files) == 1