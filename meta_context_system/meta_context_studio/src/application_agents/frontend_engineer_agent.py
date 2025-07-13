from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from meta_context_studio.src.application_agents.agent_interfaces import ArchitecturalPlan, FrontendCode

class FrontendEngineerAgent:
    """
    The Frontend Engineer Agent is responsible for generating frontend code
    based on an architectural plan.
    """
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=["architectural_plan", "context"],
            template=(
                """You are an expert frontend engineer. Based on the following architectural plan, """
                """and the provided context, generate a simple HTML/CSS/JavaScript frontend application. """
                """Include a basic index.html, style.css, and script.js file. Focus on a simple UI that """
                """interacts with the backend.\n\n"""
                """Context:\n{context}\n\n"""
                """Architectural Plan:\n{architectural_plan}\n\nFrontend Code:"""
            )
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def generate_frontend_code(self, architectural_plan: ArchitecturalPlan, context: str = "") -> List[FrontendCode]:
        """
        Generates frontend code based on the provided architectural plan and additional context.
        """
        print(f"FrontendEngineerAgent: Generating frontend code for {architectural_plan.application_name}...")
        
        # Convert architectural plan to a string format suitable for the LLM
        plan_str = f"Application Name: {architectural_plan.application_name}\nOverview: {architectural_plan.overview}\nComponents: {architectural_plan.components}\nData Models: {architectural_plan.data_models}\nAPI Endpoints: {architectural_plan.api_endpoints}"

        # Invoke the LLM to generate the code
        raw_code = self.chain.run(architectural_plan=plan_str, context=context)

        # This is a simplified parsing. In a real scenario, you'd parse the LLM's output
        # to extract file names and content, or instruct the LLM to output JSON.
        
        # For now, we'll create dummy FrontendCode objects
        frontend_files = [
            FrontendCode(
                file_path="frontend/index.html",
                content=f"<!DOCTYPE html>\n<html>\n<head>\n    <title>{architectural_plan.application_name}</title>\n    <link rel=\"stylesheet\" href=\"style.css\">\n</head>\n<body>\n    <h1>Welcome to {architectural_plan.application_name}</h1>\n    <button id=\"fetchData\">Fetch Data from Backend</button>\n    <div id=\"output\"></div>\n    <script src=\"script.js\"></script>\n</body>\n</html>",
                language="HTML"
            ),
            FrontendCode(
                file_path="frontend/style.css",
                content="body { font-family: sans-serif; margin: 20px; }\nh1 { color: #333; }\nbutton { padding: 10px 15px; background-color: #007bff; color: white; border: none; cursor: pointer; }\n#output { margin-top: 20px; padding: 10px; border: 1px solid #ccc; }",
                language="CSS"
            ),
            FrontendCode(
                file_path="frontend/script.js",
                content="document.getElementById('fetchData').addEventListener('click', async () => {\n    try {\n        const response = await fetch('/api/v1/data'); // Assuming a backend endpoint\n        const data = await response.json();\n        document.getElementById('output').innerText = JSON.stringify(data, null, 2);\n    } catch (error) {\n        document.getElementById('output').innerText = 'Error fetching data: ' + error;\n    }\n});",
                language="JavaScript"
            )
        ]
        
        print(f"FrontendEngineerAgent: Frontend code generated for {architectural_plan.application_name}.")
        return frontend_files