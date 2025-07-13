from typing import List, Dict, Any
from meta_context_studio.src.lancedb_ingestion.ingestion_pipeline import LanceDBIngestionPipeline
from meta_context_studio.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class ContextRetriever:
    """
    A dedicated class to handle all interactions with the unstructured knowledge base (LanceDB).
    This serves as the primary, standardized interface for any agent needing to perform semantic searches.
    """

    def __init__(self):
        """
        Initializes the ContextRetriever, setting up a connection to the LanceDB knowledge base.
        """
        # The pipeline handles the connection to the DB path and table from settings
        self.ingestion_pipeline = LanceDBIngestionPipeline(
            db_path=settings.KNOWLEDGE_BASE_PATH,
            table_name=settings.LANCE_TABLE_NAME
        )
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.2)
        self.summarization_prompt = PromptTemplate(
            input_variables=["context"],
            template="""Summarize the following text concisely, focusing on key information relevant to software engineering:

{context}

Summary:"""
        )
        self.summarization_chain = LLMChain(llm=self.llm, prompt=self.summarization_prompt)

    def retrieve_context(self, query: str, top_k: int = 5, summarize_context: bool = False) -> str:
        """
        Takes a natural language query, retrieves the most relevant document chunks,
        and formats them into a context payload suitable for injection into an agent's prompt.

        Args:
            query (str): The natural language query to search for.
            top_k (int): The number of top results to retrieve.
            summarize_context (bool): Whether to summarize each retrieved context chunk.

        Returns:
            str: A formatted string containing the retrieved context.
        """
        search_results = self.ingestion_pipeline.search(query, limit=top_k)

        if not search_results:
            return "No relevant context found in the knowledge base."

        # Format the results into a clean string for the agent's context
        formatted_context = "--- Relevant Context from Knowledge Base ---\n\n"
        for i, result in enumerate(search_results):
            text = result.get('text', 'No text available.')
            source = result.get('metadata', {}).get('source', 'Unknown source')

            if summarize_context:
                print(f"Summarizing context from {source}...")
                try:
                    text = self.summarization_chain.run(context=text)
                except Exception as e:
                    print(f"Error summarizing context from {source}: {e}. Using original text.")

            formatted_context += f"Context [{i+1}] (Source: {source}):\n"
            formatted_context += f'"""\n{text}\n"""\n\n'
        
        formatted_context += "--- End of Context ---"
        
        return formatted_context
