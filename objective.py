# objective.py
from typing import Dict, Any


def _classify_time_of_day(start_time: str) -> str:
    # Returns morning, afternoon, or evening based on start hour
    h = int(start_time.split(":")[0])
    if h < 12:
        return "morning"
    if h < 17:
        return "afternoon"
    return "evening"


def _get_day_pattern(days) -> str:
    # Returns MWF, TR, or other based on day list
    s = set(days)
    if {"M", "W", "F"}.issubset(s):
        return "MWF"
    if {"T", "R"}.issubset(s):
        return "TR"
    return "other"


def calculate_student_conflicts(schedule, student_enrollments, time_slot_details) -> int:
    # Counts overlapping courses for each student
    total = 0

    def overlap(ts1, ts2):
        d1, d2 = time_slot_details[ts1], time_slot_details[ts2]
        common = set(d1["days"]) & set(d2["days"])
        if not common:
            return False
        def to_min(t):
            h, m = t.split(":")
            return int(h) * 60 + int(m)
        s1, s2 = to_min(d1["start_time"]), to_min(d2["start_time"])
        e1, e2 = s1 + d1["duration_min"], s2 + d2["duration_min"]
        return s1 < e2 and s2 < e1

    for sid, courses in student_enrollments.items():
        for i in range(len(courses)):
            ci = courses[i]
            if ci not in schedule:
                continue
            ts1 = schedule[ci]["time"]

            for j in range(i + 1, len(courses)):
                cj = courses[j]
                if cj not in schedule:
                    continue
                ts2 = schedule[cj]["time"]

                if overlap(ts1, ts2):
                    total += 1

    return total


def calculate_professor_penalty(schedule, professor_preferences, professors, time_slot_details) -> int:
    # Computes penalties for how badly courses violate professor prefs
    total = 0

    for course, info in schedule.items():
        prof = professors[course]
        prefs = professor_preferences.get(prof, {})

        ts = info["time"]
        ts_info = time_slot_details[ts]

        tod = _classify_time_of_day(ts_info["start_time"])
        pattern = _get_day_pattern(ts_info["days"])

        tod_pref = prefs.get("time_of_day_pref", [])
        pattern_pref = prefs.get("day_pattern_pref", "both")
        preferred_slots = prefs.get("preferred_time_slots", [])
        avoided_slots = prefs.get("avoided_time_slots", [])

        # Penalty for avoided time slot
        if ts in avoided_slots:
            total += 10

        # Penalty if not in preferred slot list
        if preferred_slots and ts not in preferred_slots:
            total += 3

        # Penalty for time-of-day mismatch
        if tod_pref and tod not in tod_pref:
            total += 2

        # Penalty for day-pattern mismatch
        if pattern_pref != "both" and pattern != pattern_pref:
            total += 2

    return total


def calculate_total_cost(schedule, data, w_student=1.0, w_prof=0.5) -> float:
    # Combines student conflicts and professor penalties
    student_conflicts = calculate_student_conflicts(
        schedule,
        data["student_enrollments"],
        data["time_slot_details"]
    )

    prof_penalty = calculate_professor_penalty(
        schedule,
        data["professor_preferences"],
        data["professors"],
        data["time_slot_details"]
    )

    return w_student * student_conflicts + w_prof * prof_penalty
