from crewai import Crew
from agents import create_researcher_agent, create_analyst_agent
from tools import PerplexitySearchTool
from tasks import create_research_task, create_analysis_task


def create_search_crew(query: str, perplexity_api_key: str = None) -> Crew:
    """
    Create and configure a crew for public domain search and analysis
    
    Args:
        query: The search query (person or company name)
        perplexity_api_key: Optional custom Perplexity API key
        
    Returns:
        Configured Crew instance ready to execute
    """
    # Create agents
    researcher = create_researcher_agent()
    analyst = create_analyst_agent()
    search_tool = PerplexitySearchTool(api_key=perplexity_api_key)

    # Create tasks
    research_task = create_research_task(researcher, query)
    analysis_task = create_analysis_task(analyst, query)
    
    # Create and configure the crew
    crew = Crew(
        agents=[researcher, analyst],
        tasks=[research_task, analysis_task],
        verbose=2
    )
    
    return crew


def run_search_crew(query: str, perplexity_api_key: str = None) -> str:
    """
    Execute the search crew and return results
    
    Args:
        query: The search query (person or company name)
        perplexity_api_key: Optional custom Perplexity API key
        
    Returns:
        String containing the crew's analysis results
    """
    crew = create_search_crew(query, perplexity_api_key)
    result = crew.kickoff()
    return result
