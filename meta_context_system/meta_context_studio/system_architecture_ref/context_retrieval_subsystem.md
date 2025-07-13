# Context Retrieval Subsystem

**Component:** `ContextRetriever`
**Location:** `meta_context_studio/src/context_management/retrieval/context_retriever.py`

## 1. Purpose and Role

The `ContextRetriever` is a specialized subsystem designed to act as the sole interface between the agentic layer and the unstructured knowledge base stored in LanceDB. Its primary responsibility is to encapsulate the logic of semantic search and retrieval, providing a clean, high-level API for agents to request and receive context.

This encapsulation serves several key architectural principles:
-   **Separation of Concerns:** Agents do not need to know the underlying implementation details of the vector store (LanceDB), embedding models, or search algorithms. They simply request context for a given topic.
-   **Standardization:** It provides a single, consistent method for context retrieval across the entire Genesis Engine, ensuring that all agents receive context in a uniform format.
-   **Maintainability:** Changes to the retrieval mechanism (e.g., upgrading LanceDB, changing embedding models, or modifying search logic) can be made in one place without affecting any of the agents that depend on it.

## 2. Core Functionality

The subsystem is implemented as the `ContextRetriever` class.

-   **Initialization:** Upon instantiation, it establishes a connection to the LanceDB table defined in the system's configuration.
-   **Primary Method (`retrieve_context`):**
    -   **Input:** A natural language `query` string and an optional `top_k` integer to specify the number of desired results.
    -   **Process:**
        1.  It uses the configured embedding model to generate a vector embedding for the input query.
        2.  It performs a semantic similarity search against the LanceDB vector store.
        3.  It retrieves the `top_k` most relevant document chunks.
    -   **Output:** It formats the retrieved text chunks and their associated metadata (e.g., source document) into a single, formatted string. This string is designed to be directly injected into an agent's prompt to provide it with relevant, just-in-time information.

## 3. Interaction with Other Systems

-   **Meta-Agent:** The `Meta-Agent` is the primary consumer of this subsystem. Before dispatching a task to a specialized agent, it will use the `ContextRetriever` to fetch relevant background information based on the task description.
-   **Specialized Agents:** Any agent can, in theory, use the `ContextRetriever` if its workflow requires it to perform its own research during a task.
-   **LanceDB Ingestion Pipeline:** The `ContextRetriever` relies on the data populated by the `LanceDBIngestionPipeline`. It is a read-only consumer of the knowledge base.