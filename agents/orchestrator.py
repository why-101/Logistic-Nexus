import os
import json
from groq import Groq
from utils.db_client import db
from utils.prompts import ORCHESTRATOR_SYSTEM_PROMPT

# Import specialists and generalist
from agents.profit_agent import run_profit_analysis
from agents.maintenance_agent import run_maintenance_analysis
from agents.performance_agent import run_performance_analysis
from agents.general_agent import run_general_query

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def handle_request(user_prompt):
    """Determines the target specialist based on the user's prompt."""
    res = client.chat.completions.create(
        messages=[{"role": "system", "content": ORCHESTRATOR_SYSTEM_PROMPT},
                  {"role": "user", "content": user_prompt}],
        model="openai/gpt-oss-120b",
        response_format={"type": "json_object"}
    )
    target = json.loads(res.choices[0].message.content).get("target_agent", "GENERAL")
    
    if target == "PROFIT": return run_profit_analysis(user_prompt), "Accountant Agent"
    if target == "MAINTENANCE": return run_maintenance_analysis(user_prompt), "Mechanic Agent"
    if target == "PERFORMANCE": return run_performance_analysis(user_prompt), "Coach Agent"
    return run_general_query(user_prompt), "Logistics Generalist"

def execute_final_query(intent, collection, query):
    try:
        # Check if collection exists and has data first
        if db[collection].count_documents({}) == 0:
            return {"error": f"The collection '{collection}' is empty. Please check your data import."}

        if intent == "aggregate" or isinstance(query, list):
            pipeline = query if isinstance(query, list) else [query]
            
            # Inject safety limit
            if not any("$limit" in str(s) for s in pipeline):
                pipeline.insert(0, {"$limit": 100})
            
            results = list(db[collection].aggregate(pipeline, maxTimeMS=30000))
            
            # 💡 THE FIX: A professional, generic empty-state message
            if not results:
                return {"error": "Query executed successfully, but returned 0 records. The filter conditions may be too strict, or the joined data fields do not match."}
            return results
        
        if isinstance(query, dict):
            results = list(db[collection].find(query).limit(100))
            if not results:
                return {"error": "No records found matching this exact filter."}
            return results
            
        return {"error": "Format Mismatch: Query payload was structurally expected to behave as a dictionary."}
    except Exception as e:
        err = str(e)
        if "MaxTimeMSExpired" in err:
            return {"error": "Database Timeout: The query took too long. Check your Atlas Indexes."}
        return {"error": err}