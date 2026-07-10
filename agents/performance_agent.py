import os
import json
from groq import Groq
from services.schema_manager import get_raw_database_schema, get_logistics_formulas
from utils.prompts import BASE_AGENT_PROMPT

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_performance_analysis(user_prompt):
    raw_schema = get_raw_database_schema()
    raw_formulas = get_logistics_formulas()

    prompt = f"""
    {BASE_AGENT_PROMPT}
    You are the Coach Agent specializing in fleet driver performance behavior and safety ratings.
    
    USER REQUEST: {user_prompt}
    
    SOURCE OF TRUTH SCHEMA:
    \"\"\"
    {raw_schema}
    \"\"\"

    STRICT LOGISTICS FORMULAS & PATHING RULES:
    \"\"\"
    {raw_formulas}
    \"\"\"

    STRICT STRUCTURAL REQUIREMENTS:
    1. To prevent zero-result tables, follow the exact collection paths listed in the rules above.
    2. Never check for arrival times on the trips collection; always lookup 'delivery_events' as mandated.
    3. Every stage inside the generated "query" list MUST be a valid MongoDB aggregate operator block.

    Return ONLY a JSON block matching this EXACT structure (schema_mapping MUST come first):
    {{
        "schema_mapping": "Explain exactly which collection and fields you found in the SCHEMA text to fulfill this request.",
        "intent": "aggregate",
        "collection": "trips",
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