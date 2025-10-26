from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# This is the first thing we do to ensure keys are available
load_dotenv()

# Check if the API key is available
if not os.getenv("GEMINI_API_KEY"):
    raise EnvironmentError("GEMINI_API_KEY not found in .env file. Please set it.")

# Initialize the Gemini LLM
# We use "gemini-2.5-flash-preview-09-2025" as it's strong and fast.
# 'convert_system_message_to_human=True' helps with compatibility.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-09-2025",
    verbose=True,
    temperature=0.1, # Low temperature for factual, consistent agent behavior
    convert_system_message_to_human=True
)