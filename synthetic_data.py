import json
import random

#CONFIGURATION:
NUM_COURSES = 40   
NUM_PROFESSORS = 12
NUM_ROOMS = 8 
OUTPUT_FILE = "input_synthetic.json"

def generate():
    # 1. Define Fixed Resources (Purdue Rooms & Times)
    time_slots = [
        {"id": "MWF_0730", "days": ["M","W","F"], "start_time": "07:30", "duration_min": 50},
        {"id": "MWF_0830", "days": ["M","W","F"], "start_time": "08:30", "duration_min": 50},
        {"id": "MWF_0930", "days": ["M","W","F"], "start_time": "09:30", "duration_min": 50},
        {"id": "MWF_1030", "days": ["M","W","F"], "start_time": "10:30", "duration_min": 50},
        {"id": "MWF_1130", "days": ["M","W","F"], "start_time": "11:30", "duration_min": 50},
        {"id": "MWF_1230", "days": ["M","W","F"], "start_time": "12:30", "duration_min": 50},
        {"id": "MWF_1330", "days": ["M","W","F"], "start_time": "13:30", "duration_min": 50},
        {"id": "MWF_1430", "days": ["M","W","F"], "start_time": "14:30", "duration_min": 50},
        {"id": "MWF_1530", "days": ["M","W","F"], "start_time": "15:30", "duration_min": 50},
        {"id": "TR_0900",  "days": ["T","R"],     "start_time": "09:00", "duration_min": 75},
        {"id": "TR_1030",  "days": ["T","R"],     "start_time": "10:30", "duration_min": 75},
        {"id": "TR_1200",  "days": ["T","R"],     "start_time": "12:00", "duration_min": 75},
        {"id": "TR_1330",  "days": ["T","R"],     "start_time": "13:30", "duration_min": 75},
        {"id": "TR_1500",  "days": ["T","R"],     "start_time": "15:00", "duration_min": 75},
    ]

    # Rooms with varied capacities
    all_rooms = [
        ("CL50_224", 470), ("PHYS_112", 280), ("WALC_1055", 300), ("EE_129", 200),
        ("LWSN_1142", 120), ("LWSN_B151", 60), ("LWSN_B155", 50), ("HAAS_G066", 45),
        ("REC_122", 30), ("STEW_202", 35), ("BRNG_2280", 80), ("MATH_175", 90)
    ]
    # Pick a subset of rooms to make it harder
    selected_rooms = {r[0]: r[1] for r in all_rooms[:NUM_ROOMS]}

    # 2. Generate Professors
    professors = [f"Prof_{chr(65+i)}" for i in range(NUM_PROFESSORS)] # Prof_A, Prof_B...

    # 3. Generate Courses
    courses = {}
    
    # Bottleneck courses
    # We force 2 big classes that only fit in the biggest 1 or 2 rooms
    courses["CS_18000"] = {"professor": "Prof_Star", "enrollment": 450} 
    courses["CS_24000"] = {"professor": "Prof_Star", "enrollment": 275} # Same prof, hard constraint.

    for i in range(NUM_COURSES - 2):
        course_code = f"CS_{random.randint(300, 599)}{random.choice(['00', '01'])}"
        
        # Weighted random enrollment:
        rand_val = random.random()
        if rand_val < 0.6:
            enroll = random.randint(20, 60)   # 60% Small
        elif rand_val < 0.9:
            enroll = random.randint(61, 120)  # 30% Medium
        else:
            enroll = random.randint(121, 250) # 10% Large
            
        courses[course_code] = {
            "professor": random.choice(professors),
            "enrollment": enroll
        }

    # 4. Construct Final JSON
    data = {
        "time_slots": time_slots,
        "rooms": selected_rooms,
        "courses": courses
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Generated {OUTPUT_FILE} with {len(courses)} courses, {len(selected_rooms)} rooms.")

if __name__ == "__main__":
    generate()