import os
from crewai import Crew, Process
from dotenv import load_dotenv

# Load .env file to get API keys
load_dotenv()

# Import all agents and tasks
from src.agents.planner_agent import planner_agent
from src.agents.search_agent import search_agent
from src.agents.summarizer_agent import summarizer_agent
from src.agents.writer_agent import writer_agent

from src.crew.tasks import (
    plan_task,
    search_task,
    summarize_task,
    write_task
)

def run_crew(topic: str):
    """
    Initializes and runs the AutoResearch crew for a given topic.
    Returns the final report.
    """
    print(f"Starting AutoResearch crew for topic: {topic}")
    
    # Check for necessary API keys
    if not os.environ.get("GEMINI_API_KEY"):
        raise EnvironmentError("GEMINI_API_KEY not found in .env file.")
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY not found in .env file.")
    if not os.environ.get("GOOGLE_CSE_ID"):
        raise EnvironmentError("GOOGLE_CSE_ID not found in .env file.")

    # Assemble the agents and tasks into a crew
    research_crew = Crew(
        agents=[
            planner_agent,
            search_agent,
            summarizer_agent,
            writer_agent
        ],
        tasks=[
            plan_task,
            search_task,
            summarize_task,
            write_task
        ],
        process=Process.sequential, # Tasks will be executed one after another
        verbose=2 # Shows agent actions and tool usage in the console
    )

    # Kick off the crew's work!
    # The '{topic}' variable in the task descriptions will be
    # automatically populated with the value from this input.
    result = research_crew.kickoff(inputs={'topic': topic})
    
    print("AutoResearch crew finished.")
    return result

if __name__ == "__main__":
    # This allows you to run the crew directly from the command line
    # for testing.
    
    # --- !! IMPORTANT !! ---
    # Make sure you have created a .env file in the root directory
    # with your API keys:
    #
    # GEMINI_API_KEY="your_gemini_key"
    # GOOGLE_API_KEY="your_google_api_key"
    # GOOGLE_CSE_ID="your_google_cse_id"
    # -----------------------

    try:
        # Example topic to research
        research_topic = "latest advancements in quantum computing for finance"
        final_report = run_crew(research_topic)
        
        print("\n\n--- FINAL REPORT ---")
        print(final_report)
        print("\nReport also saved to 'autoresearch_report.md'")

    except EnvironmentError as e:
        print(f"Error: {e}")
        print("Please make sure your .env file is set up correctly.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
