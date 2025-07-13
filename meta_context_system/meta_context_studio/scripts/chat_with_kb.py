import gradio as gr
from meta_context_studio.src.context_management.retrieval.context_retriever import ContextRetriever
from meta_context_studio.config import settings
from meta_context_studio.src.utils.environment import verify_venv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# --- Backend Setup ---
# Enforce the rule from GEMINI.md that all operations must run in the correct venv.
# verify_venv() --- needs fixing

# Initialize the context retriever once at startup.
try:
    context_retriever = ContextRetriever()
    RETRIEVER_SUCCESS = True
    INITIALIZATION_MESSAGE = "Ready to chat."
except Exception as e:
    context_retriever = None
    RETRIEVER_SUCCESS = False
    INITIALIZATION_MESSAGE = f"Error initializing Context Retriever: {e}\n\nHave you run the ingestion pipeline? (run-ingestion)"

# Initialize the LLM for the "Generation" part of RAG
try:
    if not settings.LLM_API_KEYS["gemini"] or "YOUR_GEMINI_API_KEY" in settings.LLM_API_KEYS["gemini"]:
        raise ValueError("Gemini API key is not set. Please configure it in meta_context_studio/config/settings.py or as an environment variable.")
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=settings.LLM_API_KEYS["gemini"])
    LLM_SUCCESS = True
except Exception as e:
    llm = None
    LLM_SUCCESS = False
    INITIALIZATION_MESSAGE = f"Error initializing LLM: {e}"


def chat_fn(query: str, history: list):
    """
    Function to handle the chat interaction.
    'history' is managed by Gradio and is a list of [user, bot] message pairs.
    """
    history = history or []

    if not RETRIEVER_SUCCESS or not LLM_SUCCESS:
        history.append((query, INITIALIZATION_MESSAGE))
        return history

    if not query:
        # Silently ignore empty queries, or you could add a message like:
        # history.append((None, "Please enter a question."))
        return history

    # 1. Retrieve context from the knowledge base
    retrieved_context = context_retriever.retrieve_context(query, top_k=3)

    # 2. Create prompt for LLM
    prompt_template = f"""You are a helpful assistant for the Genesis Engine project. Answer the user's question based ONLY on the following context provided. If the context does not contain the answer, state that you cannot answer based on the provided information.

--- CONTEXT ---
{retrieved_context}
--- END CONTEXT ---

Question: {query}
"""

    # 3. Invoke LLM to generate a conversational answer
    try:
        messages = [HumanMessage(content=prompt_template)]
        ai_response = llm.invoke(messages)
        response_text = ai_response.content
    except Exception as e:
        response_text = f"An error occurred while generating the response: {e}"

    # 4. Update history
    history.append((query, response_text))
    return history

# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft(), title="Chat with Knowledge Base") as demo:
    gr.Markdown("# Chat with Knowledge Base (RAG)")
    gr.Markdown("Ask a question about the project. The system will perform a semantic search on the knowledge base, provide the relevant context to an LLM, and generate a conversational answer.")
    
    chatbot = gr.Chatbot(label="Conversation", height=600)
    msg = gr.Textbox(label="Your Question", placeholder="e.g., How does the ContextRetriever work?")
    clear = gr.ClearButton([msg, chatbot])

    # The `then` event clears the input textbox after submission
    msg.submit(chat_fn, [msg, chatbot], chatbot).then(
        lambda: gr.update(value=""), None, [msg], queue=False
    )

def main():
    """Launches the Gradio web server."""
    demo.launch()

if __name__ == "__main__":
    main()
