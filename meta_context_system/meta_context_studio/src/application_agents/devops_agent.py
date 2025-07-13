"""Specialized agent for creating deployment configurations and CI/CD pipelines."""
from meta_context_studio.src.agent_orchestration.prompt_aggregator import PromptAggregator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from meta_context_studio.config import settings

class DevOpsAgent:
    """
    The DevOps Agent is responsible for creating deployment configurations.
    """

    def __init__(self, prompt_aggregator: PromptAggregator, llm_model: str = settings.DEFAULT_LLM_MODEL):
        """
        Initializes the DevOpsAgent.

        Args:
            prompt_aggregator: An instance of the PromptAggregator.
            llm_model: The LLM model to use for generation.
        """
        self.prompt_aggregator = prompt_aggregator
        self.llm = ChatGoogleGenerativeAI(model=llm_model, temperature=0.7)

    def create_deployment(self, architecture: str) -> str:
        """
        Creates a deployment configuration based on an architecture.

        Args:
            architecture: The architecture of the application.

        Returns:
            The generated deployment configuration.
        """
        prompt_content = self.prompt_aggregator.get_prompt(
            "devops_deployment",
            {"architecture": architecture}
        )

        print(f"DevOpsAgent: Sending prompt to LLM:\n{prompt_content}")
        message = HumanMessage(content=prompt_content)
        response = self.llm.invoke([message])
        config = response.content

        print(f"DevOpsAgent: Received configuration from LLM:\n{config}")
        return config
