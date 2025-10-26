from crewai import Task
from src.agents.planner_agent import planner_agent
from src.agents.search_agent import search_agent
from src.agents.summarizer_agent import summarizer_agent
from src.agents.writer_agent import writer_agent

from pydantic import BaseModel, Field
from typing import List

# --- Pydantic Schema for the Plan ---
class SubQuestion(BaseModel):
    sub_question: str = Field(..., description="A specific, focused sub-question for research.")
    source_type: str = Field(..., description="Best source type, e.g., 'academic papers', 'recent news', 'blogs'.")
    keywords: List[str] = Field(..., description="A list of 1-2 precise search keywords.")

class ResearchPlan(BaseModel):
    research_plan: List[SubQuestion] = Field(..., description="A list of 3-4 sub-question objects.")

# --- Task Definitions ---

# Task 1: Planning (No changes)
plan_task = Task(
    description=(
        "1. Break down the user's main research topic: '{topic}' into a list of 3-4 specific, "
        "targetable sub-questions. "
        "2. For each sub-question, identify the best type of source to search (e.g., 'academic papers' for technical details, "
        "'recent news' for current events, 'blogs' for opinions). "
        "3. Create a list of 1-2 precise search keywords for each sub-question. "
        "4. Compile this into a valid JSON object. You must output *only* this JSON object."
    ),
    expected_output=(
        "A valid JSON object structured according to the 'ResearchPlan' schema. "
        "This JSON is your *only* output. No preamble or conversational text."
    ),
    agent=planner_agent,
    output_json=ResearchPlan
)

# Task 2: Searching & Scraping (Updated)
search_task = Task(
    description=(
        "You will receive a JSON research plan. For each sub-question in the plan: "
        "1. Use the `Google Search_tool` or `arxiv_search_tool` based on the `source_type` and `keywords`. " # <-- FIXED TYPO HERE (removed space)
        "2. From the search results, identify the single most relevant URL (or ArXiv paper). "
        "3. Use the `scrape_website_tool` to get the full text content from that URL. "
        "   (If it's an ArXiv paper, the summary is sufficient, no need to scrape). "
        "4. Compile all the scraped text and ArXiv summaries into a single large block of text. "
        "   Clearly label where each piece of text came from (e.g., '[Source: example.com]...text...')."
    ),
    expected_output=(
        "A single string containing the combined, raw, unstructured text "
        "from all the scraped web pages and ArXiv summaries. This text "
        "will be used for summarization."
    ),
    agent=search_agent,
    context=[plan_task] # This task depends on the plan
)

# Task 3: Summarization (Updated)
summarize_task = Task(
    description=(
        "You will receive a large block of unstructured text (the research findings) "
        "and the original JSON research plan. Your job is: "
        "1. Read through the unstructured text. "
        "2. Using the sub-questions from the JSON plan as your guide, extract the key "
        "   findings, insights, and data points relevant to *each* sub-question. "
        "3. Compile these findings into a concise, well-structured summary. "
        "   Organize the summary by the original sub-questions. "
        "4. Include any important source URLs you find in the text."
    ),
    expected_output=(
        "A structured summary of the key findings, organized by research sub-question. "
        "This summary will be the direct input for the final report writer."
    ),
    agent=summarizer_agent,
    context=[search_task, plan_task] # Depends on the scraped text AND the original plan
)

# Task 4: Writing (Updated)
write_task = Task(
    description=(
        "You will receive a structured summary of findings and the original research plan. "
        "Your job is to synthesize this information into a final, professional research report. "
        "The report must be in Markdown format and include: "
        "1. An Abstract (a brief overview of the topic and key findings). "
        "2. An Introduction (based on the original topic). "
        "3. Key Findings (based on the summarized text, organized by theme or sub-question). "
        "4. Challenges / Future Scope (if mentioned in the findings). "
        "5. A list of References (any URLs or ArXiv IDs cited in the summary). "
        "The report should be coherent, well-written, and directly address the user's original topic."
    ),
    expected_output=(
        "A final, polished research report in Markdown format, "
        "containing all the sections mentioned in the description."
    ),
    agent=writer_agent,
    context=[summarize_task, plan_task] # Depends on the summary AND the original plan/topic
)

