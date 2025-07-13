"""Specialized agent for producing unit, integration, and end-to-end tests."""
from meta_context_studio.src.agent_orchestration.prompt_aggregator import PromptAggregator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from meta_context_studio.config import settings

class TestGenerationAgent:
    """
    The Test Generation Agent is responsible for creating tests for the application.
    """

    def __init__(self, prompt_aggregator: PromptAggregator, llm_model: str = settings.DEFAULT_LLM_MODEL):
        """
        Initializes the TestGenerationAgent.

        Args:
            prompt_aggregator: An instance of the PromptAggregator.
            llm_model: The LLM model to use for generation.
        """
        self.prompt_aggregator = prompt_aggregator
        self.llm = ChatGoogleGenerativeAI(model=llm_model, temperature=0.7)

    def generate_tests(self, code: str) -> str:
        """
        Generates tests for a given code.

        Args:
            code: The code to generate tests for.

        Returns:
            The generated tests.
        """
        prompt_content = self.prompt_aggregator.get_prompt(
            "test_generation",
            {"code": code}
        )

        print(f"TestGenerationAgent: Sending prompt to LLM:\n{prompt_content}")
        message = HumanMessage(content=prompt_content)
        response = self.llm.invoke([message])
        tests = response.content

        print(f"TestGenerationAgent: Received tests from LLM:\n{tests}")
        return tests
