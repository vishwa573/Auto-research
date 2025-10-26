from crewai import Task
from src.agents.planner_agent import planner_agent
from src.agents.search_agent import search_agent
from src.agents.summarizer_agent import summarizer_agent
from src.agents.writer_agent import writer_agent
from src.agents.critic_agent import critic_agent

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

# Task 2: Searching & Scraping (No changes)
search_task = Task(
    description=(
        "You will receive a JSON research plan. For each sub-question in the plan: "
        "1. Use the `Google Search_tool` or `arxiv_search_tool` based on the `source_type` and `keywords`. "
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
    context=[plan_task]
)

# Task 3: Summarization (No changes)
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
    context=[search_task, plan_task]
)

# Task 4: Drafting (UPDATED)
draft_task = Task(
    description=(
        "You will receive a structured summary of findings and the original research plan. "
        "Your job is to synthesize this information into a **first draft** of a professional research report. "
        "The report must be in Markdown format and include: "
        "1. An Abstract (a brief overview of the topic and key findings). "
        "2. An Introduction (based on the original topic). "
        "3. Key Findings (based on the summarized text, organized by theme or sub-question). "
        "4. Challenges / Future Scope (if mentioned in the findings). "
        "5. A list of References (any URLs or ArXiv IDs cited in the summary). "
        "The report should be coherent and well-written. "
        "**IMPORTANT: Do NOT add a date, author name, or any other metadata. "
        "The report should start directly with the main title (e.g., '# Report Title...').**"
    ),
    expected_output=(
        "A comprehensive **first draft** of the research report in Markdown format, "
        "containing all the sections mentioned in the description."
    ),
    agent=writer_agent,
    context=[summarize_task, plan_task]
)

# Task 5: Critiquing (No changes)
critique_task = Task(
    description=(
        "Review the provided draft report. You also have the original research plan "
        "and the summarized findings for context. "
        "Your review must: "
        "1. Check for factual accuracy by cross-referencing the draft against the summarized findings. "
        "2. Check for logical flow, clarity, and good structure. "
        "3. Ensure the report fully addresses all sub-questions from the original research plan. "
        "4. Provide a bullet-point list of actionable feedback for improvement. "
        "If the report is excellent and needs no changes, just say 'The report is excellent and ready to publish.'"
    ),
    expected_output=(
        "A bullet-point list of constructive criticism, feedback, and specific suggestions "
        "for improving the draft report. Or, a single line of approval."
    ),
    agent=critic_agent,
    context=[draft_task, summarize_task, plan_task] # Needs all context
)

# Task 6: Final Revision (UPDATED)
final_report_task = Task(
    description=(
        "You will receive a **first draft** of a report and a list of **critiques** from a senior analyst. "
        "Your job is to meticulously apply all the feedback from the critique to the draft. "
        "Revise the document to create a final, polished, and publishable research report. "
        "If the critique was 'The report is excellent and ready to publish,' then just output the original draft. "
        "**IMPORTANT: Do NOT add a date, author name, or any other metadata. "
        "The final report must start directly with the main title (e.g., '# Report Title...').**"
    ),
    expected_output=(
        "The final, revised, and polished research report in Markdown format. "
        "This version should incorporate all feedback from the critique."
    ),
    agent=writer_agent, # <-- We re-use the writer agent, now in "revise" mode
    context=[draft_task, critique_task] # Needs the draft and the feedback
)

