"""Handles ontology loading, validation, and inference."""


class OntologyManager:
    """
    Manages the loading and validation of ontologies.
    """

    def __init__(self, knowledge_graph_engine):
        """
        Initializes the OntologyManager.

        Args:
            knowledge_graph_engine: An instance of the KnowledgeGraphEngine.
        """
        self.knowledge_graph_engine = knowledge_graph_engine

    def load_ontology(self, ontology_path: str, ontology_format: str = "turtle"):
        """
        Loads an ontology into the knowledge graph.

        Args:
            ontology_path: The path to the ontology file.
            ontology_format: The format of the ontology file (e.g., "turtle", "xml").
        """
        self.knowledge_graph_engine.load_ontology(ontology_path, ontology_format)
        print(f"OntologyManager: Loaded ontology from '{ontology_path}'")
