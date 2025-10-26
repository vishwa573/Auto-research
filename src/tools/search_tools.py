import os
import json
import requests
from bs4 import BeautifulSoup
from crewai_tools import tool
from googleapiclient.discovery import build
from langchain.tools import Tool
import arxiv

# --- Google Search Tool ---
@tool("google_search_tool")
def google_search_tool(query: str) -> str:
    """
    Searches Google for the given query and returns the top 5 results
    with snippets and source titles.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    service = build("customsearch", "v1", developerKey=api_key)
    try:
        res = (
            service.cse()
            .list(
                q=query,
                cx=cse_id,
                num=5,
            )
            .execute()
        )
        snippets = []
        if "items" in res:
            for item in res["items"]:
                snippets.append({
                    "title": item["title"],
                    "link": item["link"],
                    "snippet": item["snippet"]
                })
        return json.dumps(snippets, indent=2)
    except Exception as e:
        return f"Error during Google search: {e}"

# --- ArXiv Search Tool ---
@tool("arxiv_search_tool")
def arxiv_search_tool(query: str) -> str:
    """
    Searches ArXiv for the given query and returns the top 3 results
    with summaries.
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=3,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for r in search.results():
            results.append({
                "title": r.title,
                "summary": r.summary,
                "url": r.entry_id
            })
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error during ArXiv search: {e}"

# --- NEW: Web Scraping Tool ---
@tool("scrape_website_tool")
def scrape_website_tool(url: str) -> str:
    """
    Fetches the content of a given URL and returns the clean,
    unstructured text content.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Error: Failed to fetch URL with status code {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text from common content tags
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li', 'span'])
        text = ' '.join(elem.get_text(strip=True) for elem in text_elements)

        # Basic cleaning
        text = ' '.join(text.split()) # Remove extra whitespace
        
        if not text:
            return "Error: No meaningful text could be extracted from the page."

        return text[:8000] # Return first 8000 chars to avoid token limits

    except requests.exceptions.RequestException as e:
        return f"Error fetching or parsing URL: {e}"
    except Exception as e:
        return f"An unexpected error occurred during scraping: {e}"

# --- Export Tools ---
search_tools = [
    google_search_tool,
    arxiv_search_tool,
    scrape_website_tool  # Add the new tool to the list
]

