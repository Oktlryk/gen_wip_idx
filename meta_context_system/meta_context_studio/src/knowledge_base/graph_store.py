from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS
from meta_context_studio.src.ingestion.data_models import DocumentType
from typing import List, Dict, Any
import os

from meta_context_studio.src.ingestion.data_models import ParsedDocument, ContentBlock

# Define Namespaces for our ontology (simplified for now)
GENESIS = Namespace("http://genesis.engine.org/ontology/")

class GraphStore:
    """
    Handles interactions with the RDF graph for storing and querying structured knowledge.
    """
    def __init__(self, graph_path: str = "meta_context_studio/knowledge_base/ontologies/knowledge_graph.ttl"):
        self.graph = Graph()
        self.graph_path = graph_path
        self._bind_namespaces()
        self.load_graph()

    def _bind_namespaces(self):
        """Binds common namespaces to the graph."""
        self.graph.bind("genesis", GENESIS)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)

    def load_graph(self):
        """Loads the RDF graph from a file if it exists."""
        if os.path.exists(self.graph_path):
            try:
                self.graph.parse(self.graph_path, format="turtle")
                print(f"Loaded knowledge graph from {self.graph_path}")
            except Exception as e:
                print(f"Error loading graph from {self.graph_path}: {e}")
        else:
            print(f"No existing knowledge graph found at {self.graph_path}. A new one will be created.")

    def save_graph(self):
        """Saves the RDF graph to a file."""
        try:
            self.graph.serialize(destination=self.graph_path, format="turtle")
            print(f"Saved knowledge graph to {self.graph_path}")
        except Exception as e:
            print(f"Error saving graph to {self.graph_path}: {e}")

    def add_document_to_graph(self, document: ParsedDocument):
        """
        Adds a ParsedDocument and its extracted entities/relationships to the graph.
        This is a simplified example; real entity/relationship extraction would be done
        by the KnowledgeGraphUpdateAgent.
        """
        doc_uri = URIRef(GENESIS[document.document_id])
        self.graph.add((doc_uri, RDF.type, GENESIS.Document))
        self.graph.add((doc_uri, RDFS.label, Literal(document.metadata.get("title", document.document_id))))
        self.graph.add((doc_uri, GENESIS.hasSourcePath, Literal(document.source_path)))
        self.graph.add((doc_uri, GENESIS.hasDocumentType, Literal(document.document_type.value)))

        # Add content blocks as part of the document
        for i, block in enumerate(document.content_blocks):
            block_uri = URIRef(GENESIS[f"{document.document_id}_block_{i}"])
            self.graph.add((block_uri, RDF.type, GENESIS.ContentBlock))
            self.graph.add((block_uri, GENESIS.partOf, doc_uri))
            self.graph.add((block_uri, GENESIS.hasContent, Literal(block.content)))
            self.graph.add((block_uri, GENESIS.hasBlockType, Literal(block.block_type.value)))
            for key, value in block.metadata.items():
                self.graph.add((block_uri, GENESIS[key], Literal(value)))

    def query_graph(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes a SPARQL query against the graph and returns the results.
        """
        results = []
        try:
            for row in self.graph.query(query):
                results.append(row.asdict())
        except Exception as e:
            print(f"Error executing SPARQL query: {e}")
        return results

    def get_document_by_id(self, document_id: str) -> ParsedDocument | None:
        """
        Retrieves a ParsedDocument from the graph based on its ID.
        This is a simplified reconstruction and might not capture all nuances.
        """
        doc_uri = URIRef(GENESIS[document_id])
        if (doc_uri, RDF.type, GENESIS.Document) in self.graph:
            title = str(self.graph.value(doc_uri, RDFS.label))
            source_path = str(self.graph.value(doc_uri, GENESIS.hasSourcePath))
            doc_type = str(self.graph.value(doc_uri, GENESIS.hasDocumentType))

            content_blocks: List[ContentBlock] = []
            for s, p, o in self.graph.triples((None, GENESIS.partOf, doc_uri)):
                if (s, RDF.type, GENESIS.ContentBlock) in self.graph:
                    content = str(self.graph.value(s, GENESIS.hasContent))
                    block_type = str(self.graph.value(s, GENESIS.hasBlockType))
                    block_metadata = {}
                    for bp, bo in self.graph.predicate_objects(s):
                        if str(bp).startswith(str(GENESIS)) and bp not in [GENESIS.partOf, GENESIS.hasContent, GENESIS.hasBlockType]:
                            block_metadata[str(bp).replace(str(GENESIS), "")] = str(bo)
                    content_blocks.append(ContentBlock(
                        block_type=block_type,
                        content=content,
                        metadata=block_metadata
                    ))
            
            return ParsedDocument(
                document_id=document_id,
                document_type=DocumentType(doc_type),
                source_path=source_path,
                metadata={"title": title},
                content_blocks=content_blocks
            )
        return None
