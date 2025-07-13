# Operations Manual: The Genesis Engine

## 1. Introduction

This manual provides detailed instructions for the setup, operation, and management of the Meta-Context Engineering System, also known as the Genesis Engine. This system is designed to autonomously generate software applications by intelligently managing and generating its own context.

## 2. System Setup

### 2.1. Prerequisites

- Python 3.9+
- `pip` for package management

### 2.2. Installation

1.  **Clone the repository** (if applicable) and navigate to the `meta_context_system` directory.
2.  **Install the project in editable mode.** This command uses the `setup.py` file to install all necessary dependencies and make the project's packages available throughout your virtual environment.

    ```bash
    pip install -e .
    ```
    This is the only installation step required. It replaces the need to manually install from `requirements.txt`.

### 2.3. Configuration

All system-wide configurations are managed in the `meta_context_studio/config/` directory.

1.  **API Keys and Paths (`settings.py`):**

    - Open `meta_context_studio/config/settings.py`.
    - Set your Gemini and/or Groq API keys by replacing the placeholder values or setting the corresponding environment variables (e.g., `GEMINI_API_KEY`, `GROQ_API_KEY`).
    - The `KNOWLEDGE_BASE_PATH` is set automatically, but you can modify it if you move the directory.

2.  **Agent Configuration (`agent_configs.yaml`):

    - Open `meta_context_studio/config/agent_configs.yaml`.
    - Here you can define the roles, capabilities, and default LLM models for each specialized agent in the system.

## 3. Running the System

The primary entry point for all system operations is the Meta-Agent.
To initiate a task, use the `run-meta-agent` command-line script. This is an entry point created by the `setup.py` file and is the correct way to launch the system.

    ```bash
    run-meta-agent
    ```

    The task is currently hardcoded in the script to "build a simple flask api for a task manager".

## 4. Core Workflows

### 4.1. Application Generation

This is the primary workflow for creating new software.

1.  **Goal Initiation:** The process starts when you run the `run_meta_agent.py` script with a high-level task.
2.  **Goal Decomposition:** The `MetaAgent` analyzes the task and breaks it down into smaller, manageable sub-goals (e.g., design architecture, create backend, develop UI).
3.  **Agent Delegation:** The `MetaAgent` delegates these sub-goals to the appropriate specialized agents (`ArchitectAgent`, `BackendEngineerAgent`, etc.).
4.  **Execution:** Each agent executes its task within a Plan-Execute-Reflect (PER) loop, using the context provided by the Meta-CMS to generate code, tests, or documentation.
5.  **Integration:** The `MetaAgent` integrates the outputs from all agents into a coherent application, stored in the `meta_context_studio/generated_apps/` directory.

### 4.2. Context Generation (Self-Refinement)

The system continuously improves its own knowledge and capabilities.

1.  **Need Identification:** The `MetaAgent` identifies a knowledge gap. This can be triggered by a new project requirement, an external document, or poor performance metrics from the evaluation framework.
2.  **Extraction:** The `ContextExtractionAgent` is dispatched to process new unstructured data (e.g., a research paper in `knowledge_base/reference_docs/`).
3.  **Update:** The `KnowledgeGraphUpdateAgent` integrates the newly extracted, structured information into the central Knowledge Graph and RAG stores.
4.  **Refinement:** The `PromptGenerationAgent` and `PolicyEnforcementAgent` update existing prompt templates and policies to reflect the new knowledge.

## 5. Knowledge Base Management

The system's intelligence is stored in the `meta_context_studio/knowledge_base/` directory.

-   **To chat with the unstructured knowledge base (RAG):** Launch the Gradio web UI to ask questions and get answers from the documents stored in LanceDB.

    ```bash
    chat-with-kb
    ```

-   **To browse the structured knowledge graph (SPARQL):** Launch the Gradio UI to execute SPARQL queries against the RDF graph.

    ```bash
    browse-kb
    ```

-   **To add new knowledge:** Place new technical reports, articles, or other documents into `knowledge_base/reference_docs/`. The system can then be prompted to process them.
-   **To add a new ontology:** Create a new `.ttl` file in `knowledge_base/ontologies/domain_specific_ontologies/`.
-   **To add a new policy:** Add a new entry to `knowledge_base/policies/policy_as_code.yaml`.

## 6. Evaluation

The `meta_context_studio/evaluation/` directory contains scripts to assess the system's performance.

-   **RAG Evaluation:** Run `rag_evaluator.py` to assess the quality of the context retrieval system.
-   **CodeGen Evaluation:** Run `codegen_evaluator.py` to assess the quality of the generated code using metrics like `pass@k`.

These evaluation scripts provide the necessary feedback for the system's self-refinement loop.

## 7. Troubleshooting & Debugging

### 7.1. Empty Response from Knowledge Base Chat (`chat_kb`)

An empty or non-responsive answer from the knowledge base chat UI is typically a symptom of a breakdown in the RAG (Retrieval-Augmented Generation) pipeline. Follow these steps to diagnose the issue:

1.  **Verify Data Ingestion:**
    -   The most common cause is an empty or improperly indexed knowledge base.
    -   **Action:** Ensure the ingestion pipeline has been run successfully after adding new documents to `knowledge_base/reference_docs/`.
    -   **Verification:** Use the provided verification script to connect to the LanceDB table and check its contents.
        ```bash
        verify-kb
        ```
    -   If the script reports 0 rows or fails, the problem is with the data ingestion process. Review the ingestion logic and logs.

2.  **Isolate the Retriever:**
    -   If the KB has data, the retriever might not be finding relevant documents for your query.
    -   **Action:** Add logging to the retrieval function within your chat logic to print the retrieved documents and their similarity scores.
    -   **Check:** Are documents being returned? Are their scores very low? If so, you may need to adjust the embedding model, the number of documents to retrieve (`k`), or the query itself.

3.  **Inspect the Final LLM Prompt:**
    -   If documents *are* being retrieved, the final prompt sent to the LLM might be malformed, or the LLM might be choosing not to answer.
    -   **Action:** Log the exact prompt being sent to the Gemini model. It should contain the retrieved context.
    -   **Check:** If the context is present but the answer is empty, the LLM might be filtering the answer due to its safety settings or a lack of confidence. Try a different query or a more capable model (e.g., `gemini-pro`) as defined in `gemini.md`.

4.  **Review the UI Layer:**
    -   Finally, ensure the Gradio UI (`browse_knowledge_base.py`) is correctly handling the backend's response. An error in the UI code could prevent the display of a valid response.
    -   **Action:** Check the terminal where you launched the Gradio app for any frontend or backend errors that occur when you submit a query.
