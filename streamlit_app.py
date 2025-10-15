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
    
    st.subheader("🔑 API Keys")
    
    # OpenAI API Key (for CrewAI)
    openai_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Required for CrewAI analysis. Get one at https://platform.openai.com/api-keys"
    )
    
    # Perplexity API Key
    perplexity_key = st.text_input(
        "Perplexity API Key",
        type="password",
        placeholder="pplx-...",
        help="Enter your Perplexity API key. Get one at https://www.perplexity.ai/settings/api"
    )
    
    # Status indicators
    if openai_key:
        st.success("✅ OpenAI key provided")
    else:
        default_openai = os.getenv('OPENAI_API_KEY')
        if default_openai:
            st.info("ℹ️ Using default OpenAI key")
        elif mode in ['crewai', 'both']:
            st.warning("⚠️ OpenAI key required for CrewAI")
    
    if perplexity_key:
        st.success("✅ Perplexity key provided")
    else:
        default_perplexity = os.getenv('PERPLEXITY_API_KEY')
        if default_perplexity:
            st.info("ℹ️ Using default Perplexity key")
        elif mode in ['perplexity', 'both']:
            st.warning("⚠️ Perplexity key required")

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
    elif mode in ['crewai', 'both'] and not openai_key and not os.getenv('OPENAI_API_KEY'):
        st.error("❌ Please enter an OpenAI API key for CrewAI analysis")
    elif mode in ['perplexity', 'both'] and not perplexity_key and not os.getenv('PERPLEXITY_API_KEY'):
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
                            # Set OpenAI API key temporarily if provided
                            if openai_key:
                                os.environ['OPENAI_API_KEY'] = openai_key
                            
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
                        
                        # Process citations to make bracketed numbers clickable
                        if "citations" in perplexity_result and perplexity_result["citations"]:
                            citations = perplexity_result["citations"]
                            # Replace [1], [2], etc. with clickable links
                            import re
                            for idx, url in enumerate(citations, 1):
                                # Match [number] pattern
                                pattern = rf'\[{idx}\]'
                                replacement = f'[[{idx}]]({url})'
                                content = re.sub(pattern, replacement, content)
                        
                        # Display the content with clickable citations
                        st.markdown(content, unsafe_allow_html=True)
                        
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
