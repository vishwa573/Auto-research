from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os

from langchain.chat_models import ChatOpenAI

# --- Import the new tool ---
from src.tools.rag_tools import rag_query_tool

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash-preview-09-2025",
    # model="models/gemini-pro",

    verbose=True,
    temperature=0.3, # Slightly more creative for summarization
    google_api_key=os.getenv("GEMINI_API_KEY")
)
# openai_key = os.getenv("OPENAI_API_KEY")
# if not openai_key:
#     raise EnvironmentError("OPENAI_API_KEY missing in .env")

# # LangChain LLM wrapper (works with your langchain 0.1.20)
# llm = ChatOpenAI(
#     model_name="gpt-3.5-turbo",   # or "gpt-4o-mini", "gpt-4o"
#     temperature=0.2,
#     openai_api_key=openai_key     # explicit pass (optional if env var is set)
# )
summarizer_agent = Agent(
    role="Specialized Research Summarizer",
    goal=(
        "Receive a large block of unstructured text and a JSON research plan. "
        "For *each* sub-question in the plan, use the `rag_query_tool` "
        "to find the *most relevant* information from the text. "
        "Then, compile a concise summary based *only* on the relevant snippets."
    ),
    backstory=(
        "You are an expert in information retrieval and data synthesis. "
        "You don't just read and summarize; you intelligently query the provided "
        "text using RAG to extract *only* the most precise, relevant information. "
        "Your skill lies in ignoring the noise and focusing on the signal, "
        "answering each research question directly with supporting evidence "
        "from the provided context."
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True,
    # --- Give the new tool to the agent ---
    tools=[rag_query_tool]
)

