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

# 🚀 Key Features

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

------------------------------------------------------------------------

## 🧠 System Workflow (4-Task Crew)

The default 4-task workflow is optimized for speed and to work within
free-tier API limits.

1.  **Plan:** The Planner Agent creates a detailed JSON research plan.
2.  **Search:** The Search Agent executes the plan, searches
    Google/ArXiv, and uses the `scrape_website_tool` to gather all the
    raw text and source URLs.
3.  **Summarize (RAG):** The Summarizer Agent builds a FAISS vector
    index from the raw text and uses it to find the best snippets to
    answer each sub-question.
4.  **Write:** The Writer Agent takes the RAG summaries (complete with
    sources) and synthesizes them into the final, polished Markdown
    report.

------------------------------------------------------------------------

## 🛠️ Tech Stack

  -----------------------------------------------------------------------
  Component                          Technology
  ---------------------------------- ------------------------------------
  Agent Framework                    CrewAI

  LLMs                               Google Gemini (via
                                     `langchain-google-genai`) & OpenAI
                                     GPT-4o-mini (via `langchain-openai`)

  RAG / Vector Store                 LangChain (FAISS-CPU +
                                     OpenAIEmbeddings)

  Web Scraping                       requests, BeautifulSoup4

  Web Search                         googlesearch-python, arxiv

  Frontend                           Streamlit

  Core Language                      Python 3.10+
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## ⚙️ Setup and Installation

### 1. Clone the Repository

``` bash
git clone https://github.com/vishwa573/auto-research.git
cd auto-research
```

### 2. Create and Activate a Virtual Environment

**On macOS/Linux:**

``` bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**

``` bash
python -m venv venv
.venv\Scripts\activate
```

### 3. Install Dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure Your API Keys

Find the `.env.example` file in the root directory (or create a new
`.env` file).

``` bash
# --- OpenAI ---
OPENAI_API_KEY="sk-..."

# --- Google Gemini ---
GEMINI_API_KEY="AIza..."

# --- Google Custom Search Engine ---
GOOGLE_API_KEY="AIza..."
GOOGLE_CSE_ID="..."
```

------------------------------------------------------------------------

## ▶️ How to Run the Application

Once your environment is ready and `.env` file is configured:

``` bash
streamlit run app/app.py
```

This will open the app in your browser at **http://localhost:8501** ---
enter your research topic and press **Start Research!**

------------------------------------------------------------------------

## ✨ Upgrade to 6-Agent Critic Crew

By default, the system uses 4 tasks. You can upgrade to a 6-agent
workflow for enhanced quality control.


### Step 1: Modify `src/crew/main_crew.py`

Comment out the 4-task lines and enable the 6-task crew version (as
shown in the project docs).

### Step 2: Modify `src/crew/tasks.py`

Uncomment the commentted lines(first half of the file, uses critic agent ) and comment the second half (which does not use critic agent)

------------------------------------------------------------------------

## 🔮 Future Improvements

-   **Persistent Vector Store:** Use ChromaDB or Pinecone for long-term
    memory.
-   **Advanced Scraping:** Add Playwright or Selenium for
    JavaScript-heavy sites.
-   **Human-in-the-Loop:** Let users approve research plans in Streamlit
    before proceeding.

------------------------------------------------------------------------

**Author:** [Vishwa Sundar](https://github.com/vishwa573) 
