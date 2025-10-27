import os
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.search_tools import search_tools
from langchain_community.chat_models import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

# Check if the API key is available
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    raise EnvironmentError("GEMINI_API_KEY not found in .env file. Please set it.")

# Initialize the Gemini LLM
# We use "gemini-2.5-flash-preview-09-2025" as it's strong and fast.
# 'convert_system_message_to_human=True' helps with compatibility.
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash-preview-09-2025",
    # model="models/gemini-pro",

    google_api_key=gemini_key,
    verbose=True,
    temperature=0.1, # Low temperature for factual, consistent agent behavior
    convert_system_message_to_human=True
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
search_agent = Agent(
    role="Specialized Research Agent",
    goal=(
        "Execute web and academic searches based on a given plan. "
        "Then, scrape the full text content from the most relevant URLs."
    ),
    backstory=(
        "You are a highly efficient web automaton. You are given a "
        "set of search queries and source types from a planner. "
        "Your job is to use your search tools to find the most "
        "relevant information and then use your scraping tool to "
        "extract the *full text* from those sources for summarization."
    ),
    llm=llm,
    tools=search_tools, # <-- Now includes the scraper tool
    allow_delegation=False,
    verbose=True
)

