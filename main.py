import json
import argparse
from data_model import load_data
from csp_solver import find_initial_assignment

OUTPUT_FILE = 'initial_schedule_A0.json'

def print_grid_view(schedule, data):
    rooms = list(data['room_capacities'].keys())
    time_slots = list(data['time_slot_details'].keys())

    # Normalize schedule values (list or tuple) to (time_slot, room)
    normalized = {}
    for course, val in schedule.items():
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            ts, room = val[0], val[1]
        else:
            continue
        normalized.setdefault(room, []).append((ts, course))

    print("\n--- Room View ---")
    for r in rooms:
        print(f"\n{r}:")
        entries = normalized.get(r, [])
        # Sort by time-slot id
        for ts, course in sorted(entries):
            print(f"  {ts} -> {course}")

def main():
    """
    Data loading, CSP solving, and output saving.
    """
    parser = argparse.ArgumentParser(description="Run MACSS Initial Solver")
    parser.add_argument(
        'input_file', 
        nargs='?', 
        default='input_synthetic.json', 
        help="Path to the input JSON file (default: input_synthetic.json)"
    )
    args = parser.parse_args()
    print("--- Multi-Agent Classroom Scheduling System (MACSS) ---")
    print(f"Reading from: {args.input_file}")
    
    # 1. Load Data (from input_data.json)
    data = load_data(args.input_file)
    if data is None:
        return
    
    # 2. Find Initial Feasible Assignment (A0)
    initial_schedule = find_initial_assignment(data)
    
    # 3. Save Output for Agent Negotiation
    if initial_schedule:
        print("\nStatus: Feasible Initial Assignment (A0) Found.")
        
        # Display the schedule
        print("\n--- Initial Schedule (A0) ---")
        for course, (time, room) in initial_schedule.items():
            enrollment = data["enrollments"][course]
            capacity = data["room_capacities"][room]
            print(f"{course:<9}: {time:<15} in {room:<10} (Enroll: {enrollment}, Room Cap: {capacity})")
        
        print_grid_view(initial_schedule, data)
            
        # Save the result
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(initial_schedule, f, indent=4)
            
        print(f"\nSchedule saved successfully to {OUTPUT_FILE} for agent negotiation.")
        
    else:
        print("\nStatus: Could not find a feasible schedule satisfying all hard constraints.")


if __name__ == "__main__":
    main()