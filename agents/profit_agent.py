import os
import json
from groq import Groq
from services.schema_manager import get_raw_database_schema, get_logistics_formulas
from utils.prompts import BASE_AGENT_PROMPT

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_profit_analysis(user_prompt):
    raw_schema = get_raw_database_schema()
    raw_formulas = get_logistics_formulas()

    prompt = f"""
    {BASE_AGENT_PROMPT}
    You are the Accountant Agent specializing in financial metrics, gross revenue, fuel overhead, and profit margins.
    
    USER REQUEST: {user_prompt}
    
    SOURCE OF TRUTH SCHEMA:
    \"\"\"
    {raw_schema}
    \"\"\"

    LOGISTICS FORMULAS:
    \"\"\"
    {raw_formulas}
    \"\"\"

    STRICT OPERATOR REQUIREMENT:
    To implement the 4/30 maintenance proration calculation without triggering a JSON validation crash, use this exact syntax layout:
    {{"$multiply": ["$maintenance_records.total_cost", {{"$divide": [6, 30]}}]}}

    Return ONLY a JSON block matching this EXACT structure (schema_mapping MUST come first):
    {{
        "schema_mapping": "Explain exactly which collection and fields you found in the SCHEMA text to fulfill this request.",
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