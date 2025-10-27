# 🧭 AutoResearch — AI-Powered Multi-Agent Research Assistant

**AutoResearch** is an autonomous multi-agent system built with **Python** and **CrewAI** that takes a **high-level research topic** and generates a **comprehensive, structured, and fully cited research report** — automatically.

---

### 🧠 Overview
AutoResearch showcases a **sophisticated agentic workflow** designed to emulate the complete research process — from planning and information retrieval to synthesis and report generation.

It integrates:
- **Dynamic Planning** to decompose complex topics  
- **Real-Time Web Research** for up-to-date sources  
- **Robust Web Scraping** for content extraction  
- **In-Memory RAG (Retrieval-Augmented Generation)** for factual accuracy and relevance  

Together, these components produce **high-quality, evidence-based research reports** with minimal human intervention.

---

## 🚀 Key Features

### 🧠 **Autonomous Multi-Agent Crew**
A coordinated team of specialized AI agents — **Planner**, **Searcher**, **Summarizer**, and **Writer** — working collaboratively to produce a complete, high-quality research report.

---

### 🗂️ **Dynamic Research Planning**
The **Planner Agent** decomposes complex topics into a well-structured **JSON-based research plan**, including sub-questions, relevant keywords, and suggested source types.

---

### 🌐 **Real-Time Data Retrieval**
The **Search Agent** leverages both the **Google Search API** and **ArXiv API** to gather the most **relevant and up-to-date information** available on the web.

---

### 🕸️ **Robust Web Scraping**
Equipped with a resilient `scrape_website_tool`, the system attempts to extract full webpage content.  
If scraping fails (e.g., due to a `403 Forbidden` error), it **intelligently falls back** to using the search snippet — ensuring **uninterrupted execution** and **error-free operation**.

---

### 🧩 **In-Memory RAG (Retrieval-Augmented Generation)**
The **Summarizer Agent** performs **text chunking** and builds an **in-memory FAISS vector store**, enabling fast, context-aware retrieval and accurate citation of sources when answering each sub-question.

---

### 🔄 **Resilient Multi-LLM Strategy**
Multiple LLM providers — **Google Gemini** and **OpenAI GPT-4o-mini** — are seamlessly integrated to **distribute workload**, **enhance reliability**, and **avoid free-tier rate limits**.

---

### 💻 **Interactive Frontend**
A user-friendly **Streamlit interface** allows anyone to simply **enter a research topic** and receive a **structured, well-cited final report**, all within a few clicks.

---

## ⚙️ System Workflow (4-Task Crew)

The default **4-task workflow** is optimized for speed and efficiency within free-tier API limits:

1. **Plan:** The Planner Agent creates a detailed JSON research plan.  
2. **Search:** The Search Agent executes the plan, searches Google/ArXiv, and uses the `scrape_website_tool` to gather all the raw text and source URLs.  
3. **Summarize (RAG):** The Summarizer Agent builds a FAISS vector index from the raw text and finds the best snippets to answer each sub-question.  
4. **Write:** The Writer Agent synthesizes the summaries (with sources) into the final, polished Markdown report.  

---

## 🛠️ Tech Stack

| Component | Technology |
|------------|-------------|
| **Agent Framework** | CrewAI |
| **LLMs** | Google Gemini (via `langchain-google-genai`), OpenAI GPT-4o-mini (via `langchain-openai`) |
| **RAG / Vector Store** | LangChain with FAISS-CPU + OpenAIEmbeddings |
| **Web Scraping** | `requests`, `BeautifulSoup4` |
| **Web Search** | `googlesearch-python`, `arxiv` |
| **Frontend** | Streamlit |
| **Core Language** | Python 3.10+ |

---

## ⚙️ Setup and Installation

Follow these steps to get the project running on your local machine.

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/vishwa573/Auto-research.git
cd Auto-research
```

### 2️⃣ Create and Activate a Virtual Environment
**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```
**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Your API Keys
This is the most important step. The project will not run without these keys.

Find the `.env.example` file in the root directory (or create a new `.env` file) and add your keys as follows:

```bash
# --- OpenAI ---
OPENAI_API_KEY="sk-..."

# --- Google Gemini ---
GEMINI_API_KEY="AIza..."

# --- Google Custom Search Engine ---
GOOGLE_API_KEY="AIza..."
GOOGLE_CSE_ID="..."
```

---

## ▶️ How to Run the Application

Once your environment is set up and your keys are in the `.env` file, start the Streamlit app:

```bash
streamlit run app/app.py
```

The app will open automatically in your browser at [http://localhost:8501](http://localhost:8501).  
Enter a research topic and click **Start Research** to generate your report!

---

## ✨ Upgrade: 6-Agent "Critic" Workflow

By default, AutoResearch uses a **4-task crew** for efficiency.  
If you have paid API plans and want **higher-quality, critiqued reports**, enable the **Critic Agent** workflow.

### 🔁 6-Agent 'Draft → Review → Revise' Workflow

| Step | Description |
|------|--------------|
| **1. Plan** | Planner Agent creates a detailed JSON-based research plan. |
| **2. Search** | Search Agent executes the plan, retrieves text, and sources. |
| **3. Summarize (RAG)** | Summarizer Agent uses RAG to extract relevant, citable snippets. |
| **4. Draft** | Writer Agent synthesizes the summaries into a first draft. |
| **5. Critique** | Critic Agent reviews for factual accuracy, logic, and citation quality. |
| **6. Revise** | Writer Agent applies feedback to produce the polished final report. |

---

### 🧩 Step 1: Create or Confirm the Critic Agent File

```python
# src/agents/critic_agent.py
from crewai import Agent
from src.llm_config import heavy_llm

critic_agent = Agent(
    role="Senior Quality Assurance Analyst",
    goal=(
        "To meticulously review a research report for factual accuracy, logical consistency, "
        "clarity, and adherence to all instructions. You must ensure all claims are "
        "backed by sources and that the 'References' section is formatted correctly."
    ),
    backstory=(
        "You are a notoriously strict and detail-oriented analyst from a top-tier "
        "consulting firm. Your job is to find every flaw, no matter how small. "
        "You ensure that no document leaves the company unless it is absolutely perfect. "
        "You have a keen eye for unsupported claims and logical fallacies."
    ),
    llm=heavy_llm,
    verbose=True,
    allow_delegation=False
)
```

---

### 🧩 Step 2: Edit `src/crew/main_crew.py`

Uncomment the 6-agent configuration and comment out the 4-agent setup.

```python
# src/crew/main_crew.py
...
# from src.crew.tasks import plan_task, search_task, summarize_task, draft_task  # <-- COMMENT THIS LINE
from src.crew.tasks import (  # <-- UNCOMMENT THESE LINES
    plan_task, 
    search_task, 
    summarize_task, 
    draft_task, 
    critique_task, 
    final_report_task
)
...
# from src.agents.planner_agent import planner_agent # <-- COMMENT THIS LINE
# from src.agents.search_agent import search_agent
# from src.agents.summarizer_agent import summarizer_agent
# from src.agents.writer_agent import writer_agent

from src.agents.planner_agent import planner_agent # <-- UNCOMMENT THESE LINES
from src.agents.search_agent import search_agent
from src.agents.summarizer_agent import summarizer_agent
from src.agents.writer_agent import writer_agent
from src.agents.critic_agent import critic_agent # <-- ADD THIS AGENT
...
        return Crew(
            # agents=[planner_agent, search_agent, summarizer_agent, writer_agent], # <-- COMMENT THIS LINE
            # tasks=[plan_task, search_task, summarize_task, draft_task], # <-- COMMENT THIS LINE
            
            agents=[planner_agent, search_agent, summarizer_agent, writer_agent, critic_agent], # <-- UNCOMMENT THIS
            tasks=[plan_task, search_task, summarize_task, draft_task, critique_task, final_report_task], # <-- UNCOMMENT THIS
            process=Process.sequential,
            verbose=2,
            memory=False
        )
```

---

### 🧩 Step 3: Edit `src/crew/tasks.py`
Comment out the 4-task setup and uncomment the 6-task setup.
```python
# src/crew/tasks.py
from crewai import Task
from src.agents.planner_agent import planner_agent
from src.agents.search_agent import search_agent
from src.agents.summarizer_agent import summarizer_agent
from src.agents.writer_agent import writer_agent
from src.agents.critic_agent import critic_agent # <-- UNCOMMENT THIS LINE
...
# --- Task Definitions ---
...
# (Keep plan_task, search_task, and summarize_task as they are)
...
# Task 4: Drafting (Combined Final Task)
draft_task = Task(
    description=(
        "You will receive a structured summary of findings (which includes `[Source: ...]` tags). "
        "Your job is to synthesize this information into a **first draft** of a professional research report. " # <-- CHANGE 'final, polished' to 'first draft'
        # ... (rest of the description is fine, but you can remove the self-critique part)
    ),
    expected_output=(
        "A comprehensive **first draft** of the research report in Markdown format..." # <-- CHANGE to 'first draft'
    ),
    agent=writer_agent,
    context=[summarize_task],
    max_retries=2 
)

# --- UNCOMMENT THE FOLLOWING TASKS ---

# Task 5: Critiquing
critique_task = Task(
    description=(
        "Review the provided draft report. You also have the summarized findings (with sources) "
        "for context. "
        "Your review must: "
        "1. Check for factual accuracy by cross-referencing the draft against the "
        "   summarized findings. "
        "2. Ensure all statements are properly supported by a reference. "
        "3. Check for logical flow, clarity, and good structure. "
        "4. Ensure the 'References' section is present and contains *only* a numbered list of raw URLs. "
        "5. Provide a bullet-point list of actionable feedback for improvement. "
        "If the report is excellent and needs no changes, just say 'The report is excellent and ready to publish.'"
    ),
    expected_output=(
        "A bullet-point list of constructive criticism, feedback, and specific suggestions "
        "for improving the draft report. Or, a single line of approval."
    ),
    agent=critic_agent,
    context=[draft_task, summarize_task],
    max_retries=2
)

# Task 6: Final Revision
final_report_task = Task(
    description=(
        "You will receive a **first draft** of a report and a list of **critiques** from a senior analyst. "
        "Your job is to meticulously apply all the feedback from the critique to the draft. "
        "This includes fixing any issues with references, flow, or factual accuracy. "
        "Revise the document to create a final, polished, and publishable research report. "
        "If the critique was 'The report is excellent and ready to publish,' then just output the original draft. "
        "**IMPORTANT: Do NOT add a date, author name, or any other metadata. "
        "The final report must start directly with the main title (e.g., '# Report Title...').**"
    ),
    expected_output=(
        "The final, revised, and polished research report in Markdown format. "
        "This version should incorporate all feedback from the critique."
    ),
    agent=writer_agent,
    context=[draft_task, critique_task],
    max_retries=2
)
```

---

## 🔮 Future Improvements

- **Persistent Vector Store:** Integrate ChromaDB or Pinecone for long-term agent memory.  
- **Advanced Scraping:** Use Playwright or Selenium for JavaScript-heavy sites.  
- **Human-in-the-Loop:** Pause execution after planning and allow manual approval in the Streamlit UI.  
