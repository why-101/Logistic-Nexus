import os
import json
from groq import Groq
from services.schema_manager import get_raw_database_schema, get_logistics_formulas
from utils.prompts import BASE_AGENT_PROMPT

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_maintenance_analysis(user_prompt):
    raw_schema = get_raw_database_schema()
    raw_formulas = get_logistics_formulas()

    prompt = f"""
    {BASE_AGENT_PROMPT}
    You are the Mechanic Agent specializing in truck active telemetry, utilization rates, maintenance logs, and breakdown risks.
    
    USER REQUEST: {user_prompt}
    
    CRITICAL DATABASE SCHEMA DEFINITION:
    \"\"\"
    {raw_schema}
    \"\"\"
    
    BUSINESS FORMULAS:
    \"\"\"
    {raw_formulas}
    \"\"\"

    # ... inside run_maintenance_analysis ...
    STRICT STRUCTURAL REQUIREMENTS:
    1. Every stage inside the generated "query" list MUST be a valid MongoDB aggregate operator block.
    2. Primary Collection: Default to 'truck_utilization_metrics' for active utilization or mileage threshold requests.
    3. Ensure filters live inside an explicit {{ "$match": {{ ... }} }} block.
    4. CASE INSENSITIVITY: Whenever filtering by a string status like "Active" or "Delivered", you MUST use a case-insensitive regex operator. Example: {{"status": {{"$regex": "^active$", "$options": "i"}}}}

    Return ONLY a JSON block matching this EXACT structure:
    {{
        "schema_mapping": "Explain exactly which collection and fields you found in the SCHEMA text to fulfill this request.",
        "intent": "aggregate",
        "collection": "truck_utilization_metrics",
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