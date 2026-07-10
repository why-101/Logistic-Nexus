import os
import json
from groq import Groq
from services.schema_manager import get_raw_database_schema
from utils.prompts import BASE_AGENT_PROMPT

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_rework_agent(failed_query="", error_message="", user_suggestion=""):
    """Takes optional inputs and rewrites the pipeline to fix errors."""
    raw_schema = get_raw_database_schema()

    prompt = f"""
    {BASE_AGENT_PROMPT}
    You are the Senior Debug Agent. The previous pipeline execution failed or needs modification.
    
    SOURCE OF TRUTH SCHEMA:
    \"\"\"
    {raw_schema}
    \"\"\"

    INPUTS FOR REWORK (Treat as optional context):
    - FAILED PIPELINE: {failed_query if failed_query else "None provided."}
    - DATABASE ERROR: {error_message if error_message else "No explicit database error. Just needs adjustment."}
    - USER SUGGESTION: {user_suggestion if user_suggestion else "None provided. Analyze the error and fix the pipeline autonomously."}

    INSTRUCTIONS:
    Analyze why the pipeline failed based on the error or suggestion. 
    Rewrite the pipeline. Ensure you follow all strict MongoDB and JSON rules (e.g., $subtract takes 2 arguments, use $cond for division, use regex for strings).
    
    Return ONLY a JSON block matching this EXACT structure (schema_mapping MUST come first):
    {{
        "schema_mapping": "Explain what was wrong and how you fixed it.",
        "intent": "aggregate",
        "collection": "VALID_SCHEMA_COLLECTION_NAME",
        "query": [],
        "explanation": "..."
    }}
    """
    res = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model="openai/gpt-oss-120b",
        response_format={"type": "json_object"}
    )
    return json.loads(res.choices[0].message.content)