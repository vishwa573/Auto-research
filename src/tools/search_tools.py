import os
import arxiv
from langchain_core.tools import tool
from googleapiclient.discovery import build

"""
IMPORTANT: For these tools to work, you must set up API keys
in a .env file in the root of your project:

/.env
    GOOGLE_API_KEY="your_google_api_key"
    GOOGLE_CSE_ID="your_google_cse_id"

You can get a Google API Key from the Google Cloud Console:
https://console.cloud.google.com/apis/credentials

You can get a Google CSE ID (Custom Search Engine ID) from:
https://cse.google.com/cse/all
(Set it up to search the entire web)
"""

@tool
def google_search(query: str) -> str:
    """
    Searches Google for recent articles, blogs, and news on a given query.
    Returns a list of formatted search results.
    """
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        cse_id = os.environ.get("GOOGLE_CSE_ID")

        if not api_key or not cse_id:
            return "Error: GOOGLE_API_KEY or GOOGLE_CSE_ID not set in .env file."

        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cse_id, num=5).execute() # Get top 5 results

        if 'items' not in res:
            return f"No results found for: {query}"

        formatted_results = []
        for item in res.get('items', []):
            formatted_results.append(
                f"Title: {item['title']}\n"
                f"Snippet: {item['snippet']}\n"
                f"URL: {item['link']}\n"
                "-----------------"
            )
        return "\n".join(formatted_results)

    except Exception as e:
        return f"Error during Google Search: {e}"

@tool
def arxiv_search(query: str) -> str:
    """
    Searches ArXiv for academic papers on a given query.
    Returns a list of formatted search results from ArXiv.
    """
    try:
        # Use the arxiv library to search
        search = arxiv.Search(
            query=query,
            max_results=3, # Get top 3 relevant papers
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        client = arxiv.Client()
        results = list(client.results(search))

        if not results:
            return f"No ArXiv papers found for: {query}"

        formatted_results = []
        for result in results:
            formatted_results.append(
                f"Paper Title: {result.title}\n"
                f"Authors: {', '.join(str(author) for author in result.authors)}\n"
                f"Published: {result.published.date()}\n"
                f"Summary: {result.summary[:500]}...\n" # Truncate summary
                f"URL: {result.entry_id}\n"
                "-----------------"
            )
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Error during ArXiv Search: {e}"
