"""Global configurations for the Meta-Context Engineering System."""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file at the project root.
# This allows for secure and flexible configuration of API keys and other secrets.
# It should be called before any other code that relies on environment variables.
load_dotenv()

# Placeholder for LLM API keys
LLM_API_KEYS = {
    # The second argument to os.environ.get is a default value if the env var is not found.
    "gemini": os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"),
    "groq": os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY"),
}

# Default LLM model to use
DEFAULT_LLM_MODEL = "models/gemini-2.5-flash" # Or "llama3-8b-8192" for Groq

# Default embedding model
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Base path for the knowledge base
KNOWLEDGE_BASE_PATH = "lancedb_data"

# LanceDB Configuration
LANCE_TABLE_NAME = "genesis_knowledge_base"
