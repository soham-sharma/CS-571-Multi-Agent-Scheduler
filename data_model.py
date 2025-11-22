# data_model.py

import json
# Import datetime tools for conflict checking later
from datetime import datetime, timedelta 

def load_data(filepath='input_data.json'):
    # ... (File loading remains the same)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found at {filepath}")
        return None

    # Retrieve and process raw data
    time_slots_list = data.get("time_slots", []) # List of dictionaries
    rooms = data.get("rooms", {}) 
    courses_raw = data.get("courses", {}) 

    # --- NEW: Create a dictionary mapping time slot ID to its details ---
    time_slots = {ts['id']: ts for ts in time_slots_list}
    
    # Create simplified lists and mappings for the CSP solver
    course_ids = list(courses_raw.keys())
    
    professors = {cid: details["professor"] for cid, details in courses_raw.items()}
    enrollments = {cid: details["enrollment"] for cid, details in courses_raw.items()}
    
    # Generate the full domain D = T_ID x R
    full_domain = []
    for ts_id in time_slots.keys():
        for r in rooms.keys():
            full_domain.append((ts_id, r)) # Assignment is now (Time_ID, Room_ID)
            
    return {
        "course_ids": course_ids,
        "full_domain": full_domain,
        "professors": professors,
        "enrollments": enrollments,
        "room_capacities": rooms,
        "time_slot_details": time_slots # Store the details for constraint checks
    }

if __name__ == '__main__':
    # Test data loading
    data = load_data()
    if data:
        print("Data loaded successfully. Domain size:", len(data['full_domain']))