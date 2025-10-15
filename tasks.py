from crewai import Task, Agent


def create_research_task(agent: Agent, query: str) -> Task:
    """Create a research task for gathering information"""
    return Task(
        description=f"""Conduct a thorough search about: {query}.
        
        Your task is to:
        1. Find relevant information from public domain sources
        2. Focus on key details, history, and recent developments
        3. Verify the accuracy of the information
        4. Identify the most important and relevant facts
        
        Be comprehensive but concise in your findings.""",
        expected_output="""A detailed report containing:
        - Overview of the subject
        - Key facts and details
        - Historical context (if relevant)
        - Recent developments or news
        - Sources of information""",
        agent=agent
    )


def create_analysis_task(agent: Agent, query: str) -> Task:
    """Create an analysis task for processing information"""
    return Task(
        description=f"""Analyze the information collected about: {query}.
        
        Your task is to:
        1. Review all the information gathered by the researcher
        2. Identify key points, trends, and patterns
        3. Assess the significance and implications
        4. Present the information in a clear, organized manner
        5. Highlight any notable findings or concerns
        
        Provide a well-structured analysis that is easy to understand.""",
        expected_output="""A comprehensive analysis report containing:
        - Executive summary
        - Key findings and insights
        - Notable trends or patterns
        - Potential implications
        - Conclusion with main takeaways""",
        agent=agent
    )
