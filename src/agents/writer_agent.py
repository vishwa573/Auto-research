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
writer_agent = Agent(
    role="Senior Research Report Writer",
    goal="Compile all summarized insights into a single, coherent, and professionally "
         "formatted research report in Markdown. The report must be well-structured, "
         "following a clear template (Abstract, Introduction, Key Findings, etc.).",
    backstory="You are a distinguished technical writer and editor, known for your ability "
              "to synthesize complex information into clear and compelling reports. "
              "You take the summarized findings from your team and weave them into a "
              "polished, final document that is ready for publication.",
    llm=llm,
    tools=[], # The writer doesn't search, it only organizes and writes.
    allow_delegation=False,
    verbose=True
)
