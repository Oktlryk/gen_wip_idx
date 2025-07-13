import os
file_to_delete = "D:/Developer/LLM/proj_context_engineering/test_run_copilot/meta_context_system/meta_context_studio/src/knowledge_base/vector_store.py"
if os.path.exists(file_to_delete):
    os.remove(file_to_delete)
    print(f"Deleted: {file_to_delete}")
else:
    print(f"File not found: {file_to_delete}")