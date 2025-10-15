import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from tools import PerplexitySearchTool

# Try to import CrewAI - will fail on Python 3.9
try:
    from crew import run_search_crew
    CREWAI_AVAILABLE = True
except (ImportError, TypeError) as e:
    print(f"CrewAI not available: {e}")
    print("CrewAI requires Python 3.10+. Direct Perplexity mode will still work.")
    CREWAI_AVAILABLE = False
    run_search_crew = None

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the search tool
search_tool = PerplexitySearchTool()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').strip()
    mode = request.form.get('mode', 'crewai')  # crewai, both, or perplexity
    perplexity_key = request.form.get('perplexity_key', '').strip()  # Optional custom API key
    
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
    
    try:
        print(f"Searching for: {query}")
        print(f"Mode: {mode}")
        
        crewai_result = None
        perplexity_result = None
        
        # Handle different modes
        if mode in ['crewai', 'both']:
            # Run CrewAI
            if not CREWAI_AVAILABLE:
                crewai_result = "⚠️ CrewAI is not available. Requires Python 3.10+. Please use Perplexity Only mode or upgrade Python."
            else:
                try:
                    print("Running CrewAI analysis...")
                    # Pass custom API key if provided
                    crewai_result = run_search_crew(query, perplexity_api_key=perplexity_key if perplexity_key else None)
                    print(f"CrewAI result: {crewai_result}")
                except Exception as crew_error:
                    print(f"CrewAI error: {str(crew_error)}")
                    crewai_result = f"CrewAI analysis failed: {str(crew_error)}"
        
        if mode in ['perplexity', 'both']:
            # Run Perplexity search with optional custom API key
            if perplexity_key:
                print(f"Using custom Perplexity API key")
                # Create a temporary search tool with custom API key
                from tools import PerplexitySearchTool
                custom_search_tool = PerplexitySearchTool(api_key=perplexity_key)
                perplexity_result = custom_search_tool.search(query)
            else:
                perplexity_result = search_tool.search(query)
            print(f"Perplexity result: {perplexity_result}")
            
            # Check for errors
            if "error" in perplexity_result:
                print(f"Error in perplexity result: {perplexity_result['error']}")
                if mode == 'perplexity':  # Only return error if perplexity-only mode
                    return jsonify({"error": perplexity_result["error"]}), 500
        
        # Set default messages if not run
        if crewai_result is None:
            crewai_result = "CrewAI analysis not requested in this mode."
        if perplexity_result is None:
            perplexity_result = {"message": "Perplexity search not requested in this mode."}
        
        response_data = {
            "crewai_result": crewai_result,
            "perplexity_result": perplexity_result,
            "mode": mode
        }
        print(f"Sending response with mode: {mode}")
        return jsonify(response_data)
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)
