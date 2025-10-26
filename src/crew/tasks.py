from crewai import Task
from src.agents.planner_agent import planner_agent
from src.agents.search_agent import search_agent
from src.agents.summarizer_agent import summarizer_agent
from src.agents.writer_agent import writer_agent

# Import Pydantic models for structured output
from pydantic import BaseModel, Field
from typing import List

# --- Define the JSON Schema for the Research Plan ---
# This tells the Planner Agent *exactly* what its JSON output must look like.
class SubQuestion(BaseModel):
    sub_question: str = Field(..., description="A specific, focused sub-question for research.")
    source_type: str = Field(..., description="Best source type, e.g., 'academic papers', 'recent news', 'blogs'.")
    keywords: List[str] = Field(..., description="A list of 1-2 precise search keywords.")

class ResearchPlan(BaseModel):
    research_plan: List[SubQuestion] = Field(..., description="A list of 3-4 sub-question objects.")
# ----------------------------------------------------


# Task 1: Planning
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
    output_json=ResearchPlan # <-- This is the new, critical line!
)

# Task 2: Searching
search_task = Task(
    description=(
        "Using the 'Research Plan' provided, execute searches for each sub-question. "
        "Use the specified 'source_type' to decide which tool to use: "
        "- If 'academic papers' is specified, use the 'arxiv_search' tool. "
        "- For all other source types ('recent news', 'blogs', etc.), use the 'google_search' tool. "
        "Gather all the raw search results into a single document."
    ),
    expected_output=(
        "A single string document containing all raw search results (snippets, titles, URLs) "
        "found for all sub-questions, clearly separated."
    ),
    agent=search_agent,
    context=[plan_task] # This task depends on the output of the plan_task
)

# Task 3: Summarizing
summarize_task = Task(
    description=(
        "Read and analyze all the 'Raw Search Results' provided. "
        "Condense the information to answer each of the original 'sub_questions' from the 'Research Plan'. "
        "Extract only the most critical findings, data, and insights. "
        "Organize these findings clearly by sub-question."
    ),
    expected_output=(
        "A 'Summarized Insights' document. This document should contain a concise summary "
        "for each sub-question, formatted in clear Markdown. Example:\n"
        "## Key Insights for 'Sub-Question 1'\n"
        "- Insight 1...\n"
        "- Insight 2...\n\n"
        "## Key Insights for 'Sub-Question 2'\n"
        "- Insight 1...\n"
    ),
    agent=summarizer_agent,
    context=[search_task, plan_task] # Depends on the results from search_task and the plan from plan_task
)

# Task 4: Writing the Report
write_report_task = Task(
    description=(
        "Using the 'Summarized Insights' document, compile a final, professional research report "
        "in Markdown format. The report must be structured with the following sections: "
        "- # AutoResearch Report: {topic}\n"
        "- ## Abstract\n"
        "  (A brief, 1-paragraph summary of the entire topic and key findings.)\n"
        "- ## Introduction\n"
        "  (A short introduction to the main research topic.)\n"
        "- ## Key Findings / Trends\n"
        "  (This section should present the 'Summarized Insights' in a clean, readable format.)\n"
        "- ## Challenges / Future Scope\n"
        "  (A brief section on challenges or future outlook, based on the findings.)\n"
        "- ## References\n"
        "  (A list of all the URLs and ArXiv paper IDs gathered from the 'Raw Search Results'.)"
    ),
    expected_output=(
        "The complete, final research report as a single Markdown string, "
        "ready for the user to read or save."
    ),
    agent=writer_agent,
    context=[summarize_task, search_task], # Depends on summaries and the original search results (for references)
    output_file="autoresearch_report.md" # This tells crewAI to save the final output to a file
)

