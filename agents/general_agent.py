import os
import json
from groq import Groq
from services.schema_manager import get_raw_database_schema

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_general_query(user_prompt):
    raw_schema = get_raw_database_schema()

    gen_prompt = f"""
    You are a Logistics Generalist. Your job is to handle metadata, basic collection exploration, and system queries.
    
    USER REQUEST: {user_prompt}
    
    CRITICAL DATABASE SCHEMA DEFINITION:
    \"\"\"
    {raw_schema}
    \"\"\"

    STRICT PIPELINE CONSTRUCTION RULES:
    1. Every item inside the "query" array MUST be a valid MongoDB aggregation stage operator.
    2. ANTI-HALLUCINATION: You MUST map the user's request to the EXACT collections and fields listed in the schema text above. Do not invent collections like 'shipments' or 'destinations'.
    
    Return ONLY JSON matching this EXACT structure (schema_mapping MUST come first): 
    {{
        "schema_mapping": "Explain exactly which collection and fields you found in the SCHEMA text to fulfill this request.",
        "intent": "aggregate",
        "collection": "VALID_SCHEMA_COLLECTION_NAME",
        "query": [],
        "explanation": "..."
    }}
    """
    res = client.chat.completions.create(
        messages=[{"role": "system", "content": gen_prompt}],
        model="openai/gpt-oss-120b",
        response_format={"type": "json_object"}
    )
    return json.loads(res.choices[0].message.content)