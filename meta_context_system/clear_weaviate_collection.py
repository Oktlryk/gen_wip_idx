import sys
sys.path.append('D:/Developer/LLM/proj_context_engineering/test_run_copilot/meta_context_system')
from meta_context_studio.src.knowledge_base.vector_store import VectorStore
vs = VectorStore()
vs.clear_collection()