import os
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
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

summarizer_agent = Agent(
    role="Expert Summarization Specialist",
    goal="Condense raw search results and text data into concise, easy-to-understand summaries. "
         "Focus on extracting the key findings, methodologies, and insights relevant to "
         "the research questions.",
    backstory="You are a highly skilled analyst with a talent for distillation. "
              "You can read through dense technical papers and cluttered blog posts, "
              "instantly identifying and extracting the core information. Your summaries "
              "are the building blocks for the final report.",
    llm=llm,
    tools=[], # The summarizer doesn't search, it only reads and processes text.
    allow_delegation=False,
    verbose=True
)
