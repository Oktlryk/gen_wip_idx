# System Structure and Operations: Technical Report

This document provides a condensed, high-level overview of the Genesis Engine's architecture and core operational workflows, suitable for deep analysis.

## 1. Core Concepts

-   **Meta-Context Engineering:** The discipline of building AI systems that not only use context but can also *generate, generalize, and manage the context itself*.
-   **Agentic Workflows:** System operations are conducted by a symphony of specialized AI agents orchestrated by a central Meta-Agent, following dynamic patterns like Plan-Execute-Reflect (PER).
-   **Process Encapsulation:** Modularizing AI functionalities (e.g., prompt logic, context management) into reusable, intelligent components with clear interfaces.
-   **Dual Mandate & Self-Propagation:** The system's core objective is a virtuous cycle of self-improvement: it generates applications, learns from the process, refines its own context, and can re-bootstrap itself from an optimized state.

## 2. Key Technologies & Frameworks

-   **Primary Language:** Python
-   **API Framework:** FastAPI (for potential future exposure of agentic services)
-   **Vector Store:** ChromaDB (for lightweight, embeddable RAG storage)
-   **Core AI Libraries:** LangChain (for composing agentic chains and tool usage), Pydantic (for data validation and settings management).

## 3. System Architecture (Genesis Engine)

### 3.1. Architectural Patterns & Design Decisions

-   **Modularity and Layering:** The system is organized into distinct layers (Context Management, Agent Orchestration, Application Agents) to ensure a clear separation of concerns, facilitating independent development and maintenance.
-   **Event-Control-Action (ECA) Pattern:** Context management (sensing) is decoupled from the system's reactive behaviors (action). This allows context processing and agent actions to evolve independently, enhancing flexibility.
-   **Composability over Configuration:** The design favors creating small, purpose-built, reusable components (e.g., individual context heuristics, specific agent tools) that can be flexibly assembled into complex workflows, rather than relying on monolithic, overly configurable structures.
-   **Policy as Code (PaC):** Architectural constraints, coding standards, and security protocols are defined in machine-readable YAML files (`policy_as_code.yaml`). This allows policies to be version-controlled, automatically enforced, and audited throughout the generation lifecycle.

### 3.2. Core Components

-   **Meta-Context Management System (Meta-CMS):** The cognitive core. Responsible for the generation, generalization, and management of context at a meta-level.
-   **Agent Orchestration:** A hierarchical, dynamic system for coordinating tasks.
    -   **Meta-Agent:** The central conductor. Decomposes high-level goals and delegates to specialized agents.
    -   **Specialized Agents:** Experts in specific domains (e.g., `ArchitectAgent`, `BackendEngineerAgent`, `TestGenerationAgent`).
-   **Knowledge Base:** The central repository of all system knowledge.
    -   **Ontologies:** Formal, structured schemata for knowledge (`general_dev_ontology.ttl`).
    -   **Policies:** Codiﬁed rules and best practices (`policy_as_code.yaml`).
    -   **RAG Stores:** Vectorized embeddings of documents and knowledge graph data for efficient retrieval.

### 3.3. Implemented Agents and Capabilities

-   **`ArchitectAgent`:** Designs the high-level architecture of the application.
-   **`BackendEngineerAgent`:** Generates the backend API endpoints.
-   **`FrontendEngineerAgent`:** Creates the user interface components.
-   **`DevOpsAgent`:** Generates deployment configurations.
-   **`TestGenerationAgent`:** Produces unit tests for the application code.

## 4. Key Operational Workflows & Techniques

### 4.1. Information Extraction (IE) Pipeline

-   **Purpose:** To learn from unstructured data and convert it into formalized knowledge.
-   **Techniques:**
    -   **Parsing:** Utilizes parsers for various formats (PDF, HTML, Markdown).
    -   **NLP/ML:** Employs Named Entity Recognition (NER), Relation Extraction (RE), and Event Extraction to identify key concepts and their relationships.
    -   **Formalization:** Stores the structured output in the central Knowledge Graph, guided by the system's ontologies.

### 4.2. Advanced Reasoning Patterns

The system's LLM-based agents employ a hierarchy of reasoning techniques to tackle complex problems:

-   **Chain-of-Thought (CoT):** For linear, step-by-step reasoning, making the AI's thought process transparent.
-   **Tree-of-Thoughts (ToT):** For exploring multiple potential solutions in a structured, branching manner, allowing for self-evaluation and backtracking.
-   **Graph-of-Thoughts (GoT):** For maximum flexibility, decomposing problems into a graph of operations, enabling the system to model and solve highly interconnected and complex tasks.

### 4.3. Application Generation Workflow

-   **Purpose:** To autonomously generate a complete software application from a high-level goal.
-   **Flow:**
    1.  **Goal Decomposition:** `MetaAgent` breaks the user's request into sub-tasks.
    2.  **Agent Delegation:** `MetaAgent` assigns tasks to specialized agents.
    3.  **Context Provisioning & Heuristics:** The `Meta-CMS` provides each agent with precisely tailored context, optimized by:
        -   **Relevance Filtering:** Prioritizing the most relevant information.
        -   **Summarization:** Compressing long documents to reduce token usage.
        -   **Context Quarantining:** Isolating potentially distracting or conflicting information.
    4.  **Iterative Generation (PER Loop):** Each agent **Plans** its approach, **Executes** (e.g., writes code), and **Reflects** on the outcome (e.g., runs tests), iterating until its sub-goal is met.
    5.  **Integration:** `MetaAgent` assembles the final application from the outputs of all agents.

### 4.4. Context Generation Workflow (Self-Refinement Loop)

-   **Purpose:** To enable the system to improve its own knowledge and performance over time.
-   **Flow:**
    1.  **Need Identification:** `MetaAgent` detects a knowledge gap from a new requirement or poor evaluation score.
    2.  **Context Extraction:** `ContextExtractionAgent` processes a new document using the IE Pipeline.
    3.  **Knowledge Graph Update:** The new knowledge is integrated into the central KG.
    4.  **Schema/Policy Refinement:** Prompts (`.yaml` files) and policies (`policy_as_code.yaml`) are automatically updated to reflect the new, generalized knowledge.

## 5. Directory Structure Mapping

-   **Context Management (`src/context_management/`):** Houses the IE Pipeline, KG engine, and context heuristics.
-   **Agent Orchestration (`src/agent_orchestration/`):** Contains the `MetaAgent` and workflow management logic.
-   **Specialized Agents (`src/application_agents/`):** Contains the individual worker agents.
-   **Knowledge (`knowledge_base/`):** The central store for all ontologies, policies, and raw/processed data.
-   **Evaluation (`evaluation/`):** Contains the framework and datasets for assessing system performance.