from crewai import Crew, Process
from src.agents.planner_agent import planner_agent
from src.agents.search_agent import search_agent
from src.agents.summarizer_agent import summarizer_agent
from src.agents.writer_agent import writer_agent
from src.agents.critic_agent import critic_agent  # <-- IMPORT NEW AGENT

from src.crew.tasks import (
    plan_task, 
    search_task, 
    summarize_task, 
    draft_task,         # <-- RENAMED
    critique_task,      # <-- NEW
    final_report_task   # <-- NEW
)

def run_crew(topic: str) -> str:
    """
    Initializes and runs the multi-agent research crew.
    """
    
    # Define the agents
    agents = [
        planner_agent,
        search_agent,
        summarizer_agent,
        writer_agent,
        critic_agent  # <-- ADD NEW AGENT TO LIST
    ]
    
    # Define the tasks
    tasks = [
        plan_task,
        search_task,
        summarize_task,
        draft_task,         # <-- DRAFT TASK
        critique_task,      # <-- CRITIQUE TASK
        final_report_task   # <-- FINAL REPORT TASK
    ]
    
    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=2,  # Provides detailed logs
        process=Process.sequential
    )
    
    # Kick off the crew's work
    # The 'topic' will be injected into the 'plan_task'
    result = crew.kickoff(inputs={"topic": topic})
    
    # The result will be the output of the final_report_task
    return result

if __name__ == "__main__":
    # This allows you to test the crew directly from the command line
    # (Optional, as we are using Streamlit)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    topic = "What are the latest advancements in LLM reasoning?"
    print(f"Running crew for topic: {topic}")
    
    report = run_crew(topic)
    
    print("\n--- FINAL REPORT ---")
    print(report)

