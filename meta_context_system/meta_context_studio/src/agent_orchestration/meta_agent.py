from typing import List
from meta_context_studio.src.knowledge_base.graph_store import GraphStore
from meta_context_studio.src.context_management.retrieval.context_retriever import ContextRetriever
from meta_context_studio.src.application_agents.architect_agent import ArchitectAgent
from meta_context_studio.src.application_agents.backend_engineer_agent import BackendEngineerAgent
from meta_context_studio.src.application_agents.frontend_engineer_agent import FrontendEngineerAgent
from langchain_google_genai import ChatGoogleGenerativeAI # Import LLM for agents
from meta_context_studio.src.application_agents.agent_interfaces import ApplicationRequirements, GeneratedApplication
from meta_context_studio.src.reasoning_core.self_reflection import SelfReflectionModule # New import
from meta_context_studio.src.context_management.context_refinement import ContextRefinementModule # New import

class MetaAgent:
    """
    The central orchestrating agent of the Genesis Engine.
    Responsible for coordinating various specialized agents, managing workflows,
    and ensuring the overall system objectives are met.
    """
    def __init__(self):
        self.agents: List[str] = [] # Placeholder for registered agents
        self.context_retriever = ContextRetriever()
        self.graph_store = GraphStore()
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.7) # Initialize LLM for agents
        self.architect_agent = ArchitectAgent(llm=self.llm)
        self.backend_engineer_agent = BackendEngineerAgent(llm=self.llm)
        self.frontend_engineer_agent = FrontendEngineerAgent(llm=self.llm)
        self.self_reflection_module = SelfReflectionModule() # Initialize SelfReflectionModule
        self.context_refinement_module = ContextRefinementModule() # Initialize ContextRefinementModule

    

    def retrieve_context_from_kb(self, query: str, top_k: int = 5, summarize_context: bool = False) -> str:
        """
        Retrieves relevant context from the knowledge base using the ContextRetriever.
        """
        print(f"MetaAgent: Retrieving context for query: '{query}' (top_k={top_k}, summarize={summarize_context})")
        return self.context_retriever.retrieve_context(query, top_k, summarize_context=summarize_context)

    def query_graph_store(self, sparql_query: str) -> List[dict]:
        """
        Queries the graph store using a SPARQL query.
        """
        print(f"MetaAgent: Querying graph store with SPARQL query: {sparql_query}")
        return self.graph_store.query_graph(sparql_query)

    def orchestrate_workflow(self, workflow_name: str, initial_context: dict, summarize_context: bool = False) -> dict:
        """
        Orchestrates a specific workflow by coordinating registered agents.
        This version orchestrates application generation.
        """
        print(f"MetaAgent: Orchestrating workflow '{workflow_name}' with initial context: {initial_context}")

        if workflow_name == "generate_application":
            # 1. Plan: Extract application requirements
            app_requirements = ApplicationRequirements(**initial_context)
            print(f"MetaAgent: Planning application generation for {app_requirements.name}...")

            # 2. Execute: Architect Agent
            print("MetaAgent: Delegating to Architect Agent...")
            # Retrieve context for the Architect Agent
            architect_context = self.retrieve_context_from_kb(f"architectural patterns for {app_requirements.name}", summarize_context=summarize_context)
            architectural_plan = self.architect_agent.generate_architectural_plan(app_requirements, context=architect_context)
            print("MetaAgent: Architectural plan received.")

            # 3. Execute: Backend Engineer Agent
            print("MetaAgent: Delegating to Backend Engineer Agent...")
            # Retrieve context for the Backend Engineer Agent
            backend_context = self.retrieve_context_from_kb(f"backend development best practices for {app_requirements.name}", summarize_context=summarize_context)
            backend_code = self.backend_engineer_agent.generate_backend_code(architectural_plan, context=backend_context)
            print(f"MetaAgent: Backend code generated ({len(backend_code)} files).")

            # 4. Execute: Frontend Engineer Agent
            print("MetaAgent: Delegating to Frontend Engineer Agent...")
            # Retrieve context for the Frontend Engineer Agent
            frontend_context = self.retrieve_context_from_kb(f"frontend development best practices for {app_requirements.name}", summarize_context=summarize_context)
            frontend_code = self.frontend_engineer_agent.generate_frontend_code(architectural_plan, context=frontend_context)
            print(f"MetaAgent: Frontend code generated ({len(frontend_code)} files).")

            # 5. Reflect: Assemble generated application
            generated_app = GeneratedApplication(
                application_name=app_requirements.name,
                architectural_plan=architectural_plan,
                backend_code=backend_code,
                frontend_code=frontend_code
            )
            print(f"MetaAgent: Application '{generated_app.application_name}' generated successfully.")

            workflow_outcome = {"status": "workflow_completed", "workflow_name": workflow_name, "generated_application": generated_app.model_dump()}

            # Self-reflection
            reflection_insights = self.self_reflection_module.reflect_on_workflow_outcome(workflow_name, workflow_outcome)
            print(f"MetaAgent: Reflection insights: {reflection_insights}")

            # Context refinement
            refined_context = self.context_refinement_module.refine_context(reflection_insights)
            print(f"MetaAgent: Refined context: {refined_context}")

            return workflow_outcome
        else:
            print(f"MetaAgent: Unknown workflow: {workflow_name}")
            workflow_outcome = {"status": "failed", "reason": "unknown_workflow"}
            
            # Self-reflection for failed workflow
            reflection_insights = self.self_reflection_module.reflect_on_workflow_outcome(workflow_name, workflow_outcome)
            print(f"MetaAgent: Reflection insights for failed workflow: {reflection_insights}")

            # Context refinement for failed workflow
            refined_context = self.context_refinement_module.refine_context(reflection_insights)
            print(f"MetaAgent: Refined context for failed workflow: {refined_context}")

            return workflow_outcome

    def delegate_task(self, task_description: str, target_agent: str, task_context: dict = None) -> dict:
        """
        Delegates a specific task to a registered specialized agent.
        """
        if target_agent not in self.agents:
            print(f"MetaAgent: Error - Agent '{target_agent}' not registered.")
            return {"status": "failed", "reason": "agent_not_registered"}

        print(f"MetaAgent: Delegating task '{task_description}' to '{target_agent}'. Context: {task_context}")
        # In a real scenario, this would involve:
        # 1. Sending the task to the target_agent's input queue or method.
        # 2. Waiting for the agent's response or status update.
        # 3. Handling potential errors or timeouts.

        return {"status": "task_delegated", "task": task_description, "agent": target_agent, "context": task_context}
