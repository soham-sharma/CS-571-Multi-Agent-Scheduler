# Implementation Review: What Was Built vs. Implementation Plan

This document compares the actual implementation (from git pull) with the planned implementation from `IMPLEMENTATION_PLAN.md`.

---

## ✅ **WHAT MATCHES THE PLAN**

### 1. Agent Architecture (`agents.py`)
**Status: ✅ MOSTLY ALIGNED**

✅ **Implemented correctly:**
- `BaseAgent` class exists with common structure
- `RegistrarAgent` validates hard constraints (room capacity, room-time conflicts)
- `ProfessorAgent` generates proposals (single and swap)
- `StudentAggregatorAgent` computes student conflicts
- Proposal class structure (`Proposal` dataclass)
- Both single reassignment and swap proposals supported

❌ **Missing from plan:**
- `DepartmentAgent` - Not implemented (though plan said it was "conceptually done")
- **Professor max 2 classes constraint** - NOT ENFORCED (plan specified this must be checked)

### 2. Negotiation Protocol (`negotiation.py`)
**Status: ✅ FULLY ALIGNED**

✅ **Matches plan perfectly:**
- Max 10 rounds (configurable)
- Convergence: no improvement for 3 rounds
- Professors sorted by enrollment priority
- Registrar validates proposals
- Only accepts cost-improving proposals
- Tracks cost history
- Supports both single and swap proposals (70% single, 30% swap in ProfessorAgent)

### 3. Data Model (`data_model.py`)
**Status: ✅ ALIGNED**

✅ **Correctly implemented:**
- Loads preferences from JSON
- Calculates professor priorities (total enrollment)
- Integrates all data structures
- Handles missing preferences file gracefully

### 4. Main Integration (`main.py`)
**Status: ✅ ALIGNED**

✅ **Correctly implemented:**
- Runs Stage 1 (CSP) and Stage 2 (Negotiation)
- Saves both A0 and final schedules
- Generates visualizations
- Prints comparison metrics

### 5. Visualization (`visualization.py`)
**Status: ✅ PARTIALLY ALIGNED**

✅ **Implemented:**
- Cost history plot (negotiation rounds)
- Basic comparison chart (A0 vs Final)
- Conflict heatmap (optional, exists but commented out)

⚠️ **Missing from plan:**
- Timetable grid view (room × time slot matrix with courses)
- Color-coded cells for conflicts
- Room utilization visualization

---

## ⚠️ **WHAT DIFFERS FROM THE PLAN**

### 1. Preference Function Design ⚠️ **SIGNIFICANT DIFFERENCE**

**Planned (from `PREFERENCE_FUNCTION_DESIGN.md`):**
```python
professor_preferences = {
    "Prof_A": {
        "time_of_day": "morning",  # Single value: "morning", "afternoon", or "no_preference"
        "preferred_days": ["M", "W"],  # List of preferred days
        "avoid_days": ["F"]  # List of avoided days
    }
}
```

**Actually Implemented (in `generate_preferences.py` and `objective.py`):**
```python
professor_preferences = {
    "Prof_A": {
        "time_of_day_pref": ["morning", "afternoon"],  # List (1-3 values)
        "day_pattern_pref": "MWF",  # "MWF", "TR", or "both"
        "preferred_time_slots": ["MWF_0930", "MWF_1030"],  # Specific time slot IDs
        "avoided_time_slots": ["MWF_1430"]  # Specific time slot IDs
    }
}
```

**Key Differences:**
1. **Time-of-day**: Plan = single value, Implementation = list of 1-3 preferences
2. **Day preferences**: Plan = `preferred_days` + `avoid_days` lists, Implementation = `day_pattern_pref` (MWF/TR/both)
3. **Specific slots**: Implementation adds `preferred_time_slots` and `avoided_time_slots` (not in plan)
4. **No preference function**: Implementation doesn't use the `calculate_preference_score()` function we designed

### 2. Professor Penalty Calculation ⚠️ **DIFFERENT APPROACH**

**Planned Approach:**
- Use preference function to get score (0.0 to 1.0)
- Convert score to penalty using `calculate_penalty()` function
- Weight by enrollment for high-enrollment professors

**Actual Implementation (`objective.py`):**
```python
def calculate_professor_penalty(...):
    # Penalty for avoided time slot: +10
    # Penalty if not in preferred slot list: +3
    # Penalty for time-of-day mismatch: +2
    # Penalty for day-pattern mismatch: +2
```
- Uses additive penalties (not score-based)
- Doesn't use the preference scoring function we designed
- No enrollment weighting in penalty calculation (priority only affects negotiation order)

**Impact:** The penalty system is simpler but doesn't match the design document.

### 3. Student Preferences ⚠️ **NOT IN PLAN**

**Actually Implemented:**
- `generate_preferences.py` generates `student_preferences` with time-of-day and day-pattern preferences
- These preferences are loaded in `data_model.py`
- **BUT**: They are never used! No code references `student_preferences` for cost calculation.

**Plan:** Students only had enrollment data, not preferences (preferences were professor-only).

---

## 📋 **SUMMARY OF DEVIATIONS**

### Major Deviations:
1. ❌ **Preference Format**: Different data structure than designed
2. ❌ **Preference Function**: Doesn't use the `calculate_preference_score()` function from design doc
3. ❌ **Penalty System**: Additive penalties instead of score-to-penalty conversion
4. ❌ **Max 2 Classes Constraint**: Not enforced for professors
5. ⚠️ **Enrollment Weighting**: Priority affects negotiation order but not penalty weights

### Minor Deviations:
1. ⚠️ **DepartmentAgent**: Not implemented (acceptable, was "conceptually done")
2. ⚠️ **Visualization**: Missing timetable grid view (but has other plots)
3. ⚠️ **Student Preferences**: Generated but never used

### What Works Well:
1. ✅ Core negotiation algorithm matches plan
2. ✅ Agent architecture mostly correct
3. ✅ Data loading and integration works
4. ✅ Basic functionality is complete

---

## 🔍 **DETAILED CODE ANALYSIS**

### Preference Generation (`generate_preferences.py`)

**What it does:**
- Generates professor preferences based on time slot metadata
- Uses pattern matching (MWF/TR) instead of individual day preferences
- Generates preferred/avoided time slot lists
- Creates student enrollment population
- Creates unused student preferences

**Differences from plan:**
- Preference format doesn't match `PREFERENCE_FUNCTION_DESIGN.md`
- No connection to the designed preference scoring function
- Student preferences generated but unused

### Objective Function (`objective.py`)

**What it does:**
- Calculates student conflicts correctly ✅
- Calculates professor penalties using additive system
- Combines with weights (w_student=1.0, w_prof=0.5) ✅

**Differences from plan:**
- Doesn't use `calculate_preference_score()` function
- Penalty is additive (10, 3, 2, 2) not based on score-to-penalty conversion
- No enrollment-based penalty weighting

### ProfessorAgent (`agents.py`)

**What it does:**
- Generates proposals (70% single, 30% swap) ✅
- Uses random selection from domain
- Manages courses per professor ✅

**Missing:**
- No max 2 classes enforcement
- Doesn't use preference function to evaluate proposals
- Proposals are random, not preference-driven

---

## 🎯 **RECOMMENDATIONS**

### High Priority Fixes:
1. **Add max 2 classes constraint** - Check in data generation or CSP solver
2. **Align preference format** - Either:
   - Update `generate_preferences.py` to match design doc format, OR
   - Update `PREFERENCE_FUNCTION_DESIGN.md` to match implementation
3. **Use preference scoring function** - Integrate the designed `calculate_preference_score()` into penalty calculation

### Low Priority Improvements:
1. Remove unused `student_preferences` generation (or implement if needed)
2. Add timetable grid visualization
3. Add enrollment weighting to penalty calculation

### Optional Enhancements:
1. Make ProfessorAgent proposals preference-driven (not random)
2. Add DepartmentAgent if needed
3. Add more detailed evaluation metrics

---

## ✅ **CONCLUSION**

**Overall Assessment:** The implementation is **functionally complete** and follows the **core negotiation algorithm** from the plan. However, there are **significant differences** in:
- Preference data format
- Preference scoring approach
- Penalty calculation method

**The system works**, but it doesn't match the detailed preference function design we created. You should either:
1. **Update the design docs** to match implementation, OR
2. **Refactor code** to match design docs

The core functionality is solid, but alignment with the design document needs attention.

