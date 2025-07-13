import os

directories = [
    r'D:\Developer\LLM\proj_context_engineering\test_run_copilot\meta_context_system\ingestion_queue',
    r'D:\Developer\LLM\proj_context_engineering\test_run_copilot\meta_context_system\ingestion_done',
    r'D:\Developer\LLM\proj_context_engineering\test_run_copilot\meta_context_system\meta_context_studio\src\context_management\ingestion',
    r'D:\Developer\LLM\proj_context_engineering\test_run_copilot\meta_context_system\meta_context_studio\request_for_resolution'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")
