"""
Professor Preference Scoring System

This module implements the preference function designed in PREFERENCE_FUNCTION_DESIGN.md.
It provides functions to calculate how well a time slot assignment matches a professor's preferences.

The preference function returns scores from 0.0 (worst) to 1.0 (best), considering:
- Time-of-day preference (morning vs afternoon) - 50% weight
- Day-of-week preference (preferred days, avoided days) - 50% weight

Room preferences are NOT considered - room assignments are determined by capacity constraints only.
"""

from typing import Dict, Any


def score_time_of_day(time_slot_details: Dict[str, Any], professor_prefs: Dict[str, Any]) -> float:
    """
    Score based on morning/afternoon preference.

    Logic:
    - Morning: 07:00 - 12:00
    - Afternoon: 12:00 - 17:00

    Args:
        time_slot_details: Dictionary with 'start_time' and 'duration_min'
        professor_prefs: Dictionary with 'time_of_day' field

    Returns:
        float: 0.0 (wrong time) to 1.0 (perfect match), 0.5 (neutral)
    """
    time_pref = professor_prefs.get("time_of_day", "no_preference")

    if time_pref == "no_preference":
        return 0.5  # Neutral

    # Extract start time from time slot
    start_time_str = time_slot_details['start_time']  # "10:30"
    hour = int(start_time_str.split(':')[0])  # 10

    if time_pref == "morning":
        if 7 <= hour < 12:
            return 1.0  # Perfect morning match
        else:
            return 0.2  # Afternoon (not preferred)

    elif time_pref == "afternoon":
        if 12 <= hour < 17:
            return 1.0  # Perfect afternoon match
        else:
            return 0.2  # Morning (not preferred)

    # Unknown preference
    return 0.5


def score_days_of_week(time_slot_details: Dict[str, Any], professor_prefs: Dict[str, Any]) -> float:
    """
    Score based on preferred/avoided days.

    Args:
        time_slot_details: Dictionary with 'days' field (list of day strings like ["M", "W", "F"])
        professor_prefs: Dictionary with 'preferred_days' and 'avoid_days' fields

    Returns:
        float: 0.0 (avoided days) to 1.0 (preferred days), 0.5 (neutral)
    """
    preferred_days = set(professor_prefs.get("preferred_days", []))
    avoid_days = set(professor_prefs.get("avoid_days", []))
    slot_days = set(time_slot_details['days'])  # ["M", "W", "F"]

    # Check if any days are avoided
    if slot_days & avoid_days:
        return 0.1  # Contains avoided day (e.g., Friday)

    # Check if matches preferred days
    if preferred_days and (slot_days & preferred_days):
        match_ratio = len(slot_days & preferred_days) / len(slot_days)
        return 0.5 + (match_ratio * 0.5)  # 0.5 to 1.0 based on overlap

    # No preference specified
    if not preferred_days and not avoid_days:
        return 0.5  # Neutral

    # Doesn't match preferences but not avoided
    return 0.3  # Below neutral


def calculate_preference_score(
    time_slot_id: str,
    professor_prefs: Dict[str, Any],
    time_slot_details: Dict[str, Dict[str, Any]]
) -> float:
    """
    Calculate professor preference score for a time slot assignment.

    Only considers time-of-day and day-of-week preferences.
    Room is assigned separately based on capacity constraints.

    Args:
        time_slot_id: ID of the time slot (e.g., "MWF_1030")
        professor_prefs: Professor's preference dictionary with:
            - time_of_day: "morning", "afternoon", or "no_preference"
            - preferred_days: List of preferred days ["M", "W", etc.]
            - avoid_days: List of days to avoid ["F", etc.]
        time_slot_details: Dictionary mapping time slot IDs to their details

    Returns:
        float: Preference score from 0.0 (worst) to 1.0 (best)

    Examples:
        >>> prof_prefs = {
        ...     "time_of_day": "morning",
        ...     "preferred_days": ["M", "W"],
        ...     "avoid_days": ["F"]
        ... }
        >>> time_slot_details = {
        ...     "MWF_1030": {"days": ["M", "W", "F"], "start_time": "10:30", "duration_min": 50}
        ... }
        >>> score = calculate_preference_score("MWF_1030", prof_prefs, time_slot_details)
        >>> # Time: 1.0 (morning), Day: 0.1 (has Friday), Average: 0.55
    """
    # Get time slot details
    ts_details = time_slot_details[time_slot_id]

    # Calculate component scores
    time_score = score_time_of_day(ts_details, professor_prefs)
    day_score = score_days_of_week(ts_details, professor_prefs)

    # Equal weighting: 50% time, 50% day
    total_score = 0.5 * time_score + 0.5 * day_score

    return round(total_score, 3)  # Round to 3 decimal places


def preference_to_penalty_linear(preference_score: float, max_penalty: float = 5.0) -> float:
    """
    Convert preference score (0-1) to penalty (higher = worse).

    Uses linear conversion: penalty = max_penalty * (1 - preference_score)

    Args:
        preference_score: Score from 0.0 to 1.0
        max_penalty: Maximum penalty value (default 5.0)

    Returns:
        float: Penalty value from 0 (best) to max_penalty (worst)

    Examples:
        >>> preference_to_penalty_linear(1.0)  # Perfect preference
        0.0
        >>> preference_to_penalty_linear(0.5)  # Neutral
        2.5
        >>> preference_to_penalty_linear(0.0)  # Worst preference
        5.0
    """
    return max_penalty * (1.0 - preference_score)


def preference_to_penalty_stepped(preference_score: float) -> float:
    """
    Convert preference score to penalty using stepped thresholds.

    Perfect preference (1.0) → 0 penalty
    Good (0.7+) → 1 penalty
    Neutral (0.5+) → 2 penalty
    Poor (0.3+) → 3 penalty
    Worst (<0.3) → 5 penalty

    Args:
        preference_score: Score from 0.0 to 1.0

    Returns:
        float: Penalty value

    Examples:
        >>> preference_to_penalty_stepped(1.0)
        0.0
        >>> preference_to_penalty_stepped(0.75)
        1.0
        >>> preference_to_penalty_stepped(0.5)
        2.0
        >>> preference_to_penalty_stepped(0.1)
        5.0
    """
    if preference_score >= 1.0:
        return 0.0
    elif preference_score >= 0.7:
        return 1.0
    elif preference_score >= 0.5:
        return 2.0
    elif preference_score >= 0.3:
        return 3.0
    else:
        return 5.0


def calculate_penalty(
    preference_score: float,
    enrollment_weight: float = 1.0,
    use_linear: bool = True
) -> float:
    """
    Convert preference score to penalty for cost function with enrollment-based weighting.

    Lower preference score = higher penalty.
    Professors with more students get higher penalty weights.

    Args:
        preference_score: Score from 0.0 to 1.0
        enrollment_weight: Weight based on professor's total enrollment
                          (higher enrollment = higher weight = more important to satisfy)
        use_linear: If True, use linear conversion; otherwise use stepped

    Returns:
        float: Weighted penalty value (higher = worse)

    Examples:
        >>> # Professor with 100 students, decent preference (0.7)
        >>> calculate_penalty(0.7, enrollment_weight=1.0)
        1.5
        >>> # Professor with 700 students, same preference (0.7)
        >>> calculate_penalty(0.7, enrollment_weight=7.0)
        10.5
    """
    # Calculate base penalty
    if use_linear:
        base_penalty = preference_to_penalty_linear(preference_score)
    else:
        base_penalty = preference_to_penalty_stepped(preference_score)

    # Weight by enrollment: professors with more students get higher penalty weights
    # This ensures their preferences matter more in the cost function
    weighted_penalty = base_penalty * enrollment_weight

    return weighted_penalty


def normalize_enrollment_weight(
    professor_enrollment: int,
    normalization_factor: float = 100.0
) -> float:
    """
    Normalize professor enrollment to use as weight in penalty calculation.

    Args:
        professor_enrollment: Total enrollment across all professor's courses
        normalization_factor: Divide enrollment by this to get reasonable weight values

    Returns:
        float: Normalized weight (e.g., 700 students → 7.0 weight)

    Examples:
        >>> normalize_enrollment_weight(700)  # High enrollment prof
        7.0
        >>> normalize_enrollment_weight(100)  # Regular prof
        1.0
        >>> normalize_enrollment_weight(50)   # Low enrollment prof
        0.5
    """
    return professor_enrollment / normalization_factor
