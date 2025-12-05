# preferences.py
import json
import random
import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any

RNG = random.Random(42)
OUTPUT_FILE_DEFAULT = "preferences.json"


def classify_time_of_day(start_time: str) -> str:
    """
    start_time: "HH:MM" (24h)
    Returns: "morning" (<12), "afternoon" (12–17), "evening" (>=17)
    """
    hour = int(start_time.split(":")[0])
    if hour < 12:
        return "morning"
    elif hour < 17:
        return "afternoon"
    else:
        return "evening"


def get_day_pattern(days: List[str]) -> str:
    """
    days: list like ["M","W","F"] or ["T","R"]
    Returns "MWF", "TR", or "other"
    """
    dset = set(days)
    if {"M", "W", "F"}.issubset(dset):
        return "MWF"
    if {"T", "R"}.issubset(dset):
        return "TR"
    return "other"


def pick_time_of_day_pref() -> List[str]:
    """
    Pick 1–3 time-of-day preferences out of {morning, afternoon, evening}.
    """
    options = ["morning", "afternoon", "evening"]
    k = RNG.randint(1, 3)
    return RNG.sample(options, k)


def pick_day_pattern_pref() -> str:
    """
    Pick one of {MWF, TR, both}.
    """
    return RNG.choice(["MWF", "TR", "both"])


def generate_professor_preferences(
    time_slots: Dict[str, Dict[str, Any]],
    courses_raw: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    time_slots: {time_id: {id, days, start_time, duration_min}}
    courses_raw: {"CS_500": {"professor": "Prof_A", "enrollment": 60}, ...}
    Returns:
      {prof_id: {
          "time_of_day_pref": [...],
          "day_pattern_pref": "MWF"/"TR"/"both",
          "preferred_time_slots": [...],
          "avoided_time_slots": [...]
      }}
    """
    # Build set of professors and map prof -> list of their courses
    prof_courses: Dict[str, List[str]] = defaultdict(list)
    for cid, info in courses_raw.items():
        prof = info["professor"]
        prof_courses[prof].append(cid)

    # Precompute metadata for time slots
    ts_meta = {}
    for ts_id, ts in time_slots.items():
        tod = classify_time_of_day(ts["start_time"])
        pattern = get_day_pattern(ts["days"])
        ts_meta[ts_id] = {"time_of_day": tod, "pattern": pattern}

    professor_prefs: Dict[str, Any] = {}

    for prof in prof_courses.keys():
        tod_pref = pick_time_of_day_pref()
        day_pref = pick_day_pattern_pref()

        # Candidate time slots matching preferences
        candidate_preferred = []
        candidate_avoid = []

        for ts_id, meta in ts_meta.items():
            tod = meta["time_of_day"]
            pattern = meta["pattern"]

            # Check pattern match
            match_pattern = False
            if day_pref == "MWF" and pattern == "MWF":
                match_pattern = True
            elif day_pref == "TR" and pattern == "TR":
                match_pattern = True
            elif day_pref == "both" and pattern in ("MWF", "TR"):
                match_pattern = True

            if match_pattern and tod in tod_pref:
                candidate_preferred.append(ts_id)
            else:
                # Could be avoided or neutral; we'll sample some as avoid
                candidate_avoid.append(ts_id)

        preferred_time_slots = RNG.sample(
            candidate_preferred, k=min(3, len(candidate_preferred))
        ) if candidate_preferred else []

        avoided_time_slots = RNG.sample(
            candidate_avoid, k=min(2, len(candidate_avoid))
        ) if candidate_avoid else []

        professor_prefs[prof] = {
            "time_of_day_pref": tod_pref,
            "day_pattern_pref": day_pref,
            "preferred_time_slots": preferred_time_slots,
            "avoided_time_slots": avoided_time_slots,
        }

    return professor_prefs


def generate_student_population(
    courses_raw: Dict[str, Dict[str, Any]],
) -> Dict[str, List[str]]:
    """
    Very simple synthetic student enrollment generator.
    Returns student_enrollments: {student_id: [course_ids...]}
    """
    course_ids = list(courses_raw.keys())
    enrollments = {cid: info["enrollment"] for cid, info in courses_raw.items()}

    total_enrollment = sum(enrollments.values())
    # Roughly each student takes 3–4 courses on avg
    approx_courses_per_student = 3.5
    num_students = max(1, int(total_enrollment / approx_courses_per_student))

    # Precompute weights for courses (proportional to enrollment)
    course_weights = [enrollments[cid] for cid in course_ids]
    weight_sum = float(sum(course_weights))

    def sample_course() -> str:
        r = RNG.random() * weight_sum
        acc = 0.0
        for cid, w in zip(course_ids, course_weights):
            acc += w
            if r <= acc:
                return cid
        return course_ids[-1]

    student_enrollments: Dict[str, List[str]] = {}

    for i in range(num_students):
        sid = f"student_{i}"
        r = RNG.random()
        if r < 0.1:
            num_courses = 1
        elif r < 0.7:
            num_courses = RNG.randint(2, 3)
        else:
            num_courses = RNG.randint(4, 5)

        chosen = set()
        for _ in range(num_courses):
            chosen.add(sample_course())
        student_enrollments[sid] = sorted(chosen)

    return student_enrollments


def generate_student_preferences(
    student_enrollments: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Each student gets:
      - time_of_day_pref: list of {morning, afternoon, evening}
      - day_pattern_pref: {MWF, TR, both}
    """
    prefs: Dict[str, Any] = {}
    for sid in student_enrollments.keys():
        tod_pref = pick_time_of_day_pref()
        day_pref = pick_day_pattern_pref()
        prefs[sid] = {
            "time_of_day_pref": tod_pref,
            "day_pattern_pref": day_pref,
        }
    return prefs


def load_input(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r") as f:
        data = json.load(f)

    time_slots_list = data.get("time_slots", [])
    time_slots = {ts["id"]: ts for ts in time_slots_list}
    courses_raw = data.get("courses", {})

    if not time_slots or not courses_raw:
        raise ValueError("Input JSON must contain 'time_slots' and 'courses'.")

    return {
        "time_slots": time_slots,
        "courses_raw": courses_raw,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic professor and student preferences."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="input_synthetic.json",
        help="Path to input JSON (same format as synthetic_data.py output).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=OUTPUT_FILE_DEFAULT,
        help=f"Output preferences JSON file (default: {OUTPUT_FILE_DEFAULT})",
    )
    args = parser.parse_args()

    base = load_input(args.input_file)
    time_slots = base["time_slots"]
    courses_raw = base["courses_raw"]

    professor_prefs = generate_professor_preferences(time_slots, courses_raw)
    student_enrollments = generate_student_population(courses_raw)
    student_prefs = generate_student_preferences(student_enrollments)

    out = {
        "professor_preferences": professor_prefs,
        "student_enrollments": student_enrollments,
        "student_preferences": student_prefs,
        "metadata": {
            "input_file": str(Path(args.input_file).name),
            "rng_seed": 42,
        },
    }

    with open(args.output, "w") as f:
        json.dump(out, f, indent=2)

    print(
        f"Generated {len(professor_prefs)} professor prefs and "
        f"{len(student_enrollments)} students -> {args.output}"
    )


if __name__ == "__main__":
    main()
