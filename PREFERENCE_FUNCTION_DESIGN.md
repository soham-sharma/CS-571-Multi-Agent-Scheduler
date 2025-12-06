# Professor Preference Function Design

## Overview

This document defines a simple but effective preference function for professors that evaluates how well a given time_slot assignment matches a professor's preferences. The function focuses on **time-of-day** and **day-of-week** preferences only.

**Key Principle**: Professors with higher course enrollments (more students) get priority during negotiation, ensuring that popular courses receive better time slot assignments.

---

## Design Philosophy

**Simple & Intuitive**: Easy to understand and implement  
**Focus on Critical Preferences**: Time and day preferences are most important for professors  
**Enrollment-Based Priority**: Higher enrollment = higher negotiation priority = preferences weighted more heavily  
**Normalized Scores**: Returns values that are easy to combine in cost function

---

## Preference Components

The preference function considers only two factors:

1. **Time-of-Day Preference** (Morning vs Afternoon) - 50% weight
2. **Day-of-Week Preference** (Preferred days, avoided days like Friday) - 50% weight

**Note**: Room preferences are not considered. Room assignments are determined solely by capacity constraints.

---

## Preference Data Structure

Each professor has preferences stored as:

```python
professor_preferences = {
    "Prof_A": {
        "time_of_day": "morning",  # "morning", "afternoon", or "no_preference"
        "preferred_days": ["M", "W"],  # List of preferred days: M, T, W, R, F
        "avoid_days": ["F"]  # Days to avoid if possible
    }
}
```

**Enrollment-Based Priority**: Each professor also has a total enrollment count across all their courses. This is calculated as:
```python
professor_total_enrollment[professor] = sum(enrollments[course] for all courses taught by professor)
```

Higher enrollment → Higher priority during negotiation → Their preferences are considered first and weighted more heavily in the cost function.

---

## Preference Function Design

### Function Signature

```python
def calculate_preference_score(time_slot_id, professor_prefs, time_slot_details):
    """
    Calculate how well a time slot assignment matches a professor's preferences.
    
    Args:
        time_slot_id (str): Time slot ID (e.g., "MWF_1030")
        professor_prefs (dict): Professor's preference dictionary
        time_slot_details (dict): Time slot details from data model
        
    Returns:
        float: Preference score from 0.0 (worst) to 1.0 (best)
    """
```

**Note**: Room is not considered in preference scoring. Room assignments are handled separately by capacity constraints.

### Scoring System

The function returns a score from **0.0 to 1.0** where:
- **1.0** = Perfect match (all preferences satisfied)
- **0.5** = Neutral (no strong preference, or mixed)
- **0.0** = Worst match (strongly avoided)

---

## Detailed Scoring Logic

### Component 1: Time-of-Day Score (weight: 0.5)

```python
def score_time_of_day(time_slot_details, professor_prefs):
    """
    Score based on morning/afternoon preference.
    
    Logic:
    - Morning: 07:00 - 12:00
    - Afternoon: 12:00 - 17:00
    
    Returns: 0.0 (wrong time) to 1.0 (perfect match)
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
```

### Component 2: Day-of-Week Score (weight: 0.5)

```python
def score_days_of_week(time_slot_details, professor_prefs):
    """
    Score based on preferred/avoided days.
    
    Returns: 0.0 (avoided days) to 1.0 (preferred days)
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
```

### Combined Preference Score

```python
def calculate_preference_score(time_slot_id, professor_prefs, time_slot_details):
    """
    Combined preference score using weighted components.
    
    Only considers time-of-day and day-of-week preferences.
    Room assignments are determined by capacity constraints, not preferences.
    """
    # Get time slot details
    ts_details = time_slot_details[time_slot_id]
    
    # Calculate component scores
    time_score = score_time_of_day(ts_details, professor_prefs)
    day_score = score_days_of_week(ts_details, professor_prefs)
    
    # Equal weighting: 50% time, 50% day
    total_score = 0.5 * time_score + 0.5 * day_score
    
    return total_score
```

---

## Penalty Function (For Cost Calculation)

When used in the objective function, we may want to convert the preference score to a penalty:

```python
def preference_to_penalty(preference_score):
    """
    Convert preference score (0-1) to penalty (higher = worse).
    
    Perfect preference (1.0) → 0 penalty
    Neutral (0.5) → 2 penalty
    Worst (0.0) → 5 penalty
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
```

Or use a linear conversion:
```python
def preference_to_penalty_linear(preference_score):
    """Linear conversion: penalty = 5 * (1 - preference_score)"""
    return 5.0 * (1.0 - preference_score)
```

---

## Enrollment-Based Priority

Professors with higher total enrollments across their courses get priority during negotiation. This is implemented in two ways:

1. **Negotiation Order**: Professors with more students negotiate first (their proposals are considered earlier)
2. **Cost Function Weighting**: Preferences of high-enrollment professors are weighted more heavily

```python
def calculate_professor_priority(professor, courses, enrollments):
    """
    Calculate professor priority based on total enrollment.
    
    Returns: Total enrollment count (higher = more priority)
    """
    professor_courses = [c for c in courses if courses[c]['professor'] == professor]
    total_enrollment = sum(enrollments[c] for c in professor_courses)
    return total_enrollment
```

Example:
- Prof_Star teaches CS_18000 (450 students) + CS_24000 (275 students) → Priority = 725
- Prof_A teaches CS_30100 (45 students) → Priority = 45
- Prof_Star negotiates first, and their preference violations cost more in the objective function

---

## Complete Example Implementation

```python
def calculate_preference_score(time_slot_id, professor_prefs, time_slot_details):
    """
    Calculate professor preference score for a time slot assignment.
    
    Only considers time-of-day and day-of-week preferences.
    Room is assigned separately based on capacity constraints.
    
    Returns: float from 0.0 (worst) to 1.0 (best)
    """
    ts_details = time_slot_details[time_slot_id]
    
    # Component 1: Time of Day (50% weight)
    time_pref = professor_prefs.get("time_of_day", "no_preference")
    if time_pref != "no_preference":
        start_time_str = ts_details['start_time']
        hour = int(start_time_str.split(':')[0])
        
        if time_pref == "morning":
            time_score = 1.0 if 7 <= hour < 12 else 0.2
        else:  # afternoon
            time_score = 1.0 if 12 <= hour < 17 else 0.2
    else:
        time_score = 0.5  # Neutral
    
    # Component 2: Days of Week (50% weight)
    preferred_days = set(professor_prefs.get("preferred_days", []))
    avoid_days = set(professor_prefs.get("avoid_days", []))
    slot_days = set(ts_details['days'])
    
    if slot_days & avoid_days:
        day_score = 0.1  # Contains avoided day
    elif preferred_days and (slot_days & preferred_days):
        match_ratio = len(slot_days & preferred_days) / len(slot_days)
        day_score = 0.5 + (match_ratio * 0.5)  # 0.5 to 1.0
    elif not preferred_days and not avoid_days:
        day_score = 0.5  # Neutral
    else:
        day_score = 0.3  # Below neutral
    
    # Equal weighting: 50% time, 50% day
    total_score = 0.5 * time_score + 0.5 * day_score
    
    return round(total_score, 3)  # Round to 3 decimal places


def calculate_penalty(preference_score, enrollment_weight=1.0):
    """
    Convert preference score to penalty for cost function.
    Lower preference score = higher penalty.
    
    Args:
        preference_score: Score from 0.0 to 1.0
        enrollment_weight: Weight based on professor's total enrollment (higher enrollment = higher weight)
    
    Returns:
        float: Penalty value (higher = worse)
    """
    # Base penalty: ranges from 0 (best) to 5 (worst)
    base_penalty = 5.0 * (1.0 - preference_score)
    
    # Weight by enrollment: professors with more students get higher penalty weights
    # This ensures their preferences matter more in the cost function
    weighted_penalty = base_penalty * enrollment_weight
    
    return weighted_penalty
```

---

## Usage Example

```python
# Example professor preferences
prof_prefs = {
    "time_of_day": "morning",
    "preferred_days": ["M", "W"],
    "avoid_days": ["F"]
}

# Example time slot: MWF_1030 (Monday/Wednesday/Friday at 10:30)
time_slot_details = {
    "MWF_1030": {
        "days": ["M", "W", "F"],
        "start_time": "10:30",
        "duration_min": 50
    },
    "TR_0900": {
        "days": ["T", "R"],
        "start_time": "09:00",
        "duration_min": 75
    }
}

# Calculate preference score (room not needed)
score = calculate_preference_score(
    "MWF_1030", 
    prof_prefs, 
    time_slot_details
)

print(f"Preference Score: {score}")  # ~0.55 (mixed: morning ✓, but has Friday ✗)
# Time: 1.0 (morning), Day: 0.1 (has Friday), Average: (1.0 + 0.1) / 2 = 0.55

# Professor has 725 total enrollment across courses
enrollment_weight = 725 / 100  # Normalize (example: divide by 100)
penalty = calculate_penalty(score, enrollment_weight)
print(f"Penalty: {penalty}")  # ~20.25 (high penalty due to high enrollment)

# Better assignment: TR_0900 (Tuesday/Thursday, morning)
score2 = calculate_preference_score(
    "TR_0900",
    prof_prefs,
    time_slot_details
)
# Time: 1.0 (morning), Day: 0.3 (doesn't match preferred M/W), Average: (1.0 + 0.3) / 2 = 0.65

# Best: MWF_0930 or MWF_0830 (matches preferred days, no Friday conflict)
# But wait, MWF always includes Friday... so TR is actually better despite not matching preferred days
```

---

## Design Decisions

### Why Only Time and Day?

1. **Time-of-Day (50%)**: Very common preference - professors often prefer mornings or afternoons
2. **Days-of-Week (50%)**: Critical - avoiding Fridays, preferring certain days is common
3. **Room Excluded**: Room assignments are determined by capacity constraints (hard constraint), not preferences. Students need rooms that fit enrollment, so room preferences would conflict with capacity requirements.

### Why 0.0 to 1.0 Scale?

- Easy to understand (1.0 = perfect, 0.0 = worst)
- Can be weighted easily in cost function
- Can be converted to penalty easily

### Why Equal Weights (50/50)?

- Time and Day are both equally important to professors
- Simple and balanced
- **Adjustable**: Weights can be tuned if needed, but 50/50 is a good default

### Why Enrollment-Based Priority?

- Professors with more students (higher enrollment) impact more students' schedules
- Giving them priority ensures popular courses get better time slots
- This reduces overall student conflicts (more students benefit from better assignments)
- Priority affects both negotiation order and cost function weighting

---

## Extensions (Future)

This simple function can be extended with:

1. **Preferred Start Hour**: Exact hour preference (e.g., prefer 10:00 AM specifically)
2. **Consecutive Classes**: Prefer back-to-back classes for better schedule flow
3. **Spread Preferences**: Prefer classes spread across week vs. concentrated on certain days
4. **Time Between Classes**: Minimum time gap preference between classes
5. **Building Preferences**: Prefer certain buildings or locations

**Note**: Room preferences remain excluded - rooms are assigned by capacity constraints only.

---

## Summary

This preference function provides:
- ✅ Simple to understand and implement
- ✅ Focuses on critical preferences (time-of-day and day-of-week only)
- ✅ Enrollment-based priority ensures popular courses get better assignments
- ✅ Returns normalized scores (0-1)
- ✅ Easy to extend later
- ✅ Works well with penalty-based cost function

**Key Features:**
- Only considers time and day preferences (no room preferences)
- Equal weighting (50% time, 50% day)
- Enrollment counts determine negotiation priority
- Higher enrollment professors' preferences weighted more in cost function

**Next Step**: Integrate this into the agent system and preference generation.

