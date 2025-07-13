# Technical Report: A Unified Context Retrieval Strategy
## Fusing Vector Search with Knowledge Graph Traversal

**Status:** Proposed
**Author:** Gemini Code Assist
**Date:** 2024-06-02

---

### 1. Objective

To design and implement a unified context retrieval system that allows agents to seamlessly query and combine context from both the **LanceDB vector store** (unstructured, semantic knowledge) and the **RDF knowledge graph** (structured, factual knowledge). The goal is to provide a richer, more accurate context to the LLM agents while simplifying the retrieval logic within the agents themselves.

### 2. Problem Statement

Currently, the Genesis Engine maintains two distinct and powerful knowledge sources, as detailed in the `architecture_overview.md`:

1.  **LanceDB Vector Store:** Excellent for semantic search over large corpora of documents (code, reports, etc.). It answers "what is this about?" questions.
2.  **RDF Knowledge Graph:** Excellent for querying explicit, factual relationships between known entities. It answers "what is the relationship between X and Y?" questions.

Fusing these sources presents several challenges:

*   **Query Ambiguity:** An agent's natural language query (e.g., "How does the ArchitectAgent relate to the BackendEngineerAgent?") could be interpreted as either a semantic search or a factual graph traversal. The system needs a mechanism to determine the best retrieval strategy.
*   **Context Heterogeneity:** The outputs are fundamentally different. LanceDB returns chunks of text, while the graph returns structured triples (subject, predicate, object). Simply concatenating them can be confusing for an LLM and lead to "context poisoning."
*   **Agent Cognitive Overhead:** Requiring each specialized agent to decide which knowledge base to query, how to format the query (natural language vs. SPARQL), and how to merge the results would add significant complexity to their core logic, violating our principle of composability.

### 3. Proposed Architecture

We will introduce a new orchestration layer, the `UnifiedContextRetriever`. This component will act as a single, intelligent entry point for all agent-based knowledge queries. It will abstract away the complexity of choosing and querying the underlying data stores.

The `MetaAgent` will no longer call the `ContextRetriever` directly but will instead delegate all context requests to the `UnifiedContextRetriever`.

**Architectural Flow:**

```mermaid
graph TD
    A[MetaAgent] -->|1. "Tell me about X and its relation to Y"| B(UnifiedContextRetriever);
    B -->|2a. Analyze Query| B;
    B -->|3a. Semantic Query| C[ContextRetriever (LanceDB)];
    B -->|3b. Factual Query| D[KnowledgeGraphEngine (RDF)];
    C -->|4a. Text Chunks| B;
    D -->|4b. RDF Triples| B;
    B -->|5. Fuse Results| B;
    B -->|6. Fused Context Payload| A;
```

### 4. Query Orchestration & Fusion Logic

The `UnifiedContextRetriever` will employ a multi-step process to handle incoming queries.

#### 4.1. Query Analysis & Dispatch

The retriever will first analyze the agent's query to determine the optimal retrieval strategy.

*   **Heuristic-Based Dispatch:** A simple and fast approach. The query is scanned for keywords.
    *   **Keywords:** "relationship", "connects to", "subclass of", "property of", "what is the type of" -> **Dispatch to Knowledge Graph (SPARQL)**.
    *   **Keywords:** "describe", "explain", "how does", "what is the purpose of" -> **Dispatch to Vector Store (LanceDB)**.
    *   **Hybrid:** If both types of keywords are present, or if entities are clearly named, dispatch to both.

*   **LLM-Based Dispatch (Advanced):** For more nuanced queries, a quick call to a fast LLM (like `gemini-2.5-flash`) can classify the query's intent into `SEMANTIC`, `FACTUAL`, or `HYBRID`.

#### 4.2. Iterative Refinement Pattern

For complex, hybrid queries, the retriever can use an iterative approach to enrich context:

1.  **Initial Broad Search:** An agent asks, "Explain the ingestion pipeline and its connection to the KnowledgeGraphUpdateAgent."
2.  **Vector Retrieval:** The `UnifiedContextRetriever` first performs a semantic search in LanceDB for "ingestion pipeline".
3.  **Entity Extraction:** From the retrieved text chunks, it identifies key entities like `IngestionPipeline` and `KnowledgeGraphUpdateAgent`.
4.  **Factual Deep-Dive:** It then automatically formulates precise SPARQL queries to the knowledge graph using these extracted entities.
    ```sparql
    PREFIX genesis: <http://www.genesis-engine.com/ontology/>
    SELECT ?p ?o WHERE { genesis:IngestionPipeline ?p ?o . }
    ```
5.  **Combined Result:** The final context payload includes both the descriptive text from the vector search and the specific factual relationships from the graph query.

#### 4.3. Result Fusion

To avoid context poisoning, the results from the two sources will not be simply concatenated. They will be fused into a structured dictionary, making it clear to the downstream LLM what kind of information it is receiving.

**Example Fused Payload:**
```json
{
  "unstructured_summary": "The ingestion pipeline is responsible for processing various document types... It uses a DocumentInterpreter to extract key information and prepares it for storage...",
  "structured_facts": [
    {"subject": "IngestionPipeline", "predicate": "hasComponent", "object": "DocumentInterpreter"},
    {"subject": "IngestionPipeline", "predicate": "sendsDataTo", "object": "LanceDBIngestionPipeline"},
    {"subject": "KnowledgeGraphUpdateAgent", "predicate": "consumes", "object": "ParsedDocument"}
  ]
}
```
This structure allows the prompt template to explicitly label each type of context, for example: "Here is a general description of the topic: [unstructured_summary]. Here are some specific facts and relationships: [structured_facts]."

### 5. Proposed API/Interface Design

The `MetaAgent` will be updated with a new method to access this unified retriever. This provides a clean, high-level interface for all specialized agents.

```python
from typing import Union, List, Dict

class MetaAgent:
    # ... existing attributes like self.lancedb_retriever, self.graph_engine ...

    def __init__(self):
        # ...
        # self.unified_retriever = UnifiedContextRetriever(
        #     vector_retriever=self.context_retriever,
        #     graph_engine=self.graph_store
        # )
        pass

    def get_unified_context(self, query: str, sources: List[str] = ['vector', 'graph']) -> Dict[str, Union[str, List[dict]]]:
        """
        Retrieves and fuses context from multiple knowledge sources.

        This method delegates the complex task of querying and merging data to the
        UnifiedContextRetriever, providing a simple interface for agents.
        """
        # In a real implementation, this logic would reside in the UnifiedContextRetriever class.
        # 1. Analyze query to determine strategy (heuristic or LLM-based).
        # 2. Dispatch query/queries to self.context_retriever (LanceDB) and/or self.graph_store.
        # 3. Retrieve unstructured text and/or structured triples.
        # 4. Fuse the results into the standard dictionary format.
        # 5. Return the fused context payload.

        # Example call:
        # fused_context = self.unified_retriever.retrieve(query)
        # return fused_context
        pass
```

