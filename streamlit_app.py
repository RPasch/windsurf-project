import os
import streamlit as st
from dotenv import load_dotenv
from tools import PerplexitySearchTool

# Try to import CrewAI
try:
    from crew import run_search_crew
    CREWAI_AVAILABLE = True
except (ImportError, TypeError) as e:
    CREWAI_AVAILABLE = False

load_dotenv()

# Page config
st.set_page_config(
    page_title="EDD Compliance Search",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Public Domain Search")
st.markdown("Search for information about people or companies using AI")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    mode = st.radio(
        "Search Mode:",
        ["crewai", "both", "perplexity"],
        format_func=lambda x: {
            "crewai": "🤖 CrewAI Only",
            "both": "📋 Both",
            "perplexity": "⚡ Perplexity Only"
        }[x],
        index=2  # Default to Perplexity
    )
    
    mode_descriptions = {
        'crewai': 'Uses AI agents for deep analysis (slower, more detailed)',
        'both': 'Runs both CrewAI and Perplexity for comprehensive results',
        'perplexity': 'Direct Perplexity search (faster, focused on EDD compliance)'
    }
    st.caption(mode_descriptions[mode])
    
    st.divider()
    
    st.subheader("🔑 API Key")
    perplexity_key = st.text_input(
        "Perplexity API Key",
        type="password",
        placeholder="pplx-...",
        help="Enter your Perplexity API key. Get one at https://www.perplexity.ai/settings/api"
    )
    
    if perplexity_key:
        st.success("✅ Using your API key")
    else:
        # Check if default key exists
        default_key = os.getenv('PERPLEXITY_API_KEY')
        if default_key:
            st.info("ℹ️ Using default API key")
        else:
            st.warning("⚠️ No API key provided")

# Main search interface
st.divider()

# Search input
query = st.text_input(
    "🔎 Search Query",
    placeholder="Enter a person's name, company, or topic...",
    help="Enter the entity or person you want to search for"
)

# Search button
if st.button("🚀 Search", type="primary", use_container_width=True):
    if not query:
        st.error("❌ Please enter a search query")
    elif not perplexity_key and not os.getenv('PERPLEXITY_API_KEY'):
        st.error("❌ Please enter a Perplexity API key")
    else:
        # Create tabs for results
        tab1, tab2 = st.tabs(["🤖 AI Analysis", "📊 EDD Compliance Report"])
        
        crewai_result = None
        perplexity_result = None
        
        # Handle CrewAI mode
        if mode in ['crewai', 'both']:
            with tab1:
                if not CREWAI_AVAILABLE:
                    st.warning("⚠️ CrewAI is not available. Requires Python 3.10+. Please use Perplexity Only mode.")
                else:
                    try:
                        with st.spinner("🤖 Running CrewAI analysis... This may take a few minutes."):
                            crewai_result = run_search_crew(
                                query, 
                                perplexity_api_key=perplexity_key if perplexity_key else None
                            )
                        st.markdown(crewai_result)
                    except Exception as e:
                        st.error(f"❌ CrewAI analysis failed: {str(e)}")
        
        # Handle Perplexity mode
        if mode in ['perplexity', 'both']:
            with tab2:
                try:
                    with st.spinner("⚡ Running Perplexity search..."):
                        if perplexity_key:
                            search_tool = PerplexitySearchTool(api_key=perplexity_key)
                        else:
                            search_tool = PerplexitySearchTool()
                        
                        perplexity_result = search_tool.search(query)
                    
                    if "error" in perplexity_result:
                        st.error(f"❌ Error: {perplexity_result['error']}")
                    elif "choices" in perplexity_result and len(perplexity_result["choices"]) > 0:
                        message = perplexity_result["choices"][0]["message"]
                        content = message["content"]
                        
                        # Display the content
                        st.markdown(content)
                        
                        # Display metadata in expander
                        with st.expander("ℹ️ Response Metadata"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Model", perplexity_result.get("model", "N/A"))
                            with col2:
                                tokens = perplexity_result.get("usage", {}).get("total_tokens", "N/A")
                                st.metric("Tokens Used", tokens)
                            
                            # Display citations if available
                            if "citations" in perplexity_result and perplexity_result["citations"]:
                                st.subheader("📚 Citations")
                                for idx, citation in enumerate(perplexity_result["citations"], 1):
                                    st.markdown(f"{idx}. [{citation}]({citation})")
                    else:
                        st.warning("⚠️ No results found")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Show message if mode not selected
        if mode == 'crewai' and not CREWAI_AVAILABLE:
            with tab2:
                st.info("ℹ️ Perplexity search not requested in this mode.")
        elif mode == 'perplexity':
            with tab1:
                st.info("ℹ️ CrewAI analysis not requested in this mode.")

# Footer
st.divider()
st.caption("Powered by CrewAI and Perplexity API")
