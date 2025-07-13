import os
import shutil
import sys
import argparse
from datetime import datetime

# Programmatically activate the virtual environment
venv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.venv'))
activate_this_file = os.path.join(venv_path, 'Scripts', 'activate_this.py')
if os.path.exists(activate_this_file):
    with open(activate_this_file) as f:
        exec(f.read(), dict(__file__=activate_this_file))
else:
    print(f"Warning: 'activate_this.py' not found at {activate_this_file}. Ensure virtual environment is correctly set up.")

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from meta_context_studio.src.agent_orchestration.meta_agent import MetaAgent
from meta_context_studio.src.application_agents.agent_interfaces import ApplicationRequirements

# Define paths relative to the project root
GENERATED_APPS_PATH = "meta_context_studio/generated_apps"

def setup_generated_apps_environment():
    """Ensures the generated_apps directory exists."""
    os.makedirs(GENERATED_APPS_PATH, exist_ok=True)

def save_generated_application(generated_app_data: dict, run_id: str):
    """
    Saves the generated application files to the file system in a run-specific directory.
    """
    app_name = generated_app_data['application_name']
    app_dir = os.path.join(GENERATED_APPS_PATH, f"{app_name.replace(" ", "_").lower()}_{run_id}")
    os.makedirs(app_dir, exist_ok=True)

    # Save architectural plan
    with open(os.path.join(app_dir, "architectural_plan.json"), "w") as f:
        import json
        json.dump(generated_app_data['architectural_plan'], f, indent=4)

    # Save backend code
    for backend_file in generated_app_data['backend_code']:
        file_path = os.path.join(app_dir, backend_file['file_path'])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(backend_file['content'])

    # Save frontend code
    for frontend_file in generated_app_data['frontend_code']:
        file_path = os.path.join(app_dir, frontend_file['file_path'])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(frontend_file['content'])

    print(f"Generated application '{app_name}' saved to {app_dir}")

def main():
    parser = argparse.ArgumentParser(description="Run the Meta-Agent application generation workflow.")
    parser.add_argument("--summarize", action="store_true", help="Enable context summarization for agents.")
    args = parser.parse_args()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting Meta-Agent application generation workflow (Run ID: {run_id}, Summarize: {args.summarize})...")
    setup_generated_apps_environment()

    meta_agent = MetaAgent()

    # Example Application Requirements
    app_requirements = ApplicationRequirements(
        name="Simple Todo App",
        description="A basic web application to manage todo items.",
        key_features=["Add todo", "List todos", "Mark todo as complete"],
        target_users="Individuals managing personal tasks",
        technologies_preferred=["Python", "FastAPI", "HTML", "CSS", "JavaScript"],
        technologies_avoid=[]
    )

    # Orchestrate the application generation workflow
    workflow_result = meta_agent.orchestrate_workflow(
        workflow_name="generate_application",
        initial_context=app_requirements.model_dump(),
        summarize_context=args.summarize
    )

    if workflow_result['status'] == "workflow_completed":
        generated_app = workflow_result['generated_application']
        save_generated_application(generated_app, run_id)
        print("Meta-Agent application generation workflow finished successfully.")
    else:
        print(f"Meta-Agent application generation workflow failed: {workflow_result.get('reason', 'Unknown reason')}")

if __name__ == "__main__":
    main()