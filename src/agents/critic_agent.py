from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash-preview-09-2025",
    verbose=True,
    temperature=0.2, # Critics should be precise, not overly creative
    google_api_key=os.getenv("GEMINI_API_KEY")
)

critic_agent = Agent(
    role="Senior Research Analyst & Critic",
    goal=(
        "Review a draft research report for factual accuracy, logical flow, "
        "clarity, and depth. Provide specific, actionable feedback for improvement."
    ),
    backstory=(
        "You are a meticulous editor with decades of experience at a top-tier "
        "research institution. Your job is not to be nice, but to be *precise*. "
        "You identify logical fallacies, unsupported claims, poor structure, "
        "and any content that doesn't align with the original research plan. "
        "Your feedback is the crucible that turns good reports into great ones."
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True
)
