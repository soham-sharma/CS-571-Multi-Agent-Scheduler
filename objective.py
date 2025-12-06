# objective.py
from typing import Dict, Any
from utils import timeslots_overlap
from preference_scoring import calculate_preference_score, calculate_penalty, normalize_enrollment_weight


def calculate_student_conflicts(schedule, student_enrollments, time_slot_details) -> int:
    """
    Counts overlapping courses for each student.

    This is a hard metric - each overlap represents a student who cannot
    take both courses due to scheduling conflicts.

    Args:
        schedule: Current schedule assignment
        student_enrollments: Dict of student_id -> list of course IDs
        time_slot_details: Time slot information

    Returns:
        int: Total number of student schedule conflicts
    """
    total = 0

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

                if timeslots_overlap(ts1, ts2, time_slot_details):
                    total += 1

    return total


def calculate_professor_penalty(
    schedule,
    professor_preferences,
    professors,
    time_slot_details,
    enrollments,
    use_enrollment_weighting=True
) -> float:
    """
    Computes penalties for professor preference violations using the preference scoring function.

    Uses the preference scoring system from preference_scoring.py that returns scores from
    0.0 (worst) to 1.0 (best), then converts to penalties with enrollment-based weighting.

    Professors with higher total enrollment have their penalties weighted more heavily,
    ensuring that courses with more students get better time slot assignments.

    Args:
        schedule: Current schedule assignment
        professor_preferences: Dict of professor_id -> preference dict
        professors: Dict of course_id -> professor_id
        time_slot_details: Time slot information
        enrollments: Dict of course_id -> enrollment count
        use_enrollment_weighting: If True, weight penalties by professor enrollment

    Returns:
        float: Total weighted penalty across all professors
    """
    # First, calculate total enrollment per professor for weighting
    professor_enrollment = {}
    for course, prof in professors.items():
        if prof not in professor_enrollment:
            professor_enrollment[prof] = 0
        professor_enrollment[prof] += enrollments.get(course, 0)

    total_penalty = 0.0

    for course, info in schedule.items():
        prof = professors[course]
        prefs = professor_preferences.get(prof, {})

        # Get assigned time slot
        ts = info["time"]

        # Calculate preference score (0.0 to 1.0)
        pref_score = calculate_preference_score(ts, prefs, time_slot_details)

        # Calculate enrollment weight
        if use_enrollment_weighting:
            prof_total_enrollment = professor_enrollment.get(prof, 100)
            enrollment_weight = normalize_enrollment_weight(prof_total_enrollment)
        else:
            enrollment_weight = 1.0

        # Convert to penalty with enrollment weighting
        penalty = calculate_penalty(pref_score, enrollment_weight, use_linear=True)

        total_penalty += penalty

    return total_penalty


def calculate_student_preference_penalty(
    schedule,
    student_preferences,
    student_enrollments,
    time_slot_details
) -> float:
    """
    Computes penalties for student preference violations.

    Similar to professor penalties, but for students. Each student has preferences
    for time-of-day and days-of-week. This is a soft constraint - students can still
    take courses even if preferences aren't met, but lower satisfaction.

    Args:
        schedule: Current schedule assignment
        student_preferences: Dict of student_id -> preference dict
        student_enrollments: Dict of student_id -> list of course IDs
        time_slot_details: Time slot information

    Returns:
        float: Total student preference penalty
    """
    total_penalty = 0.0

    for student_id, courses in student_enrollments.items():
        prefs = student_preferences.get(student_id, {})

        for course in courses:
            if course not in schedule:
                continue

            ts = schedule[course]["time"]

            # Calculate preference score for this course assignment
            pref_score = calculate_preference_score(ts, prefs, time_slot_details)

            # Convert to penalty (no enrollment weighting for students - all equal)
            # Use smaller max penalty for students (3.0 vs 5.0 for professors)
            penalty = 3.0 * (1.0 - pref_score)

            total_penalty += penalty

    return total_penalty


def calculate_total_cost(
    schedule,
    data,
    w_student_conflict=1.0,
    w_student_pref=0.3,
    w_prof=0.5
) -> float:
    """
    Combines all cost components into a single objective value.

    Cost Components:
    1. Student conflicts (hard conflicts - overlapping courses)
    2. Student preference penalties (soft - time/day preferences)
    3. Professor preference penalties (soft - time/day preferences with enrollment weighting)

    Args:
        schedule: Current schedule assignment
        data: Dictionary containing all system data
        w_student_conflict: Weight for student schedule conflicts (default 1.0)
        w_student_pref: Weight for student preference violations (default 0.3)
        w_prof: Weight for professor preference violations (default 0.5)

    Returns:
        float: Total weighted cost (lower is better)
    """
    # Hard conflicts: Students can't take both courses
    student_conflicts = calculate_student_conflicts(
        schedule,
        data["student_enrollments"],
        data["time_slot_details"]
    )

    # Soft preference penalties: Professor preferences with enrollment weighting
    prof_penalty = calculate_professor_penalty(
        schedule,
        data["professor_preferences"],
        data["professors"],
        data["time_slot_details"],
        data["enrollments"],
        use_enrollment_weighting=True
    )

    # Soft preference penalties: Student preferences
    student_pref_penalty = calculate_student_preference_penalty(
        schedule,
        data.get("student_preferences", {}),
        data["student_enrollments"],
        data["time_slot_details"]
    )

    total_cost = (
        w_student_conflict * student_conflicts +
        w_student_pref * student_pref_penalty +
        w_prof * prof_penalty
    )

    return total_cost
