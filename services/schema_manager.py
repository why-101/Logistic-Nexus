import json
from utils.db_client import db

VALID_COLLECTIONS = [
    "drivers", "trucks", "trailers", "customers", "facilities", "routes", 
    "loads", "trips", "fuel_purchases", "maintenance_records", 
    "delivery_events", "safety_incidents", "driver_monthly_metrics", 
    "truck_utilization_metrics"
]

import os

def get_raw_database_schema():
    """Reads the absolute source of truth schema file directly from disk 
    to provide dynamic grounding context to all downstream agents.Collection name is always in small letters"""
    
    schema_path = os.path.join(os.getcwd(), "DATABASE_SCHEMA.txt")
    
    # Fallback to look one level up if executing inside the app/ folder
    if not os.path.exists(schema_path):
        schema_path = os.path.join(os.path.dirname(os.getcwd()), "DATABASE_SCHEMA.txt")
        
    try:
        with open(schema_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error reading schema configuration: {str(e)}"

def get_logistics_formulas():
    """Reads the business formulas file from disk."""
    formulas_path = os.path.join(os.getcwd(), "LOGISTICS_FORMULAS.txt")
    
    if not os.path.exists(formulas_path):
        formulas_path = os.path.join(os.path.dirname(os.getcwd()), "LOGISTICS_FORMULAS.txt")
        
    try:
        with open(formulas_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error reading formulas: {str(e)}"


