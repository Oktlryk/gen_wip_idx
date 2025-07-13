from setuptools import setup, find_packages

setup(
    name="meta-context-studio",
    version="0.1.0",
    packages=find_packages(),
    description="The Genesis Engine: A Meta-Context Engineering System",
    author="Gemini Code Assist",
    author_email="no-reply@google.com",
    install_requires=[
        "fastapi",
        "uvicorn",
        "gradio",
        "pydantic-settings",
        "langchain",
        "langchain-community",
        "haystack-ai",
        "lancedb",
        "rdflib",
        "sentence-transformers",
        "pypdf",
        "python-dotenv",
    ],
    entry_points={
        'console_scripts': [
            'verify-kb = meta_context_studio.scripts.verify_kb:verify_knowledge_base',
            'browse-kb = meta_context_studio.scripts.browse_knowledge_base:main',
            'chat-with-kb = meta_context_studio.scripts.chat_with_kb:main',
            'run-ingestion = meta_context_studio.scripts.run_ingestion:main',
            'run-meta-agent = meta_context_studio.scripts.run_meta_agent:main',
        ],
    },
)