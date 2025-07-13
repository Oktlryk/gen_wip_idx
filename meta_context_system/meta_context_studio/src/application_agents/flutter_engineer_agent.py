"""Specialized agent for developing mobile applications using Flutter."""
from meta_context_studio.src.agent_orchestration.prompt_aggregator import PromptAggregator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from meta_context_studio.config import settings

class FlutterEngineerAgent:
    """
    The Flutter Engineer Agent is responsible for creating the mobile user interface
    and application logic using Dart and the Flutter framework. It is also
    knowledgeable about integrating on-device LLM capabilities with langchain_dart.
    """

    def __init__(self, prompt_aggregator: PromptAggregator, llm_model: str = settings.DEFAULT_LLM_MODEL):
        """
        Initializes the FlutterEngineerAgent.

        Args:
            prompt_aggregator: An instance of the PromptAggregator.
            llm_model: The LLM model to use for generation.
        """
        self.prompt_aggregator = prompt_aggregator
        self.llm = ChatGoogleGenerativeAI(model=llm_model, temperature=0.7)

    def generate_flutter_app(self, design: str, langchain_logic: str) -> str:
        """
        Creates the Flutter application code based on a design and on-device logic.

        Args:
            design: The high-level design for the user interface and widget structure.
            langchain_logic: A description of the on-device LangChain logic to implement in Dart.

        Returns:
            The generated Flutter application code (main.dart, pubspec.yaml, etc.).
        """
        prompt_content = self.prompt_aggregator.get_prompt(
            "flutter_app_generation",
            {"design": design, "langchain_logic": langchain_logic}
        )

        print(f"FlutterEngineerAgent: Sending prompt to LLM:\n{prompt_content}")
        message = HumanMessage(content=prompt_content)
        response = self.llm.invoke([message])
        code = response.content

        print(f"FlutterEngineerAgent: Received code from LLM:\n{code}")
        return code