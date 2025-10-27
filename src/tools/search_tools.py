import os
from chromadb import logger
import requests
from crewai_tools import tool
from bs4 import BeautifulSoup
import json
import logging
import arxiv

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# --- ArXiv Search Tool ---
@tool("arxiv_search_tool")
def arxiv_search_tool(query: str) -> str:
    """
    Searches ArXiv for academic papers and returns snippets.
    
    Args:
        query (str): The search query string.
        
    Returns:
        str: A formatted string of search results, or a "No results" message.
    """
    log.info(f"ArXiv Tool: Searching for '{query}'")
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=3, # Get top 3 results
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = list(client.results(search))
        
        if not results:
            log.warning(f"ArXiv Tool: No results found for '{query}'")
            return f"No academic papers found on ArXiv for the query: '{query}'."

        snippets = []
        for r in results:
            snippets.append(
                f"Title: {r.title}\n"
                f"Published: {r.published.date()}\n"
                f"Summary: {r.summary}\n"
                f"URL: {r.entry_id}"
            )
            
        log.info(f"ArXiv Tool: Found {len(snippets)} results.")
        return "\n---\n".join(snippets)
        
    except Exception as e:
        log.error(f"ArXiv Tool: Error during search: {e}")
        return f"Error occurred while searching ArXiv: {e}"

# --- Google Search Tool ---
@tool("google_search_tool")
def google_search_tool(query: str) -> str:
    """
    Searches Google and returns snippets and URLs.
    
    Args:
        query (str): The search query string.
        
    Returns:
        str: A formatted string of search results, or a "No results" message.
    """
    log.info(f"Google Search Tool: Searching for '{query}'")
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        url = "https://www.googleapis.com/customsearch/v1"
        params = {'key': api_key, 'cx': cse_id, 'q': query, 'num': 3}
        
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise error for bad responses
        results = response.json().get('items', [])

        if not results:
            log.warning(f"Google Search Tool: No results found for '{query}'")
            return f"No web results found on Google for the query: '{query}'."

        snippets = []
        for r in results:
            snippets.append(
                f"Title: {r['title']}\n"
                f"Snippet: {r['snippet']}\n"
                f"URL: {r['link']}"
            )
            
        log.info(f"Google Search Tool: Found {len(snippets)} results.")
        return "\n---\n".join(snippets)

    except Exception as e:
        log.error(f"Google Search Tool: Error during search: {e}")
        return f"Error occurred while searching Google: {e}"
# # --- Website Scraping Tool (FIXED) ---
# # (The old, single-argument version has been removed)
# @tool("scrape_website_tool")
# def scrape_website_tool(url: str, snippet: str) -> str:
#     """
#     Scrapes the text content of a given URL.
#     If the scrape fails (e.g., due to 403 Forbidden),
#     it will return the provided 'snippet' as a fallback.
#     """
#     try:
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status() # Will raise an error for 4xx/5xx responses
        
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Remove script and style elements
#         for script_or_style in soup(["script", "style"]):
#             script_or_style.decompose()
            
#         # Get text and clean it up
#         text = soup.get_text()
#         lines = (line.strip() for line in text.splitlines())
#         chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#         text = '\n'.join(chunk for chunk in chunks if chunk)
        
#         if not text or len(text.strip()) < len(snippet):
#             # If text is empty or less useful than the snippet, return snippet
#             return f"Scrape was minimal. Using snippet: {snippet}"
            
#         # Truncate to a reasonable size to avoid token limits
#         max_length = 8000
#         return text[:max_length] + "..." if len(text) > max_length else text

#     except Exception as e:
#         # --- THIS IS THE FIX ---
#         # If any error occurs (403, timeout, etc.), return the snippet.
#         logger.warning(f"Scrape Tool: Error scraping '{url}': {e}. Returning snippet.")
#         return f"Scrape failed. Using snippet: {snippet}"

# --- Web Scrape Tool (UPDATED) ---
@tool("scrape_website_tool")
def scrape_website_tool(url: str) -> str:
    """
    Scrapes the text content of a single webpage.
    
    Args:
        url (str): The URL of the website to scrape.
        
    Returns:
        str: The extracted text content, or an error message.
    """
    # *** THIS IS THE 503 FIX ***
    # Limit the content to a reasonable size to avoid overloading the embedding model
    MAX_CHARS_TO_SCRAPE = 15000 

    log.info(f"Scrape Tool: Scraping URL: '{url}'")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        text = soup.get_text()
        
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if not text:
            log.warning(f"Scrape Tool: No text content found at '{url}'")
            return f"Error: No text content could be extracted from {url}."
            
        if len(text) > MAX_CHARS_TO_SCRAPE:
            log.warning(f"Scrape Tool: Truncating scraped content from {len(text)} to {MAX_CHARS_TO_SCRAPE} chars.")
            text = text[:MAX_CHARS_TO_SCRAPE]
        
        log.info(f"Scrape Tool: Successfully scraped {len(text)} characters.")
        return text
        
    except requests.exceptions.RequestException as e:
        log.error(f"Scrape Tool: Error scraping '{url}': {e}")
        return f"Error: Failed to retrieve or scrape the URL {url}. Reason: {e}"
    except Exception as e:
        log.error(f"Scrape Tool: Unknown error scraping '{url}': {e}")
        return f"Error: An unknown error occurred while scraping {url}. Reason: {e}"

search_tools = [google_search_tool, arxiv_search_tool, scrape_website_tool]