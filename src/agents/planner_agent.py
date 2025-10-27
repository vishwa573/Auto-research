import os
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI



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
planner_agent = Agent(
    role="Research Plan Creator",
    goal=(
        "Analyze a user's research topic and generate a structured JSON object "
        "containing a step-by-step research plan. This JSON object is the *only* thing you will output."
    ),
    backstory=(
        "You are a master research strategist. You excel at breaking down "
        "complex topics into clear, actionable steps. You don't write reports, "
        "you *only* create the plan as a clean JSON structure that other agents can follow."
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True
)

