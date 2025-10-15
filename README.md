# Public Domain Search with CrewAI and Perplexity

A Python web application that uses CrewAI and Perplexity API to search and analyze public domain information about people and companies.

## Features

- Web-based interface for searching public domain information
- Uses CrewAI for intelligent analysis of search results
- Integrates with Perplexity API for comprehensive web searches
- Clean, responsive UI built with Tailwind CSS

## Docs
https://wiobank.atlassian.net/wiki/spaces/AFS/pages/2361294864/AI+for+Enhanced+Due+Diligence+EDD
https://wiobank.atlassian.net/wiki/spaces/AFS/pages/2348515447/Automation+of+EDD+Public+Domain+Checks+with+AI+Perplexity

## Prerequisites

- Python 3.8+
- Perplexity API key (get one from [Perplexity AI](https://www.perplexity.ai/))

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd public-domain-search
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your Perplexity API key to the `.env` file

## Running the Application

1. Start the Flask development server:
   ```bash
   flask run
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## How It Works

1. Enter a person's name, company, or topic in the search box
2. The application will:
   - Use Perplexity API to search the web for relevant information
   - Use CrewAI to analyze and process the search results
   - Display both the raw search results and AI analysis

## Project Structure

```
├── app.py                  # Main Flask application and API endpoints
├── agents.py               # CrewAI agent definitions
├── tasks.py                # CrewAI task definitions
├── tools.py                # Perplexity search tool implementation
├── crew.py                 # Crew orchestration and execution
├── templates/
│   └── index.html         # Frontend interface
├── .env                    # Environment configuration
└── requirements.txt        # Python dependencies
```

### Module Descriptions

- **app.py**: Flask web server with routes for the frontend and search API
- **agents.py**: Defines the AI agents (Researcher and Analyst) used by CrewAI
- **tasks.py**: Defines the tasks that agents will perform (Research and Analysis)
- **tools.py**: Implements the Perplexity API search tool
- **crew.py**: Orchestrates agents and tasks into a cohesive workflow

## License

This project is open source and available under the [MIT License](LICENSE).
