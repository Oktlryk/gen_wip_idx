import gradio as gr
import pandas as pd
from pathlib import Path
from meta_context_studio.src.context_management.modeling.knowledge_graph_engine import KnowledgeGraphEngine

# --- Knowledge Base Setup ---
# This part might be slow, so it's good to do it once at startup.
knowledge_base = KnowledgeGraphEngine()
ontology_path = Path(__file__).resolve().parents[1] / "knowledge_base" / "ontologies" / "general_dev_ontology.ttl"

def initialize_kb():
    """Loads the ontology and some sample data into the knowledge base."""
    try:
        # Load the ontology
        knowledge_base.graph.parse(str(ontology_path), format="turtle")

        # Add some example data for demonstration
        # In a real scenario, this would come from the data_ingestion_pipeline
        knowledge_base.add_triple("ex:GenesisEngine", "rdf:type", "dev:SoftwareProject")
        knowledge_base.add_triple("ex:GenesisEngine", "rdfs:label", '"Genesis Engine Project"')
        knowledge_base.add_triple("ex:GenesisEngine", "dev:hasFile", "ex:run_meta_agent.py")
        knowledge_base.add_triple("ex:run_meta_agent.py", "rdf:type", "dev:CodeFile")
        return True, "Knowledge Base initialized successfully."
    except Exception as e:
        error_message = f"Error loading knowledge base: {e}"
        print(error_message)
        return False, error_message

IS_KB_LOADED, KB_LOAD_MESSAGE = initialize_kb()

def knowledge_base_query_fn(query: str):
    """Executes a SPARQL query and returns the results as a DataFrame."""
    if not IS_KB_LOADED:
        return pd.DataFrame(), KB_LOAD_MESSAGE

    try:
        results = knowledge_base.query(query)
        if not results:
            return pd.DataFrame(), "Query returned no results."
        
        # Convert results to a pandas DataFrame for display
        df = pd.DataFrame(results, columns=[str(var) for var in results.vars])
        # Convert rdflib terms to strings for better display
        for col in df.columns:
            df[col] = df[col].apply(lambda x: str(x) if x else None)

        return df, "Query successful."
    except Exception as e:
        return pd.DataFrame(), f"Query failed: {e}"

# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft(), title="Knowledge Base Explorer") as demo:
    gr.Markdown("# Knowledge Base Explorer")
    gr.Markdown("Enter a SPARQL query to explore the project's knowledge graph.")

    query_input = gr.Code(
        value="""PREFIX dev: <http://genesis-engine.com/ontology/dev#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object .
}
LIMIT 10""",
        language="sql", label="SPARQL Query", lines=10)
    query_button = gr.Button("Execute Query")
    status_output = gr.Textbox(label="Status", interactive=False, value=KB_LOAD_MESSAGE)
    results_output = gr.DataFrame(label="Query Results", wrap=True)

    query_button.click(fn=knowledge_base_query_fn, inputs=[query_input], outputs=[results_output, status_output])

def main():
    """Launches the Gradio web server."""
    demo.launch()

if __name__ == "__main__":
    main()