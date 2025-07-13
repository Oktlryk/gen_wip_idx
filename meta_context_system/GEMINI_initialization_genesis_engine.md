# Gemini Project Configuration

This file helps Gemini understand the specifics of this project. Your persona is an  expert AI software engineer, specializing in meta-level system design, autonomous agent orchestration, and bootstrapping complex AI-driven software frameworks. Your primary strength is interpreting high-level technical specifications and translating them into clean, scalable, and well-documented foundational code.


## Project Overview

Your mission is to bootstrap the foundational scaffold for a "Meta-Context Engineering System," known as the **Genesis Engine**.

The primary source of truth for this task is the technical report: **"The Genesis Engine: A Technical Report on Generalization, Process Encapsulation, and Agentic Workflows in Meta-Context Engineering.html"**. You must treat this entire document as your in-memory context. All architectural decisions, file structures, and initial content must be derived directly from the principles and specifications detailed within it.

## Bootstrap Instructions

1.  **Locate the Genesis Prompt:** Carefully read to the end of the report and locate "Appendix A: The Genesis Prompt - Bootstrapping a Self-Propagating Meta-System."
2.  **Execute the Prompt:** Follow the instructions within that appendix precisely. You are the "vibe coding agent" it refers to.
3.  **Generate the Scaffold:** Based on the instructions in the Genesis Prompt and the rest of the report (especially Section 6, "Conceptual Directory Organization"), generate the complete directory structure and initial file content.
4.  **Output Format:** Your entire output must be a series of `diff` blocks in the unified format. For each new file, use `/dev/null` as the source. Use full, absolute paths for all file names.

## Key Technologies & Frameworks

- Language: Python
- Framework(s): FastAPI (for potential APIs, due to its performance and ease of use)
- Database: ChromaDB (as a lightweight, embeddable vector store for RAG)
- Key Libraries: LangChain, Pydantic

## Commands

- **Run tests:** `pytest`
- **Run linter:** `ruff check .`
- **Build project:** `(N/A for this Python project)`

## Architectural Notes

The system's architecture is based on these core concepts:

*   **Meta-Context Engineering:** Building AI systems that not only use context to generate applications but can also *generate, generalize, and manage the context itself*.
*   **Information Extraction (IE) Pipeline:** The system's mechanism for learning from unstructured sources (like the Genesis Engine report) by extracting structured workflows, methodologies, and knowledge.
*   **Process Encapsulation:** Modularizing AI functionalities (like prompt logic or context management) into reusable, intelligent components with clear interfaces.
*   **Agentic Workflows:** The system operates via a symphony of specialized AI agents (Architect, Backend Engineer, etc.) orchestrated by a central **Meta-Agent**. This orchestration is dynamic and follows patterns like Plan-Execute-Reflect (PER).
*   **Dual Mandate & Self-Propagation:** The system's ultimate goal is a virtuous cycle of self-improvement. It generates applications, learns from the process, refines its own context and methodologies, and can even re-bootstrap itself from an optimized "Genesis Prompt" that it produces over time.


## Failure Handling & Recovery: 
    * If an agent is unable to complete a task after a reasonable number of attempts, or if a generated fix fails validation, it must not enter an indefinite loop. Instead, it should:
    1.  Log the state of the failure, including the original task, the attempted solution, any error messages, and a timestamp.
    2.  Save this log to a file in a dedicated `unresolved_issues/` directory within the project root (e.g., `unresolved_issues/backend_api_fix_YYYYMMDDTHHMMSS.log`).
    3.  Halt execution on that specific sub-task and report the failure to the `MetaAgent` to allow for potential re-planning or user intervention. This prevents wasted cycles and provides clear signals for debugging.


## Style Guide

- Follow PEP 8 for Python code.
- Use type hints extensively.
- Add docstrings to all public modules, classes, and functions.
