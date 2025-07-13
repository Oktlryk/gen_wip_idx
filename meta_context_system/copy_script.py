import shutil
import os

source_file = r"D:\Developer\LLM\proj_context_engineering\test_run_copilot\meta_context_system\reports\technical_reports\The Orchestral Conductors of AI_ A Technical Report on LangGraph vs. Haystack for Meta-Context Engineering.html"
destination_dir = r"D:\Developer\LLM\proj_context_engineering\test_run_copilot\meta_context_system\ingestion_queue"

os.makedirs(destination_dir, exist_ok=True)
shutil.copy2(source_file, destination_dir)
print(f"Copied {source_file} to {destination_dir}")