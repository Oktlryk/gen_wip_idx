# Architecture Overview: The Genesis Engine

**From:** Vibe Coding Agent
**To:** Requesting Agent

**Subject:** Analysis of Existing Context and Knowledge Management Mechanisms

This report details the current architecture of the Genesis Engine with a specific focus on how agents access, utilize, and manage context and knowledge. This information reflects the *completed* integration of the LanceDB-based knowledge base.

### 1. How Agents Access and Utilize Knowledge

Agent access to knowledge is orchestrated by the **Meta-Agent** and provisioned by the **Meta-Context Management System (Meta-CMS)**. The process is as follows:

1.  **Task Delegation:** The Meta-Agent decomposes a high-level goal and assigns a specific sub-task to a specialized agent (e.g., `BackendEngineerAgent`).
2.  **Context Retrieval (RAG):** The Meta-Agent now actively queries the **`ContextRetriever`** subsystem with a natural language description of the task. The `ContextRetriever` performs a semantic search on the LanceDB vector store and returns the most relevant document chunks.
3.  **Context Provisioning:** The Meta-CMS assembles a tailored context payload for the agent. This payload now includes:
    *   The task instructions.
    *   The retrieved context from the knowledge base.
    *   Other dynamic context (e.g., project state, previous outputs).
4.  **Agent Execution:** The agent receives the curated context and utilizes it within a **Plan-Execute-Reflect (PER)** loop to perform its task (e.g., write code, generate tests). The context informs every stage of this loop.

### 2. Mechanisms for Context Management and Retrieval

Context management is centralized within the **Knowledge Base**, which has two primary components:

1.  **Structured Knowledge (Knowledge Graph):**
    *   **Mechanism:** An RDF-based knowledge graph built using `rdflib`.
    *   **Content:** It stores formalized knowledge derived from ontologies (`.ttl` files) and the Information Extraction (IE) pipeline. This includes relationships between code entities, architectural patterns, and system policies.
    *   **Retrieval:** Agents can query this graph using SPARQL.

2.  **Unstructured & Semi-Structured Knowledge (Vector Store):**
    *   **Mechanism:** A vector store for Retrieval-Augmented Generation (RAG) powered by **LanceDB**.
    *   **Content:** This store contains vectorized embeddings of source documents (technical reports, code files, articles) that have been processed by the ingestion pipeline.
    *   **Retrieval:** When an agent needs information from the document corpus, a semantic search is performed against the LanceDB vector store. The top-k most relevant document chunks are retrieved and added to the agent's context payload.

The **Information Extraction (IE) Pipeline** is the primary mechanism for populating both components of the Knowledge Base from new, unstructured sources.

### 3. Existing Interfaces and APIs for Knowledge Interaction

Interaction with the knowledge base is handled through both programmatic APIs and user-facing tools:

1.  **Programmatic APIs (Internal):**    
    *   **Context Retrieval API:** The `ContextRetriever` class (in `meta_context_studio/src/context_management/retrieval/context_retriever.py`) provides a high-level `retrieve_context()` method. This is the **primary and intended interface** for all agents to interact with the unstructured knowledge base.
    *   **LanceDB Ingestion:** The `LanceDBIngestionPipeline` class (in `meta_context_studio/src/lancedb_ingestion/ingestion_pipeline.py`) provides `ingest_from_directory()` for populating the knowledge base.
    *   **Knowledge Graph Engine:** The `KnowledgeGraphEngine` class (in `meta_context_studio/src/context_management/modeling/knowledge_graph_engine.py`) provides `add_triple()` and `query()` methods for direct, programmatic interaction with the RDF graph.

2.  **User/Developer Interfaces:**
    *   **Knowledge Base Browser:** The `browse_knowledge_base.py` script launches a Gradio web UI that allows a developer to execute SPARQL queries directly against the Knowledge Graph and view the results.
    *   **Verification Script:** The `verify_kb.py` script provides a command-line interface to check the status and contents of the LanceDB table, serving as a quick diagnostic tool.

This architecture provides a layered and modular approach to knowledge management, with LanceDB now fully integrated and operational for enhanced context retrieval.