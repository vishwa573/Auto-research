# from crewai import Task
# from src.agents.planner_agent import planner_agent
# from src.agents.search_agent import search_agent
# from src.agents.summarizer_agent import summarizer_agent
# from src.agents.writer_agent import writer_agent
# from src.agents.critic_agent import critic_agent

# from pydantic import BaseModel, Field
# from typing import List, Dict

# # --- Pydantic Schema for the Plan ---
# class SubQuestion(BaseModel):
#     sub_question: str = Field(..., description="A specific, focused sub-question for research.")
#     source_type: str = Field(..., description="Best source type, e.g., 'academic papers', 'recent news', 'blogs'.")
#     keywords: List[str] = Field(..., description="A list of 1-2 precise search keywords.")

# class ResearchPlan(BaseModel):
#     research_plan: List[SubQuestion] = Field(..., description="A list of 3-4 sub-question objects.")

# # --- Pydantic Schema for Search Output ---
# class SourceItem(BaseModel):
#     """A single item of retrieved content, with its source."""
#     source: str = Field(..., description="The URL or ArXiv ID of the content.")
#     content: str = Field(..., description="The scraped text or summary from that source.")

# # --- NEW: Consolidated Data Schema ---
# class ConsolidatedData(BaseModel):
#     """A model to bundle the plan and search results together for the next step."""
#     plan: ResearchPlan = Field(..., description="The original research plan.")
#     sources: List[SourceItem] = Field(..., description="The list of retrieved sources and their content.")


# # --- Task Definitions ---

# # Task 1: Planning
# plan_task = Task(
#     description=(
#         "1. Break down the user's main research topic: '{topic}' into a list of 3-4 specific, "
#         "targetable sub-questions. "
#         "2. For each sub-question, identify the best type of source to search (e.g., 'academic papers' for technical details, "
#         "'recent news' for current events, 'blogs' for opinions). "
#         "3. Create a list of 1-2 precise search keywords for each sub-question. "
#         "4. Compile this into a valid JSON object. You must output *only* this JSON object."
#     ),
#     expected_output=(
#         "A valid JSON object structured according to the 'ResearchPlan' schema. "
#         "This JSON is your *only* output. No preamble or conversational text."
#     ),
#     agent=planner_agent,
#     output_json=ResearchPlan,
#     max_retries=2  # <-- ADDED FOR RESILIENCE
# )

# # Task 2: Searching & Scraping
# search_task = Task(
#     description=(
#         "You will receive a 'ResearchPlan' object. You must store this plan. "
#         "Then, for each sub-question in the 'plan.research_plan' list: "
        
#         "1. **Formulate the query:** Take the `keywords` list for the sub-question. "
#         "   Join them together with ' OR ' to create a single query string. "
#         "   For example, if keywords are ['Generative AI', 'Text-to-CAD'], the query "
#         "   string becomes 'Generative AI OR Text-to-CAD'. "
        
#         "2. **Search:** Use the `google_search_tool` or `arxiv_search_tool` (based on `source_type`) "
#         "   with this new 'OR' query string. "
        
#         "3. **Process Results:** From the search results, identify the single most relevant "
#         "   URL (or ArXiv paper). "
        
#         "4. **Scrape:** Use the `scrape_website_tool` to get the full text content from that URL. "
#         "   (If it's an ArXiv paper, use the paper's summary as the content). "
#         "   **IMPORTANT: If the scrape fails or the search tool returns 'No results', "
#         "   just use the 'No results' message or the snippet from the search result as the content. "
#         "   Do not stop or error out.** "
        
#         "5. **Format:** Create a `SourceItem` object for this finding. "
#         "6. Collect all these `SourceItem` objects into a list. "
        
#         "7. **Bundle:** Finally, create a 'ConsolidatedData' object. Put the *original 'ResearchPlan' object* "
#         "   you received into the 'plan' field, and put your new list of 'SourceItem' objects "
#         "   into the 'sources' field."
#     ),
#     expected_output=(
#         "A valid JSON object structured according to the 'ConsolidatedData' schema. "
#         "This object contains *both* the original plan and the new search results."
#     ),
#     agent=search_agent,
#     context=[plan_task],
#     output_json=ConsolidatedData,
#     max_retries=2  # <-- ADDED FOR RESILIENCE
# )

# # Task 3: Summarization
# summarize_task = Task(
#     description=(
#         "You will receive **one** 'ConsolidatedData' object. "
#         "This object contains two attributes: 'plan' (the ResearchPlan) and 'sources' (the list of SourceItems). "
#         "Your job is to generate a summary for *each* sub-question in the 'plan.research_plan' list. "
        
#         "**You must follow this process exactly:**"
#         "1. Access the research plan from the 'plan' attribute. "
#         "2. Access the list of sources from the 'sources' attribute. This is your 'context_list'. "
#         "3. For the *first* sub-question in the 'plan.research_plan' list: "
#         "4. Call the `rag_query_tool` using that sub-question as the `question` "
#         "   and the `context_list` (from the 'sources' attribute). "
#         "5. The tool will return relevant snippets, *with their sources*. "
#         "6. Read these snippets (or the 'No valid content' message) and write a concise "
#         "   summary that answers the sub-question, making sure to include any "
#         "   `[Source: ...]` tags you find. "
#         "7. Repeat this process for *all* sub-questions in the 'plan.research_plan' list. "
#         "8. Compile all the individual summaries (with their sources) into a "
#         "   single, well-structured Markdown document, organized by the sub-questions."
#     ),
#     expected_output=(
#         "A structured summary of the key findings, organized by research sub-question. "
#         "This summary *must* be based on the snippets retrieved by the "
#         "`rag_query_tool` and *must* include the `[Source: ...]` tags "
#         "provided by the tool."
#     ),
#     agent=summarizer_agent,
#     context=[search_task],
#     max_retries=2  # <-- ADDED FOR RESILIENCE
# )


# # Task 4: Drafting
# draft_task = Task(
#     description=(
#         "You will receive a structured summary of findings (which includes `[Source: ...]` tags). "
#         "Your job is to synthesize this information into a **first draft** of a professional research report. "
#         "The report must be in Markdown format and include: "
#         "1. An Abstract (a brief overview of the topic and key findings). "
#         "2. An Introduction (based on the original topic). "
#         "3. Key Findings (based on the summarized text, organized by theme or sub-question). "
#         "4. Challenges / Future Scope (if mentioned in the findings). "
#         "5. A **References** section. You must parse all the `[Source: ...]` tags "
#         "   from the summary. For each unique source, create a numbered list item "
#         "   that contains **only the raw, full URL**. "
#         "   **Example:** "
#         "   ### References"
#         "   1. https://arxiv.org/abs/2105.09492"
#         "   2. https://www.forbes.com/article/..."
#         "   **Do NOT add titles, authors, or any other bibliographic information. Just the links.**"

#         "**IMPORTANT: Do NOT add a date, author name, or any other metadata. "
#         "The report should start directly with the main title (e.Sg., '# Report Title...').**"
#     ),
#     expected_output=(
#         "A comprehensive **first draft** of the research report in Markdown format, "
#         "containing all the sections mentioned, including a 'References' section "
#         "built from *only* raw source URLs."
#     ),
#     agent=writer_agent,
#     context=[summarize_task],
#     max_retries=2  # <-- ADDED FOR RESILIENCE
# )

# # Task 5: Critiquing
# critique_task = Task(
#     description=(
#         "Review the provided draft report. You also have the summarized findings (with sources) "
#         "for context. "
#         "Your review must: "
#         "1. Check for factual accuracy by cross-referencing the draft against the "
#         "   summarized findings. "
#         "2. Ensure all statements are properly supported by a reference. "
#         "3. Check for logical flow, clarity, and good structure. "
#         "4. Ensure the 'References' section is present and contains *only* a numbered list of raw URLs. "
#         "5. Provide a bullet-point list of actionable feedback for improvement. "
#         "If the report is excellent and needs no changes, just say 'The report is excellent and ready to publish.'"
#     ),
#     expected_output=(
#         "A bullet-point list of constructive criticism, feedback, and specific suggestions "
#         "for improving the draft report. Or, a single line of approval."
#     ),
#     agent=critic_agent,
#     context=[draft_task, summarize_task],
#     max_retries=2  # <-- ADDED FOR RESILIENCE
# )

# # Task 6: Final Revision
# final_report_task = Task(
#     description=(
#         "You will receive a **first draft** of a report and a list of **critiques** from a senior analyst. "
#         "Your job is to meticulously apply all the feedback from the critique to the draft. "
#         "This includes fixing any issues with references, flow, or factual accuracy. "
#         "Revise the document to create a final, polished, and publishable research report. "
#         "If the critique was 'The report is excellent and ready to publish,' then just output the original draft. "
#         "**IMPORTANT: Do NOT add a date, author name, or any other metadata. "
#         "The final report must start directly with the main title (e.g., '# Report Title...').**"
#     ),
#     expected_output=(
#         "The final, revised, and polished research report in Markdown format. "
#         "This version should incorporate all feedback from the critique."
#     ),
#     agent=writer_agent,
#     context=[draft_task, critique_task],
#     max_retries=2  # <-- ADDED FOR RESILIENCE
# )
from crewai import Task
from src.agents.planner_agent import planner_agent
from src.agents.search_agent import search_agent
from src.agents.summarizer_agent import summarizer_agent
from src.agents.writer_agent import writer_agent
# from src.agents.critic_agent import critic_agent (REMOVED to reduce API calls)

from pydantic import BaseModel, Field
from typing import List, Dict

# --- Pydantic Schema for the Plan ---
class SubQuestion(BaseModel):
    sub_question: str = Field(..., description="A specific, focused sub-question for research.")
    source_type: str = Field(..., description="Best source type, e.g., 'academic papers', 'recent news', 'blogs'.")
    keywords: List[str] = Field(..., description="A list of 1-2 precise search keywords.")

class ResearchPlan(BaseModel):
    research_plan: List[SubQuestion] = Field(..., description="A list of 3-4 sub-question objects.")

# --- Pydantic Schema for Search Output ---
class SourceItem(BaseModel):
    """A single item of retrieved content, with its source."""
    source: str = Field(..., description="The URL or ArXiv ID of the content.")
    content: str = Field(..., description="The scraped text or summary from that source.")

# --- Consolidated Data Schema ---
class ConsolidatedData(BaseModel):
    """A model to bundle the plan and search results together for the next step."""
    plan: ResearchPlan = Field(..., description="The original research plan.")
    sources: List[SourceItem] = Field(..., description="The list of retrieved sources and their content.")


# --- Task Definitions ---

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
    output_json=ResearchPlan,
    max_retries=2 # Add retry for API flakiness
)

# Task 2: Searching & Scraping (--- THIS TASK IS UPDATED ---)
search_task = Task(
    description=(
        "You will receive a 'ResearchPlan' object. You must store this plan. "
        "Then, for each sub-question in the 'plan.research_plan' list: "
        
        "1. **Formulate the query:** Take the `keywords` list. Join them with ' OR ' "
        "   to create a single query string. "
        
        "2. **Search:** Use the `google_search_tool` or `arxiv_search_tool` (based on `source_type`). "
        
        "3. **Process Results:** From the search results, identify the single most relevant "
        "   result. You will get its URL, and if it's from Google, a 'Snippet'. "
        
        "4. **Scrape:** Use the `scrape_website_tool`. "
        "   - If it's an ArXiv paper, use the paper's summary as the 'content' and its URL as the 'source'. "
        "   - If it's a Google result, you MUST call the tool with *both* arguments: "
        "     `scrape_website_tool(url=THE_URL, snippet=THE_SNIPPET)`. "
        "     The tool will try to scrape the URL, but if it fails (e.g., 403 Forbidden), "
        "     it will automatically return the snippet as the content. "
        
        "5. **Format:** Create a `SourceItem` object. Put the URL in the 'source' field "
        "   and the resulting text (either the full scrape or the snippet) in the 'content' field. "
        
        "6. Collect all these `SourceItem` objects into a list. "
        
        "7. **Bundle:** Finally, create a 'ConsolidatedData' object. Put the *original 'ResearchPlan' object* "
        "   you received into the 'plan' field, and put your new list of 'SourceItem' objects "
        "   into the 'sources' field."
    ),
    expected_output=(
        "A valid JSON object structured according to the 'ConsolidatedData' schema. "
        "This object contains *both* the original plan and the new search results."
    ),
    agent=search_agent,
    context=[plan_task],
    output_json=ConsolidatedData,
    max_retries=2 # Add retry for API flakiness
)

# Task 3: Summarization
summarize_task = Task(
    description=(
        "You will receive **one** 'ConsolidatedData' object. "
        "This object contains two attributes: 'plan' (the ResearchPlan) and 'sources' (the list of SourceItems). "
        "Your job is to generate a summary for *each* sub-question in the 'plan.research_plan' list. "
        
        "**You must follow this process exactly:**"
        "1. Access the research plan from the 'plan' attribute. "
        "2. Access the list of sources from the 'sources' attribute. This is your 'context_list'. "
        "3. For the *first* sub-question in the 'plan.research_plan' list: "
        "4. Call the `rag_query_tool` using that sub-question as the `question` "
        "   and the `context_list` (from the 'sources' attribute). "
        "5. The tool will return relevant snippets, *with their sources*. "
        "6. Read these snippets (or the 'No valid content' message) and write a concise "
        "   summary that answers the sub-question, making sure to include any "
        "   `[Source: ...]` tags you find. "
        "7. Repeat this process for *all* sub-questions in the 'plan.research_plan' list. "
        "8. Compile all the individual summaries (with their sources) into a "
        "   single, well-structured Markdown document, organized by the sub-questions."
    ),
    expected_output=(
        "A structured summary of the key findings, organized by research sub-question. "
        "This summary *must* be based on the snippets retrieved by the "
        "`rag_query_tool` and *must* include the `[Source: ...]` tags "
        "provided by the tool."
    ),
    agent=summarizer_agent,
    context=[search_task],
    max_retries=2 # Add retry for API flakiness
)


# Task 4: Drafting (Combined Final Task)
draft_task = Task(
    description=(
        "You will receive a structured summary of findings (which includes `[Source: ...]` tags). "
        "Your job is to synthesize this information into a **final, polished, professional research report.** "
        "The report must be in Markdown format. "
        
        "**Before writing, you must self-critique:** "
        "1. 'Does this summary fully answer the user's original topic?' "
        "2. 'Is the logical flow clear?' "
        "3. 'Are all claims supported by a source tag?' "
        
        "**Then, write the report including:** "
        "1. An Abstract (a brief overview of the topic and key findings). "
        "2. An Introduction (based on the original topic). "
        "3. Key Findings (based on the summarized text, organized by theme or sub-question). "
        "4. Challenges / Future Scope (if mentioned in the findings). "
        "5. A **References** section. You must parse all the `[Source: ...]` tags "
        "   from the summary. For each unique source, create a numbered list item "
        "   that contains **only the raw, full URL**. "
        "   **Example:** "
        "   ### References"
        "   1. https://arxiv.org/abs/2105.09492"
        "   2. https://www.forbes.com/article/..."
        "   **Do NOT add titles, authors, or any other bibliographic information. Just the links.**"

        "**IMPORTANT: Do NOT add a date, author name, or any other metadata. "
        "The report should start directly with the main title (e.Sg., '# Report Title...').**"
    ),
    expected_output=(
        "The final, polished research report in Markdown format. "
        "This single, comprehensive document should be ready for publication and "
        "include all sections, including a 'References' section with raw URLs."
    ),
    agent=writer_agent,
    context=[summarize_task],
    max_retries=2 # Add retry for API flakiness
)



# Task 5: Critiquing  <-- REMOVED
# Task 6: Final Revision <-- REMOVED



