"""Manages PER loops, task decomposition, and state transitions."""
from typing import Dict, Any, List
from meta_context_studio.src.agent_orchestration.agent_registry import AgentRegistry
from meta_context_studio.src.application_agents.code_cleanup_agent import CodeCleanupAgent

class WorkflowManager:
    """
    Manages the execution of workflows, including Plan-Execute-Reflect (PER) loops.
    """

    def __init__(self):
        self.code_cleanup_agent = CodeCleanupAgent()

    def execute_workflow(self, plan: List[Dict[str, Any]], agent_registry: AgentRegistry) -> Dict[str, Any]:
        """
        Executes a workflow based on a plan from the Meta-Agent.

        Args:
            plan: A list of dictionaries, where each dictionary represents a sub-task.
            agent_registry: An instance of AgentRegistry to access specialized agents.

        Returns:
            A dictionary containing the results of the workflow execution.
        """
        results = {}
        previous_step_output = None

        for i, step in enumerate(plan):
            agent_name = step["agent"]
            task = step["task"]
            print(f"WorkflowManager: Executing step {i+1}/{len(plan)} - Agent: {agent_name}, Task: {task}")

            # Retrieve the agent from the registry
            agent = agent_registry.get_agent(agent_name)
            if not agent:
                print(f"WorkflowManager: Error - Agent '{agent_name}' not found.")
                continue

            # Execute the agent's task
            raw_output = self._execute_agent_task(agent, task, previous_step_output, results)

            # Clean the code if it's from a code-generating agent
            if agent_name in ['ArchitectAgent', 'BackendEngineerAgent', 'FrontendEngineerAgent', 'TestGenerationAgent', 'DevOpsAgent']:
                cleaned_output = self.code_cleanup_agent.clean_code(raw_output)
                results[agent_name] = cleaned_output
            else:
                results[agent_name] = raw_output
            
            previous_step_output = results[agent_name]

        return results

    def _execute_agent_task(self, agent: Any, task: str, input_data: Any, all_results: Dict[str, Any]) -> str:
        """
        Executes a single agent's task.
        """
        if hasattr(agent, "design_architecture"):
            return agent.design_architecture(task, "")
        elif hasattr(agent, "generate_api_endpoint"):
            return agent.generate_api_endpoint(task, input_data)
        elif hasattr(agent, "create_ui"):
            return agent.create_ui(input_data)
        elif hasattr(agent, "create_deployment"):
            return agent.create_deployment(input_data)
        elif hasattr(agent, "generate_tests"):
            return agent.generate_tests(input_data)
        elif hasattr(agent, "build_application"):
            return agent.build_application(task, all_results)
        else:
            return f"Error: Agent {agent.__class__.__name__} does not have a recognized execution method."
