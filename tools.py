import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv
from langchain.tools import Tool, StructuredTool
from pydantic.v1 import BaseModel, Field



load_dotenv()


class PerplexitySearchTool:
    """Tool for searching the web using Perplexity API"""
    
    def __init__(self, api_key: str = None):
        """Initialize with optional API key. If not provided, uses environment variable."""
        self.perplexity_api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
    def search(self, query: str, location :str = "AE") -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        # Build the EDD compliance prompt
        prompt = f"""You are acting as a compliance analyst performing Enhanced Due Diligence (EDD) public domain checks in line with CBUAE requirements.

                        For the following entities/persons: {query}

                        When providing the results, clearly label each entry with its category (Company, UBO, Authorized Person, Subsidiary/Partner, Counterparty). If the name does not fall under one of these, assign it to "Other (related category)" and specify what that category is.

                        If the inserted input is a company name, start by giving at least two short lines about the company — what it is, what it does, and where it is located. Keep this brief (no more than 2 lines) before moving on to the adverse media and public domain checks.

                        If the inserted input is a person's name, skip the company introduction and continue directly with the public domain checks as already instructed. 
                        
                        Perform a deep public domain search (Google, news sources, regulatory filings, sanctions lists, legal proceedings, reliable media) and identify any red flags across these categories:

                        - Sanctions & Restricted Countries – associations with Iran, Syria, Cuba, North Korea, Crimea, DPRK, Sevastopol, or international sanctions.
                        - Terrorism Financing – links to terrorist organizations, funding, or support.
                        - Financial Conduct & Regulatory Issues – fines, enforcement actions, market misconduct, insider trading.
                        - Money Laundering – laundering schemes, shell companies, suspicious transactions.
                        - Bribery & Corruption – bribery, kickbacks, embezzlement, misuse of power.
                        - Adverse Media & Negative News – fraud, scams, bankruptcy, trafficking, smuggling, forgery, counterfeit, cybercrime, evasion.
                        - Other Red Flags – reputational risks, banned industries, criminal cases.

                        Output Format (for each entity/person):

                        Name: [Entity/Person]

                        Findings Table:
                        | Risk Category | Findings (Yes/No) | Details | Source/Link |

                        Summary: Concise risk assessment (is this entity/person clear, or do they present compliance concerns?).

                        Reference Links: Direct URLs to key sources.

                        Make the results structured, clear, and ready to paste into Passfort. For each entity/person, explicitly state whether adverse media or other negative findings exist. If none are found, clearly write "No adverse results found" under that individual's section.
                        """
        
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }],
            "enable_search_classifier": True,
            "web_search_options": {
                "search_context_size": "medium",
                "user_location": {
                    "country": location
                }
            }
        }
        
        try:
            print(f"Payload: {payload}")
            response = requests.post(self.base_url, headers=headers, json=payload)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"{e}"
            try:
                error_detail = response.json()
                error_msg = f"{e} - Details: {error_detail}"
            except:
                pass
            return {"error": error_msg}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def _run(self, query: str) -> str:
        """Run method for CrewAI tool compatibility"""
        result = self.search(query)
        if "error" in result:
            return f"Error: {result['error']}"
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        
        return "No results found"


# Helper function for the tool
def _perplexity_search(tool_input: str) -> str:
    """Internal function to perform Perplexity search
    
    Args:
        tool_input: The query string (entity or person name)
    """
    search_tool = PerplexitySearchTool()
    result = search_tool.search(tool_input)
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    if "choices" in result and len(result["choices"]) > 0:
        return result["choices"][0]["message"]["content"]
    
    return "No results found"


# Create a CrewAI-compatible tool using LangChain's Tool class
perplexity_search_tool = Tool(
    name="Perplexity Search",
    func=_perplexity_search,
    description="Search the web using Perplexity API for Enhanced Due Diligence (EDD) compliance checks. Input should be an entity or person name to search for. Returns a comprehensive EDD compliance report with risk assessment."
)







# Custom tool input schema
class PerplexityCustomToolInput(BaseModel):
    """Input schema for custom Perplexity search tool"""
    region: str = Field(default='AE', description="The region of the individual or business")
    compliance_category: str = Field(description="Specific compliance category")
    individual_business_name: str = Field(description="The name of the individual or business")
    perplexity_search_prompt: str = Field(description="The prompt to use for the Perplexity search")


# Custom tool function
def _perplexity_custom_search(
    region: str,
    compliance_category: str,
    individual_business_name: str,
    perplexity_search_prompt: str
) -> str:
    """Execute custom Perplexity search for targeted compliance research"""
    perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
    base_url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {perplexity_api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""You are acting as a compliance analyst performing Enhanced Due Diligence (EDD) public domain checks in line with CBUAE requirements within the {compliance_category} category.

                    For the following entities/persons: {individual_business_name}
                    {perplexity_search_prompt}

                    Perform a deep public domain search (Google, news sources, regulatory filings, sanctions lists, legal proceedings, reliable media) and identify any red flags for the given category.

                    Summary: in depth risk assessment (is this entity/person clear, or do they present compliance concerns?).

                    Reference Links: Direct URLs to key sources.

                    Make the results structured, clear. For each entity/person, explicitly state whether adverse media or other negative findings exist. If none are found, clearly write "No adverse results found".
                    """
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "enable_search_classifier": True,
        "web_search_options": {
            "search_context_size": "high",
            "user_location": {
                "country": region
            }
        }
    }
    
    try:
        response = requests.post(base_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        
        return "No results found"
    except requests.exceptions.RequestException as e:
        return f"Error performing search: {str(e)}"


# Create the custom tool using StructuredTool
perplexity_custom_tool = StructuredTool.from_function(
    func=_perplexity_custom_search,
    name="Custom Search Tool",
    description="If not enough info is already collected or if doubts exist, this tool can be used to do more research on a specific topic using perplexity search. Provide region, compliance category, entity/person name, and custom search prompt.",
    args_schema=PerplexityCustomToolInput
)


