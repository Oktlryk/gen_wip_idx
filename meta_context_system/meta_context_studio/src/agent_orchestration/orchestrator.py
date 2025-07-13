"""
The central orchestrator (Meta-Agent) for the Genesis Engine.
This module is responsible for selecting and executing the correct
agentic workflow based on the user's high-level request.
"""
from meta_context_studio.src.agent_orchestration.prompt_aggregator import PromptAggregator
from meta_context_studio.src.application_agents.architect_agent import ArchitectAgent
from meta_context_studio.src.application_agents.backend_engineer_agent import BackendEngineerAgent
from meta_context_studio.src.application_agents.frontend_engineer_agent import FrontendEngineerAgent
from meta_context_studio.src.application_agents.flutter_engineer_agent import FlutterEngineerAgent
from meta_context_studio.src.application_agents.test_generation_agent import TestGenerationAgent
from meta_context_studio.src.application_agents.integration_agent import IntegrationAgent


class Orchestrator:
    """
    The Meta-Agent orchestrator. It selects and runs the appropriate workflow
    based on the user's request, acting as the central nervous system for the
    Genesis Engine's application generation capabilities.
    """

    def __init__(self):
        """Initializes the orchestrator and all specialized agents."""
        self.prompt_aggregator = PromptAggregator()

        # Instantiate all agents that can be part of a workflow
        self.architect = ArchitectAgent(self.prompt_aggregator)
        self.backend_engineer = BackendEngineerAgent(self.prompt_aggregator)
        self.frontend_engineer = FrontendEngineerAgent(self.prompt_aggregator)
        self.flutter_engineer = FlutterEngineerAgent(self.prompt_aggregator)
        self.test_generator = TestGenerationAgent(self.prompt_aggregator)
        self.integrator = IntegrationAgent(self.prompt_aggregator)

    def run_workflow(self, user_prompt: str) -> dict:
        """
        Analyzes the user prompt and runs the corresponding application generation workflow.
        This method embodies the logic of the Meta-Agent.

        Args:
            user_prompt: The high-level user request for an application.

        Returns:
            A dictionary representing the generated and integrated application files.
        """
        # A simple keyword-based workflow selection mechanism. This can be evolved
        # into a more sophisticated LLM-based router.
        if "flutter" in user_prompt.lower() or "mobile app" in user_prompt.lower():
            print("INFO: Mobile App Workflow selected.")
            return self._run_mobile_app_workflow(user_prompt)
        else:
            print("INFO: Web App Workflow selected.")
            return self._run_web_app_workflow(user_prompt)

    def _run_web_app_workflow(self, user_prompt: str) -> dict:
        """
        Orchestrates the generation of a standard web application with a frontend and backend.
        """
        print("--- Starting Web App Workflow ---")
        print("Step 1: Designing application architecture...")
        design = self.architect.design_architecture(user_prompt)
        schema = self.architect.design_schema(user_prompt)

        print("Step 2: Generating backend...")
        backend_code = self.backend_engineer.generate_api_endpoint(design, schema)

        print("Step 3: Generating frontend...")
        frontend_code = self.frontend_engineer.generate_ui(design)

        print("Step 4: Generating tests...")
        backend_tests = self.test_generator.generate_backend_tests(backend_code)
        frontend_tests = self.test_generator.generate_frontend_tests(frontend_code)

        print("Step 5: Integrating application...")
        final_app = {"backend_code": backend_code, "frontend_code": frontend_code, "backend_tests": backend_tests, "frontend_tests": frontend_tests}
        self.integrator.integrate_application(final_app)
        print("--- Web App Workflow Complete ---")
        return final_app

    def _run_mobile_app_workflow(self, user_prompt: str) -> dict:
        """
        Orchestrates the generation of a backend-less Flutter mobile application.
        """
        print("--- Starting Mobile App Workflow ---")
        print("Step 1: Designing mobile application architecture...")
        design = self.architect.design_architecture(user_prompt)
        langchain_logic = "Implement on-device AI capabilities using langchain_dart."

        print("Step 2: Generating Flutter application...")
        flutter_code = self.flutter_engineer.generate_flutter_app(design, langchain_logic)

        print("Step 3: Generating tests...")
        flutter_tests = self.test_generator.generate_flutter_tests(flutter_code)

        print("Step 4: Integrating application...")
        final_app = {"flutter_code": flutter_code, "flutter_tests": flutter_tests}
        self.integrator.integrate_application(final_app)
        print("--- Mobile App Workflow Complete ---")
        return final_app