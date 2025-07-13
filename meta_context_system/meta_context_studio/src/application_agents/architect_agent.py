from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from meta_context_studio.src.application_agents.agent_interfaces import ApplicationRequirements, ArchitecturalPlan

class ArchitectAgent:
    """
    The Architect Agent is responsible for taking high-level application requirements
    and translating them into a basic architectural plan.
    """
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=["requirements", "context"],
            template=(
                """You are an expert software architect. Based on the following application requirements, """
                """and the provided context, generate a high-level architectural plan. Focus on key components, """
                """data models, and API endpoints. Provide a brief overview, list components, data models, """
                """API endpoints, and consider security and scalability.\n\n"""
                """Context:\n{context}\n\n"""
                """Application Requirements:\n{requirements}\n\nArchitectural Plan:"""
            )
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def generate_architectural_plan(self, requirements: ApplicationRequirements, context: str = "") -> ArchitecturalPlan:
        """
        Generates an architectural plan based on the provided application requirements and additional context.
        """
        print(f"ArchitectAgent: Generating architectural plan for {requirements.name}...")
        
        # Convert requirements to a string format suitable for the LLM
        requirements_str = f"Name: {requirements.name}\nDescription: {requirements.description}\nKey Features: {', '.join(requirements.key_features)}\nTarget Users: {requirements.target_users}\nPreferred Technologies: {', '.join(requirements.technologies_preferred)}\nAvoid Technologies: {', '.join(requirements.technologies_avoid)}"

        raw_plan = self.chain.run(requirements=requirements_str, context=context)

        # Parse the raw plan into the ArchitecturalPlan Pydantic model
        # This is a simplified parsing. In a real scenario, you'd use more robust parsing
        # or instruct the LLM to output directly in JSON.
        
        # For now, we'll create a dummy ArchitecturalPlan based on the raw output
        # and the original requirements.
        architectural_plan = ArchitecturalPlan(
            application_name=requirements.name,
            overview=raw_plan, # Using raw_plan as overview for simplicity
            components=[{"name": "Frontend"}, {"name": "Backend"}, {"name": "Database"}],
            data_models=[{"name": "User"}, {"name": "Product"}],
            api_endpoints=[{"path": "/api/v1/users"}, {"path": "/api/v1/products"}]
        )
        
        print(f"ArchitectAgent: Architectural plan generated for {requirements.name}.")
        return architectural_plan