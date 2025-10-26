import os
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.search_tools import search_tools

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
    model="gemini-2.5-flash-preview-09-2025",
    google_api_key=gemini_key,
    verbose=True,
    temperature=0.1, # Low temperature for factual, consistent agent behavior
    convert_system_message_to_human=True
)

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

