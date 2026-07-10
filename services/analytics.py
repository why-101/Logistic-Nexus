def get_profit_margin_template():
    """
    Trip-Level Profit Logic with Prorated Maintenance.
    Logic: (Revenue) - (Fuel + (Monthly Maintenance * 4/30)).
    """
    return [
        { "$limit": 100 },
        {
            "$lookup": {
                "from": "trips",
                "localField": "load_id",
                "foreignField": "load_id",
                "as": "trip_info"
            }
        },
        { "$unwind": "$trip_info" },
        {
            "$lookup": {
                "from": "fuel_purchases",
                "localField": "trip_info.trip_id",
                "foreignField": "trip_id",
                "as": "fuel"
            }
        },
        {
            "$lookup": {
                "from": "maintenance_records",
                "localField": "trip_info.truck_id",
                "foreignField": "truck_id",
                "as": "maint"
            }
        },
        {
            "$project": {
                "route_id": 1,
                "trip_id": "$trip_info.trip_id",
                "revenue": 1,
                "fuel_cost": { "$sum": "$fuel.total_cost" },
                # Apply 4/30 fraction to monthly maintenance[cite: 5]
                "prorated_maint": { 
                    "$multiply": [{ "$sum": "$maint.total_cost" }, { "$divide": [4, 30] }] 
                }
            }
        },
        {
            "$project": {
                "route_id": 1,
                "trip_id": 1,
                "revenue": 1,
                "total_expenses": { "$add": ["$fuel_cost", "$prorated_maint"] },
                "profit": { 
                    "$subtract": ["$revenue", { "$add": ["$fuel_cost", "$prorated_maint"] }] 
                },
                "margin": {
                    "$cond": [
                        { "$eq": ["$revenue", 0] }, 0,
                        { "$divide": [{ "$subtract": ["$revenue", { "$add": ["$fuel_cost", "$prorated_maint"] }] }, "$revenue"] }
                    ]
                }
            }
        },
        { "$sort": { "profit": -1 } }
    ]

def get_driver_safety_template():
    """Returns logic for calculating incidents per driver[cite: 5]."""
    return [
        { "$limit": 100 },
        {
            "$lookup": {
                "from": "safety_incidents",
                "localField": "driver_id",
                "foreignField": "driver_id",
                "as": "incidents"
            }
        },
        {
            "$project": {
                "driver_id": 1,
                "incident_count": {"$size": "$incidents"}
            }
        }
    ]

def get_driver_safety_template():
    """Returns logic for calculating incidents per driver[cite: 5]."""
    return [
        { "$limit": 100 },
        {
            "$lookup": {
                "from": "safety_incidents",
                "localField": "driver_id",
                "foreignField": "driver_id",
                "as": "incidents"
            }
        },
        {
            "$project": {
                "driver_id": 1,
                "incident_count": {"$size": "$incidents"}
            }
        }
    ]