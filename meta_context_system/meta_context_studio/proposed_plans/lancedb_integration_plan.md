# Integration Plan: Utilizing the LanceDB Knowledge Base

**Objective:** To integrate the LanceDB-powered vector store into the Genesis Engine's core workflow, enabling agents to retrieve and utilize unstructured knowledge for task execution.

This plan transitions the project from research and data ingestion to active utilization of the knowledge base by the agentic system.

---

### Key Component: `ContextRetriever`

A new, dedicated class will be created to handle all interactions with the unstructured knowledge base.

-   **Location:** `meta_context_studio/src/context_management/retrieval/context_retriever.py`
-   **Purpose:** This class will serve as the primary, standardized interface for any agent needing to perform semantic searches.
-   **Mechanism:** It will leverage the existing `LanceDBIngestionPipeline.search()` method to query the vector store.
-   **Responsibility:** It will be responsible for taking a natural language query, retrieving the most relevant document chunks, and formatting them into a context payload suitable for injection into an agent's prompt.

### Integration Steps

1.  **Implement the `ContextRetriever` Class:**
    -   Create the new file: `meta_context_studio/src/context_management/retrieval/context_retriever.py`.
    -   The class will be initialized with a connection to the LanceDB table, using the application settings.
    -   It will expose a primary method: `retrieve_context(query: str, top_k: int = 5) -> str`, which will return a formatted string of the retrieved context.

2.  **Integrate with the Meta-Agent:**
    -   The `Meta-Agent`'s core logic will be updated.
    -   Before delegating a task to a specialized agent, the `Meta-Agent` will use the `ContextRetriever` to fetch relevant context based on the task's description.
    -   This retrieved context will be prepended to the prompt/payload sent to the specialized agent, providing it with relevant information from the knowledge base.

3.  **Update System Architecture Documentation:**
    -   Create a new document, `system_architecture_ref/context_retrieval_subsystem.md`, to detail the design and role of the `ContextRetriever`.
    -   Update `architecture_overview.md` to illustrate the `Meta-Agent`'s new interaction with the `ContextRetriever` and the LanceDB knowledge base.

4.  **Testing and Validation:**
    -   Develop unit tests for the `ContextRetriever` to ensure it correctly queries the database and formats the output.
    -   Implement an end-to-end test where the `Meta-Agent` successfully uses the retrieved context to improve the performance of a sub-agent on a sample task, demonstrating the value of the RAG pipeline.