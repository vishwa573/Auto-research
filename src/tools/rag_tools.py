from crewai_tools import tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@tool("rag_query_tool")
def rag_query_tool(question: str, context_list: list[dict]) -> str:
    """
    Performs in-memory RAG on a list of source dictionaries.
    This tool is metadata-aware. It attaches the 'source' URL to
    each text chunk *before* indexing, ensuring that retrieved
    snippets can be properly attributed.
    
    Args:
        question (str): The specific query or sub-question to find information for.
        context_list (list[dict]): A list of source objects, where each object
                                   is a dictionary with 'source' (URL) and
                                   'content' (scraped text).
                                   
    Returns:
        str: A string of the most relevant text snippets, each followed
             by its [Source: ...] tag.
    """
    log.info(f"RAG Tool: Received query: '{question}'")
    log.info(f"RAG Tool: Processing {len(context_list)} source documents.")

    # 1. Initialize Embeddings Model
    try:#USe any 1 embeddings model
        # embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        from langchain_openai import OpenAIEmbeddings

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    except Exception as e:
        log.error(f"RAG Tool: Failed to load embeddings model. Error: {e}")
        return "Error: Could not load embeddings model."

    # 2. Create lists of texts and their corresponding metadatas
    texts = []
    metadatas = []
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    
    for item in context_list:
        # *** FIX 1: Make key-checking flexible (as you suggested) ***
        # Check for multiple variations of the keys
        content = item.get('content') or item.get('Content')
        source = item.get('source') or item.get('Source') or item.get('URL')
        
        # *** FIX 2: Make content validation more lenient (as you suggested) ***
        # Only skip if content is truly missing or too short to be useful
        if not content or len(content.strip()) < 50:
            log.warning(f"RAG Tool: Skipping item with missing/short content or source: {item}")
            continue
            
        # Split the content into chunks
        chunks = text_splitter.split_text(content)
        
        # Add the chunks to the texts list
        texts.extend(chunks)
        
        # Create a metadata dictionary for each chunk, pointing to its source
        metadatas.extend([{"source": source}] * len(chunks))

    # 3. Build the FAISS index with metadata
    if not texts:
        log.warning("RAG Tool: No valid text chunks found to index after filtering.")
        return "No valid content was found to search for this sub-question."
        
    try:
        log.info(f"RAG Tool: Creating FAISS index with {len(texts)} text chunks...")
        vectordb = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
        log.info("RAG Tool: FAISS index created successfully.")
    except Exception as e:
        log.error(f"RAG Tool: Failed to create FAISS index. Error: {e}")
        return "Error: Failed to build RAG index."

    # 4. Perform similarity search
    log.info(f"RAG Tool: Performing similarity search for: '{question}'")
    results = vectordb.similarity_search(question, k=4) # Get top 4 relevant chunks

    # 5. Format the results with their sources (the final fix)
    snippets = []
    seen_sources = set()
    
    for r in results:
        # Get the source from the metadata we preserved
        src = r.metadata.get("source", "Unknown Source")
        
        # Format the snippet
        snippet_text = f"{r.page_content.strip()} [Source: {src}]"
        
        # Simple de-duplication
        if snippet_text not in snippets:
            snippets.append(snippet_text)
            seen_sources.add(src)

    if not snippets:
        log.warning(f"RAG Tool: No relevant snippets found for query: '{question}'")
        return "No relevant information found for this sub-question."

    log.info(f"RAG Tool: Returning {len(snippets)} snippets from {len(seen_sources)} sources.")
    return "\n---\n".join(snippets)

