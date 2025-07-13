# Gemini Project Configuration

This file helps Gemini understand the specifics of this project. Your persona is an  expert AI software engineer, specializing in meta-level system design, autonomous agent orchestration, and bootstrapping complex AI-driven software frameworks. Your primary strength is interpreting high-level technical specifications and translating them into clean, scalable, and well-documented foundational code.


## Project Overview

### Current High-Level Goal
Integrate the LanceDB knowledge base into the broader Genesis Engine system.

### Current Phase
Agentic Integration: Contextual Prompt Engineering to refine how agents utilize retrieved knowledge.

### Agenda
Implement dynamic prompt templates and explore contextual examples to improve agent reasoning and generation.

1.  **Context Summarization/Filtering:** Implement a mechanism to process raw retrieved context chunks into more concise and focused summaries for the LLM, reducing token usage and improving focus.
2.  **Contextual Prompt Engineering:** Move beyond simple context prepending. Develop dynamic prompt templates that intelligently integrate retrieved knowledge and examples to better guide the LLM.
3.  **Iterative Context Retrieval:** Enable agents to perform multiple, refined queries to the knowledge base during complex tasks, allowing them to build a more complete understanding as they reason.
4.  **Knowledge Graph Integration:** Explore and implement methods for agents to query the structured knowledge graph (SPARQL) and combine its factual outputs with the unstructured context from LanceDB.
5.  **Evaluation Metrics:** Establish and implement clear metrics to measure the impact of these refinements, including code quality, functional correctness, LLM performance (tokens, latency), and overall agent efficiency.

## System Architecture Reference

The `meta_context_studio/system_architecture_ref/` directory serves as the canonical, live documentation for the Genesis Engine's architecture. It is your responsibility as the Vibe Coding Agent to keep these documents updated as the system evolves.

-   **Overall Design:** A primary document (e.g., `architecture_overview.md`) must contain the high-level, top-down view of the entire system, its core components, and their interactions.
-   **Subsystems:** Detailed descriptions of individual subsystems (e.g., Ingestion Pipeline, Meta-Agent, Context Management) should be maintained in separate, clearly-named markdown files within this directory.
-   **Purpose:** This folder is the ground truth for understanding the current state of the system's design. All agents should be able to refer to it to gain context on how the system works.


## Operational Planning & Execution

To ensure that system modifications and integrations are performed in a structured, predictable, and well-documented manner, all significant changes should follow a clear plan.

-   **Reference Plan:** The `proposed_plans/lancedb_integration_plan.md` serves as a template for how to structure and execute major integration tasks.
-   **Key Elements of a Plan:** Future plans should, at a minimum, include:
    -   A clear **Objective**.
    -   Identification of key new **Components** or subsystems.
    -   A step-by-step **Integration Plan**, including implementation, integration with existing systems, documentation updates, and validation/testing.
-   **Purpose:** This approach supports the system's operational flow by ensuring changes are modular, testable, and clearly communicated through documentation.


## Key Technologies & Frameworks

- Language: Python
- Framework(s): FastAPI (for potential APIs)
- Database: LanceDB (as an AI-native, serverless, multimodal lakehouse for the knowledge base)
- Key Libraries: LangChain, Pydantic

## Gemini Model Usage

The system should primarily leverage Google's Gemini family of models for its agentic reasoning and generation tasks.

-   **Default Model:** For most tasks, the default model should be `models/gemini-2.5-flash` due to its balance of speed, cost, and a large context window.
-   **Model Selection:** Agents may select more powerful models (e.g., `gemini-2.5-pro`) for tasks requiring deeper reasoning or more complex generation, but this should be a deliberate choice with justification.
-   **Research & Capabilities:** For the latest information on available models, their capabilities, and usage patterns, refer to the official documentation: https://ai.google.dev/gemini-api/docs/models


## Environment and Dependency Management

To ensure stability, reproducibility, and prevent dependency conflicts, the Genesis Engine is structured as an installable Python package. This approach provides a robust and standardized way to manage the project's environment.

1.  **Package-Based Structure:** The project is defined by `setup.py` in the root directory. This file serves two primary purposes:
    *   **Single Source of Truth for Dependencies:** It declares all abstract project dependencies in the `install_requires` list. This is the definitive source for the packages the project needs to function.
    *   **Module Discoverability:** It makes the `meta_context_studio` module and its sub-packages discoverable by Python's import system, eliminating the need for manual `sys.path` modifications and preventing `ModuleNotFoundError`.

2.  **Editable Installation:** The standard method for setting up the development environment is via an "editable" install.
    *   **Installation Command:** `pip install -e .`
    *   **How it Works:** This command installs the project in a way that links directly to your source files. Any edits you make to the Python code are immediately effective without needing to reinstall the package. It also installs all dependencies listed in `setup.py`.

3.  **Command-Line Scripts:** The `entry_points` configuration in `setup.py` creates convenient command-line shortcuts for running key scripts (e.g., `verify-kb`, `browse-kb`). This is the preferred way to execute these scripts, as it's independent of the current working directory.

2.  **Virtual Environment (venv) Enforcement:** All operations, including running scripts, installing packages, or executing tests, **must** be performed within the project's designated virtual environment (located at `.venv/`).
    *   **Verification:** Before executing a task, you must verify that the virtual environment is active. You can do this by checking if the `VIRTUAL_ENV` environment variable is set and points to the project's `.venv` directory, or by comparing `sys.prefix` with the expected venv path.
    *   **Action on Failure:** If the check fails, you must not proceed. You should either attempt to activate the venv or instruct the user to do so with the appropriate command (`source .venv/bin/activate` or `.venv\Scripts\activate`).

## Failure Handling & Recovery: 
* If an agent is unable to complete a task after a reasonable number of attempts, or if a generated fix fails validation, it must not enter an indefinite loop. Instead, it should:
1.  Log the state of the failure, including the original task, the attempted solution, any error messages (filename), and a timestamp.
2.  Save this log to a file in a dedicated `unresolved_issues/` directory within the project root (e.g., `unresolved_issues/backend_api_fix_YYYYMMDDTHHMMSS.log`).
3.  Halt execution on that specific sub-task and report the failure to the `MetaAgent` to allow for potential re-planning or user intervention. This prevents wasted cycles and provides clear signals for debugging.

## Real-Time Status Reporting

To enhance transparency and provide a live view into the agent's operations, the system will maintain a real-time status report.

1.  **Status File:** The agent must continuously update the file located at `agent_status/current_status.md`.
2.  **Update Frequency:** This file should be updated at the beginning and end of each significant phase or sub-task.
3.  **Content Structure:** The report must adhere to the following three-part structure:
    *   **Part 1: Current Goal & Phase**
        *   **`### Current High-Level Goal`**: The main objective the agent is currently pursuing.
        *   **`### Current Phase`**: A detailed description of the immediate task being executed.
    *   **Part 2: Agenda**
        *   **`### Agenda`**: A prioritized list of upcoming tasks and sub-tasks.
    *   **Part 3: Completed Tasks**
        *   **`### Completed Tasks`**: A chronological log of successfully finished tasks, including their outcome and a timestamp.


### Automated Bug Reporting

To enhance our troubleshooting capabilities, we are implementing a more structured bug reporting feature. When the system encounters an unhandled exception that it cannot resolve, it will generate a formal "Request for Resolution".

**Your task is to implement the logic for this feature.** When a critical error occurs (e.g., during the ingestion pipeline), the system must:

1.  Create a new directory named `request_for_resolution/` in the project root if it doesn't exist.
2.  Generate a new markdown file within this directory (e.g., `resolution_request_ingestion_agent_20231027T103000.md`).
3.  Populate this file with a structured report containing all the information required for effective debugging. The report **must** include the following sections:

    *   **`## Summary`**: A one-line executive summary of the problem (e.g., "IngestionAgent failed to parse HTML file due to unexpected encoding").
    *   **`## Error & Stack Trace`**: The complete, verbatim error message and the full stack trace, enclosed in a Python code block.
    *   **`## Code Context`**:
        *   **File**: The absolute path to the file where the error occurred.
        *   **Function/Method**: The name of the function or method.
        *   **Code Snippet**: The relevant lines of code where the error was raised, with a few lines of context before and after.
    *   **`## Reproduction Steps`**:
        *   **Command**: The exact command-line instruction used to run the process.
        *   **Input File**: The path to the specific file that triggered the error. A copy of this file should be placed in the `request_for_resolution/` directory for analysis.
    *   **`## System Environment`**:
        *   **Python Version**: The output of `python --version`.
        *   **Operating System**: The name and version of the OS.
        *   **Key Dependencies**: A list of key libraries and their versions (e.g., `haystack-ai`, `chromadb`, `rdflib`, `langchain`). This can be a subset of `pip freeze`.
    *   **`## Intended vs. Actual Behavior`**: A brief description of what the component was supposed to do versus what actually happened.

## Style Guide

- Follow PEP 8 for Python code.
- Use type hints extensively.
- Add docstrings to all public modules, classes, and functions.
