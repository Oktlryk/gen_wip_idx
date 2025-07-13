import os
import sys
from pprint import pprint

# Add the project root to the Python path to ensure imports work correctly
# when running this script from the command line.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from meta_context_studio.src.knowledge_base.analyzer import KnowledgeBaseAnalyzer
from meta_context_studio.config import settings

def main():
    """
    Runs the KnowledgeBaseAnalyzer to identify knowledge gaps based on the
    current content of the LanceDB knowledge base and prints the resulting
    report requests to the console.
    """
    print("--- Starting Knowledge Base Analysis ---")

    # We explicitly configure the KnowledgeBaseAnalyzer to use the path and table
    # name from the central settings file, overriding any defaults.
    try:
        # Backwards compatibility patch: The analyzer might expect GEMINI_API_KEY directly
        # on settings, while newer parts of the app use the LLM_API_KEYS dictionary.
        if not hasattr(settings, "GEMINI_API_KEY") and hasattr(
            settings, "LLM_API_KEYS"
        ):
            gemini_key = settings.LLM_API_KEYS.get("gemini")
            if gemini_key and "YOUR_GEMINI_API_KEY" not in gemini_key:
                setattr(settings, "GEMINI_API_KEY", gemini_key)
            else:
                raise ValueError("Gemini API key is not configured in settings.LLM_API_KEYS")
        
        print(f"Loading knowledge base from '{settings.KNOWLEDGE_BASE_PATH}' using table '{settings.LANCE_TABLE_NAME}'...")
        analyzer = KnowledgeBaseAnalyzer(
            knowledge_base_uri=settings.KNOWLEDGE_BASE_PATH,
            table_name=settings.LANCE_TABLE_NAME,
        )
        report_requests = analyzer.generate_report_requests()

        if report_requests:
            print("\n✅ --- Generated Report Requests --- ✅")
            for i, req in enumerate(report_requests, 1):
                print(f"\n--- Request {i} ---")
                # Use pprint for a nicely formatted output of the Pydantic model
                pprint(req.model_dump())
        else:
            print("\nℹ️ --- No new report requests were generated at this time. ---")

    except Exception as e:
        print(f"\n❌ --- An error occurred during analysis --- ❌")
        print(f"Error: {e}")
        print(
            "Please ensure your Gemini API key is configured correctly in 'meta_context_studio/config/settings.py' under the 'LLM_API_KEYS' dictionary."
        )

    print("\n--- Knowledge Base Analysis Complete ---")

if __name__ == "__main__":
    main()