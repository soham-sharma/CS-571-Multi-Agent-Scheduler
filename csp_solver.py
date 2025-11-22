from constraint import Problem, AllDifferentConstraint
from data_model import load_data
from datetime import datetime, timedelta

# --- Helper Function for Time Conflicts ---

def get_interval(time_slot_id, time_slot_details, day):
    """Calculates the start and end datetime for a specific time slot on a specific day."""
    details = time_slot_details[time_slot_id]
    start_time_str = details['start_time']
    duration = details['duration_min']
    
    # Use a dummy date (1970-01-01) for comparison, as we only care about time of day
    start_dt = datetime.strptime(start_time_str, "%H:%M")
    end_dt = start_dt + timedelta(minutes=duration)
    
    return start_dt, end_dt

def timeslots_overlap(ts_id_1, ts_id_2, time_slot_details):
    """
    Checks if two time slots conflict on any shared day.
    
    Returns True if conflict exists (constraint violated), False otherwise.
    """
    details_1 = time_slot_details[ts_id_1]
    details_2 = time_slot_details[ts_id_2]
    
    # Find common days (e.g., if both are MWF, the conflict is possible)
    common_days = set(details_1['days']) & set(details_2['days'])
    
    if not common_days:
        return False

    # Since all instances of a given time slot (e.g., MWF_1030_50) have 
    # the same start time and duration, we only need to check one common day.
    
    start_1, end_1 = get_interval(ts_id_1, time_slot_details, common_days.pop())
    start_2, end_2 = get_interval(ts_id_2, time_slot_details, common_days.pop())
    
    # Time overlap check: start1 < end2 AND start2 < end1
    return (start_1 < end_2) and (start_2 < end_1)
    
def find_initial_assignment(data):
    # Unpack necessary data
    courses = data["course_ids"]
    domain = data["full_domain"]
    professors = data["professors"]
    enrollments = data["enrollments"]
    room_capacities = data["room_capacities"]
    time_slot_details = data["time_slot_details"]
    
    problem = Problem()
    problem.addVariables(courses, domain)

    # --- 2. Hard Constraints ---
    
    # A. Unique Room-Time (now needs overlap check)
    def check_room_collision(assignment_1, assignment_2, course_a, course_b):
        ts_id_a, room_a = assignment_1
        ts_id_b, room_b = assignment_2
        
        # Only check collision if they are in the same room
        if room_a != room_b:
            return True # Different rooms, no collision
        
        # If they are in the same room, check if their time slots overlap on any day
        if timeslots_overlap(ts_id_a, ts_id_b, time_slot_details):
            return False # Overlap in same room = Conflict
            
        return True # Same room, but no time overlap = OK

    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            course_a, course_b = courses[i], courses[j]
            # Must pass time_slot_details as a required closure variable
            problem.addConstraint(
                lambda a1, a2, ca=course_a, cb=course_b: check_room_collision(a1, a2, ca, cb), 
                (course_a, course_b)
            )


    # B. Instructor Conflict
    def check_instructor_conflict(assignment_1, assignment_2):
        ts_id_1 = assignment_1[0]
        ts_id_2 = assignment_2[0]
        
        # If the time slots overlap on any day, the instructor is double-booked
        if timeslots_overlap(ts_id_1, ts_id_2, time_slot_details):
            return False
            
        return True # No overlap = OK

    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            course_a, course_b = courses[i], courses[j]
            
            if professors[course_a] == professors[course_b]:
                problem.addConstraint(check_instructor_conflict, (course_a, course_b))

    # C. Room Capacity Constraint        
    for course_name in courses:
        required_capacity = enrollments[course_name]
        
        problem.addConstraint(
            lambda assignment, limit=required_capacity: room_capacities[assignment[1]] >= limit,
            (course_name,)
        )

    # 3. Solve and Return
    print("Solving for Initial Assignment A0 using CSP...")
    solution = problem.getSolution() 

    return solution

if __name__ == '__main__':
    data = load_data()
    if data:
        schedule = find_initial_assignment(data)
        if schedule:
            print("\nTest Solution Found:", schedule)
        else:
            print("\nTest Failed: No solution found.")