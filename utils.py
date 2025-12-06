"""
Shared utility functions for the Multi-Agent Classroom Scheduling System (MACSS).

This module provides common functions used across multiple components to avoid code duplication.
"""

from datetime import datetime, timedelta


def get_interval(time_slot_id, time_slot_details, day=None):
    """
    Calculates the start and end datetime for a specific time slot.

    Args:
        time_slot_id: ID of the time slot (e.g., "MWF_1030")
        time_slot_details: Dictionary containing time slot information
        day: Optional specific day (not used, kept for compatibility)

    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    details = time_slot_details[time_slot_id]
    start_time_str = details['start_time']
    duration = details['duration_min']

    # Use a dummy date for comparison, as we only care about time of day
    start_dt = datetime.strptime(start_time_str, "%H:%M")
    end_dt = start_dt + timedelta(minutes=duration)

    return start_dt, end_dt


def timeslots_overlap(ts_id_1, ts_id_2, time_slot_details):
    """
    Checks if two time slots conflict on any shared day.

    This is the canonical implementation used across the entire system.
    Returns True if conflict exists (time overlap on at least one shared day).
    Returns False otherwise (no conflict).

    Args:
        ts_id_1: First time slot ID
        ts_id_2: Second time slot ID
        time_slot_details: Dictionary containing time slot information

    Returns:
        bool: True if time slots overlap, False otherwise

    Examples:
        >>> details = {
        ...     "MWF_1030": {"days": ["M","W","F"], "start_time": "10:30", "duration_min": 50},
        ...     "MWF_1130": {"days": ["M","W","F"], "start_time": "11:30", "duration_min": 50}
        ... }
        >>> timeslots_overlap("MWF_1030", "MWF_1130", details)
        False
        >>> details["MWF_1045"] = {"days": ["M","W","F"], "start_time": "10:45", "duration_min": 50}
        >>> timeslots_overlap("MWF_1030", "MWF_1045", details)
        True
    """
    details_1 = time_slot_details[ts_id_1]
    details_2 = time_slot_details[ts_id_2]

    # Find common days (e.g., if both are MWF, conflict is possible)
    common_days = set(details_1['days']) & set(details_2['days'])

    if not common_days:
        # No shared days = no conflict
        return False

    # Since all instances of a given time slot (e.g., MWF_1030) have
    # the same start time and duration, we only need to check the time.
    start_1, end_1 = get_interval(ts_id_1, time_slot_details)
    start_2, end_2 = get_interval(ts_id_2, time_slot_details)

    # Time overlap check: start1 < end2 AND start2 < end1
    return (start_1 < end_2) and (start_2 < end_1)
