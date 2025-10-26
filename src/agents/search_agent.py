import os
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.search_tools import google_search, arxiv_search
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
    role="Expert Search & Retrieval Specialist",
    goal="Find the most relevant and up-to-date information for a given set of research questions. "
         "You must use the provided search tools to find information from both general web sources and academic paper databases.",
    backstory="You are a master of information retrieval. You know exactly how to craft "
              "the right search queries for any topic. You can sift through "
              "Google and ArXiv to find the most precise and authoritative sources "
              "needed to answer the research plan.",
    llm=llm,
    tools=[
        google_search,
        arxiv_search
    ],
    allow_delegation=False,
    verbose=True
)
