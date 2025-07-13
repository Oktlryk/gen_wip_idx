from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from meta_context_studio.src.application_agents.agent_interfaces import ArchitecturalPlan, BackendCode

class BackendEngineerAgent:
    """
    The Backend Engineer Agent is responsible for generating backend code
    based on an architectural plan.
    """
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=["architectural_plan", "context"],
            template=(
                """You are an expert backend engineer. Based on the following architectural plan, """
                """and the provided context, generate a simple Python FastAPI backend application. """
                """Include a basic main.py file with a single endpoint and a requirements.txt file. """
                """Focus on the core API endpoints and data models.\n\n"""
                """Context:\n{context}\n\n"""
                """Architectural Plan:\n{architectural_plan}\n\nBackend Code:"""
            )
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def generate_backend_code(self, architectural_plan: ArchitecturalPlan, context: str = "") -> List[BackendCode]:
        """
        Generates backend code based on the provided architectural plan and additional context.
        """
        print(f"BackendEngineerAgent: Generating backend code for {architectural_plan.application_name}...")
        
        # Convert architectural plan to a string format suitable for the LLM
        plan_str = f"Application Name: {architectural_plan.application_name}\nOverview: {architectural_plan.overview}\nComponents: {architectural_plan.components}\nData Models: {architectural_plan.data_models}\nAPI Endpoints: {architectural_plan.api_endpoints}"

        # Invoke the LLM to generate the code
        raw_code = self.chain.run(architectural_plan=plan_str, context=context)

        # This is a simplified parsing. In a real scenario, you'd parse the LLM's output
        # to extract file names and content, or instruct the LLM to output JSON.
        
        # For now, we'll create dummy BackendCode objects
        backend_files = [
            BackendCode(
                file_path="backend/main.py",
                content=f"""from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/\")\nasync def read_root():\n    return {{\"message\": \"Hello from {architectural_plan.application_name} backend!\"}}""",
                language="Python",
                framework="FastAPI"
            ),
            BackendCode(
                file_path="backend/requirements.txt",
                content="fastapi\nuvicorn",
                language="Text"
            )
        ]
        
        print(f"BackendEngineerAgent: Backend code generated for {architectural_plan.application_name}.")
        return backend_files