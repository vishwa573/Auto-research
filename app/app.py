import streamlit as st
import sys
import os

# We need to add the project root to the Python path
# so Streamlit can find our 'src' module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # Now we can import our crew function
    from src.crew.main_crew import run_crew
except ImportError as e:
    st.error(f"Error importing modules: {e}. "
             "Please ensure you are in the correct directory and all dependencies are installed.")
    st.stop()

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="AutoResearch AI",
    page_icon="🤖",
    layout="wide"
)

# --- App Header ---
st.title("🤖 AutoResearch – AI-Powered Multi-Agent System")
st.markdown("""
Welcome to AutoResearch! This system uses a team of AI agents to autonomously research a topic 
and generate a structured report.
""")

# --- Sidebar for API Keys (Optional but good practice) ---
with st.sidebar:
    st.header("Configuration")
    st.markdown("""
    This app uses API keys stored in your `.env` file at the root of the project.
    
    Ensure your `.env` file contains:
    - `GEMINI_API_KEY`
    - `GOOGLE_API_KEY`
    - `GOOGLE_CSE_ID`
    """)
    if ".env" not in os.listdir(project_root):
        st.warning(".env file not found!")
    else:
        st.success(".env file found.")

# --- Main Interface ---
st.header("1. Enter Your Research Topic")
topic = st.text_input(
    "e.g., 'latest advancements in quantum computing for finance'",
    label_visibility="collapsed"
)

# State to hold the report
if 'report' not in st.session_state:
    st.session_state.report = None

if st.button("Start Research", type="primary", use_container_width=True):
    if topic:
        st.session_state.report = None # Clear previous report
        st.header("2. Research in Progress...")
        
        # This container will show the agent's progress
        status_container = st.empty()
        
        try:
            # We can't easily capture the verbose log from crewAI in real-time here,
            # so we'll just show a spinner. The console will still show the verbose logs.
            with st.spinner("The AI agent crew is working... This may take a few minutes."):
                status_container.info("Initializing Crew... \n\n"
                                    "Step 1: Planner Agent is creating the research plan...")
                
                # --- This is the call to our backend ---
                final_report = run_crew(topic)
                # ----------------------------------------
                
                st.session_state.report = final_report
                status_container.empty() # Clear the status message
                st.balloons()

        except EnvironmentError as e:
            st.error(f"Configuration Error: {e}. Please check your .env file.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please enter a research topic.")

# --- Display the Final Report ---
if st.session_state.report:
    st.header("3. Final Research Report")
    st.markdown(st.session_state.report)
    
    st.download_button(
        label="Download Report as Markdown",
        data=st.session_state.report,
        file_name=f"autoresearch_report_{topic.replace(' ', '_')[:20]}.md",
        mime="text/markdown",
    )
