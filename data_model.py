# data_model.py
import json
from pathlib import Path

def load_data(input_filepath, pref_filepath="preferences.json"):
    """
    Loads:
      - Course/room/time-slot data from input_filepath
      - Professor & student preferences from preferences.json (if present)

    Returns one unified data dictionary used by CSP + negotiation layer.
    """
    # ---- Load the main input file ----
    try:
        with open(input_filepath, "r") as f:
            raw = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_filepath}")
        return None

    # Main components
    time_slots_list = raw.get("time_slots", [])
    rooms = raw.get("rooms", {})
    courses_raw = raw.get("courses", {})

    # Convert time_slots list → dict
    time_slot_details = {ts["id"]: ts for ts in time_slots_list}

    # Extract course-level data
    course_ids = list(courses_raw.keys())
    professors = {cid: info["professor"] for cid, info in courses_raw.items()}
    enrollments = {cid: info["enrollment"] for cid, info in courses_raw.items()}

    # Build domain (all valid (ts, room) pairs)
    full_domain = []
    for ts_id in time_slot_details.keys():
        for room_id in rooms.keys():
            full_domain.append((ts_id, room_id))

    # ---- Try to load preferences.json ----
    preferences = None
    pref_file = Path(pref_filepath)
    if pref_file.exists():
        with open(pref_file, "r") as f:
            preferences = json.load(f)
    else:
        print(f"Warning: preferences file not found at {pref_filepath}. Continuing without preferences.")
        preferences = {}

    professor_preferences = preferences.get("professor_preferences", {})
    student_enrollments = preferences.get("student_enrollments", {})
    student_preferences = preferences.get("student_preferences", {})

    # ---- Compute professor priorities (for negotiation order) ----
    professor_priorities = {}
    for cid, prof in professors.items():
        professor_priorities.setdefault(prof, 0)
        professor_priorities[prof] += enrollments[cid]

    # ---- Final unified data dictionary ----
    return {
        # Existing Stage 1 data
        "course_ids": course_ids,
        "full_domain": full_domain,
        "professors": professors,
        "enrollments": enrollments,
        "room_capacities": rooms,
        "time_slot_details": time_slot_details,

        # Added for Stage 2
        "professor_preferences": professor_preferences,
        "student_enrollments": student_enrollments,
        "student_preferences": student_preferences,
        "professor_priorities": professor_priorities,
    }


if __name__ == "__main__":
    # Simple smoke test
    d = load_data("input_synthetic.json")
    print("Loaded data keys:", list(d.keys()))
