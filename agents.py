from crewai import Agent
from tools import create_perplexity_search_tool, create_perplexity_custom_tool

def create_researcher_agent(perplexity_api_key: str = None) -> Agent:
    """Create a researcher agent for gathering information
    
    Args:
        perplexity_api_key: Optional custom Perplexity API key
    """
    # Create tool with custom API key
    search_tool = create_perplexity_search_tool(api_key=perplexity_api_key)
    
    return Agent(
        role='Senior Research Analyst',
        goal='Find and analyze information about the given query from public domain sources and present raw data',
        backstory="""You are an expert researcher with years of experience in 
        finding and analyzing information from various sources. You excel at 
        identifying key facts, verifying information, and presenting findings 
        in a clear and organized manner.""",
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
    )


def create_analyst_agent(perplexity_api_key: str = None) -> Agent:
    """Create an analyst agent for processing and analyzing information
    
    Args:
        perplexity_api_key: Optional custom Perplexity API key
    """
    # Create custom tool with custom API key
    custom_tool = create_perplexity_custom_tool(api_key=perplexity_api_key)
    
    return Agent(
        role='Compliance Intelligence Analyst',
        goal='Analyse compliance reports for a new entity and summarise it for onboarding agents in markdown format',
        backstory="""You are an experienced analyst who can read publicly available information and summarise it for onboarding agents.
        You are exceptional at highlighting curcial information and seeing the riks in customers. You know when to raise red flags and when to be cautious.
        You are experienced at research and know when to research further or when you have enough information to drae a conclusion. Your opinion matters a lot.""",
        verbose=True,
        allow_delegation=False,
        tools=[custom_tool],
    )
