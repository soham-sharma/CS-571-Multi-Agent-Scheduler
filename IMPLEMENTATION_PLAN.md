# MACSS Implementation Plan: Stage 2 (Multi-Agent Negotiation)

**Status:** Phase 1 (CSP Solver) Complete ✅ | Phase 2 (Multi-Agent Layer) - Planning Phase

---

## Overview

This document organizes the implementation plan for Stage 2 of MACSS, focusing on building the multi-agent negotiation layer that will improve the initial CSP-generated schedule (A0) through distributed coordination among agents.

---

## Step 1: Agent Architecture Implementation

### 1.1 Current Status
- **RegistrarAgent**: ✅ Conceptually "done" - hard constraints are already enforced in the CSP solver
  - The CSP solver in `csp_solver.py` already enforces:
    - Unique Room-Time constraints
    - Instructor Conflict constraints  
    - Room Capacity constraints
  - RegistrarAgent role: Monitor and maintain feasibility during negotiation (veto invalid proposals)
  
- **DepartmentAgent**: ✅ Conceptually "done" - acts as initializer
  - Role: Propose initial assignments (already handled by CSP solver generating A0)
  - During negotiation: May coordinate between agents or mediate conflicts

### 1.2 Agents to Implement

#### **ProfessorAgent** (Priority: HIGH)
**Requirements:**
- Each professor manages their assigned courses
- **New constraint**: Professor should teach at most 2 classes (this must be checked/enforced)
- Each professor has preferences for time slots and rooms
- Professors can propose changes to their course assignments
- Professors evaluate proposals based on their preference function `Pref_p(t, r)`

**Implementation Details:**
- One ProfessorAgent instance per unique professor
- Track which courses belong to each professor
- Store preference function/scoring mechanism
- Ability to generate proposals (single-course reassignment or swaps)
- Ability to evaluate and accept/reject proposals from other agents

**Priority During Negotiation:**
- Professors with the most student enrollments (highest total enrollment across their courses) should have higher priority in negotiation rounds
- This ensures popular/high-demand courses get better assignments first

#### **StudentAggregatorAgent** (Priority: HIGH)
**Requirements:**
- Simulates a population of students with course enrollments
- Calculates student conflict metrics: `Conflict(A, S)`
- Detects overlaps where students are enrolled in multiple courses at the same time
- Evaluates proposals based on impact on student schedule conflicts

**Implementation Details:**
- Maintains simulated student enrollment data
- For each student, tracks which courses they're enrolled in
- Calculates pairwise conflicts between courses (same time slot = conflict)
- Provides global conflict metric for cost function evaluation

---

### 1.3 Recommended File Structure
**File: `agents.py`**

```
agents.py
├── BaseAgent (abstract base class)
│   ├── Common message handling
│   ├── Proposal generation interface
│   └── State management
├── RegistrarAgent
│   ├── Hard constraint validation
│   ├── Proposal vetoing logic
│   └── Mediation capabilities
├── DepartmentAgent
│   ├── Initial proposal coordination
│   └── Conflict mediation
├── ProfessorAgent
│   ├── Preference scoring function
│   ├── Course management (max 2 courses)
│   ├── Priority calculation (based on enrollment)
│   └── Proposal generation/evaluation
└── StudentAggregatorAgent
    ├── Student enrollment simulation
    ├── Conflict detection
    └── Global conflict metric calculation
```

---

## Step 2: Preference and Student Data Generation

### 2.1 Current Status
- Course generation: ✅ Done in `synthetic_data.py`
- Student enrollment simulation: ❌ Not yet implemented

### 2.2 Implementation Requirements

#### **A. Preference Generation (Similar to Course Generation)**
**Location:** Extend `synthetic_data.py` or create new `preference_generator.py`

**What to Generate:**
1. **Professor Preferences** - For each professor, randomly generate:
   - Time-of-day preferences (morning/afternoon preference)
   - Day-of-week preferences (avoid Fridays, prefer certain days)
   - Room preferences (optional: prefer certain room types/sizes)
   - Preference strength/weights

2. **Student Enrollment Patterns** - Randomly generate:
   - Number of students (should be random/variable based on total enrollment)
   - For each student: which courses they're enrolled in (based on course enrollment numbers)
   - Distribution logic: Some students take 3-4 courses, others take 1-2

**Recommended Approach:**
- Create a function similar to `generate()` in `synthetic_data.py`
- Generate preferences as a separate JSON structure or add to existing input files
- Store in format like:
  ```json
  {
    "professor_preferences": {
      "Prof_A": {
        "preferred_times": ["MWF_0930", "MWF_1030"],
        "avoid_times": ["TR_1500"],
        "preferred_days": ["M", "W"],
        "time_of_day": "morning"  // "morning", "afternoon", "no_preference"
      }
    },
    "student_enrollments": {
      "student_1": ["CS_18000", "CS_24000", "CS_30100"],
      "student_2": ["CS_18000", "CS_30200"],
      ...
    }
  }
  ```

#### **B. Integration with data_model.py**
**What to Add:**
- Load professor preferences from generated/preference file
- Load student enrollment data
- Calculate total enrollments per professor (for priority ranking)
- Store in the data dictionary returned by `load_data()`

**Extended Data Structure:**
```python
return {
    "course_ids": course_ids,
    "full_domain": full_domain,
    "professors": professors,
    "enrollments": enrollments,
    "room_capacities": rooms,
    "time_slot_details": time_slots,
    # NEW ADDITIONS:
    "professor_preferences": {...},      # Preference data per professor
    "student_enrollments": {...},        # Student -> courses mapping
    "professor_priorities": {...}        # Professor -> total enrollment (for negotiation priority)
}
```

### 2.3 Student Enrollment Simulation Logic

**Recommendation:**
- Generate student count based on total course enrollments
- Each course has `enrollment` number - create that many student-course mappings
- Students can enroll in multiple courses (weighted probability)
- Distribution:
  - 60% of students: 2-3 courses
  - 30% of students: 4-5 courses  
  - 10% of students: 1 course
- Ensure realistic overlap (e.g., CS_18000 and CS_24000 might have many shared students)

---

## Step 3: Cost/Objective Function Implementation

### 3.1 Objective Function Formula
From task.md:
```
Cost(A) = w_student * Conflict(A, S) + w_prof * Σ Penalty(Pref_prof(A[c]))
```

Where:
- `Conflict(A, S)`: Total number of student schedule conflicts
- `Penalty(Pref_prof(A[c]))`: Penalty for unsatisfied professor preferences
- `w_student`, `w_prof`: Weight parameters (recommend: w_student = 1.0, w_prof = 0.5)

### 3.2 Implementation Requirements

**File: `objective.py`**

**Functions to Implement:**
1. `calculate_student_conflicts(schedule, student_enrollments, time_slot_details)`
   - Counts number of students with overlapping course times
   - Returns total conflict count

2. `calculate_professor_penalty(schedule, professor_preferences, courses, professors)`
   - For each course, calculates how well it matches professor preferences
   - Returns total penalty score (higher = worse)

3. `calculate_total_cost(schedule, data, w_student=1.0, w_prof=0.5)`
   - Combines both metrics with weights
   - Returns final cost value (lower = better)

**Penalty Function Recommendation:**
- Preference satisfied: penalty = 0
- Slight mismatch: penalty = 1-2
- Major mismatch (e.g., assigned to avoided time): penalty = 5-10

---

## Step 4: Negotiation Protocol Implementation

### 4.1 Negotiation Parameters
- **Number of rounds**: 5-10 rounds maximum
- **Convergence criteria**: No improvement for 3 consecutive rounds
- **Stopping conditions**:
  1. Maximum rounds reached (10)
  2. No improvement for 3 rounds (convergence)
  3. Cost reaches acceptable threshold (optional)

### 4.2 Negotiation Algorithm

**Recommended Approach: Iterative Improvement with Prioritized Agents**

**Algorithm Structure:**
```
1. Initialize: Load A0 schedule, create agents, calculate initial cost
2. Sort agents by priority (professors by total enrollment)
3. For each round (max 10):
   a. For each agent (in priority order):
      - Agent generates proposals (single reassignment OR swap)
      - Evaluate each proposal:
        * Check hard constraints (RegistrarAgent validates)
        * Calculate new cost
        * If cost improves: accept proposal, update schedule
        * Else: reject proposal
   b. Calculate global cost for this round
   c. If cost improved: reset "no improvement" counter
      Else: increment "no improvement" counter
   d. If no improvement for 3 rounds: CONVERGED
   e. If round == 10: MAX_ROUNDS_REACHED
4. Return final schedule and metrics
```

### 4.3 Proposal Types

**Recommendation: Support BOTH types**

1. **Single Course Reassignment**
   - One course gets a new (time, room) assignment
   - Simpler, faster to evaluate
   - May get stuck in local minima

2. **Course Swaps**
   - Two courses swap their (time, room) assignments
   - More exploration capability
   - Can escape local minima
   - More complex constraint checking

**Implementation Strategy:**
- Agents can propose either type
- Start with single reassignment (simpler)
- If stuck (no improvement), allow swaps
- Or: 70% single reassignment, 30% swaps

### 4.4 Priority-Based Negotiation

**Professor Priority Calculation:**
```python
professor_priority[prof] = sum(enrollments[c] for all courses c taught by prof)
```

Higher enrollment = higher priority = agent acts earlier in each round

**Example:**
- Prof_A teaches CS_18000 (450 students) + CS_24000 (275 students) → priority = 725
- Prof_B teaches CS_30100 (45 students) → priority = 45
- Prof_A negotiates first

### 4.5 File Structure
**File: `negotiation.py`**

```
negotiation.py
├── NegotiationProtocol class
│   ├── __init__(schedule_A0, agents, data)
│   ├── run_negotiation(max_rounds=10, convergence_threshold=3)
│   ├── evaluate_proposal(proposal, current_schedule)
│   ├── apply_proposal(proposal, schedule)
│   └── check_convergence(improvement_history)
├── Proposal class
│   ├── Type: SINGLE_REASSIGNMENT or SWAP
│   ├── Courses involved
│   ├── New assignments
│   └── Expected cost delta
└── Helper functions
    ├── generate_proposals(agent, current_schedule)
    └── validate_proposal(proposal, schedule, hard_constraints)
```

---

## Step 5: Integration with Stage 1

### 5.1 Modified Workflow

**Current Flow (main.py):**
```
Input → Load Data → CSP Solver → Save A0 → Done
```

**New Flow (main.py):**
```
Input → Load Data → CSP Solver → Save A0 → 
  Load A0 → Create Agents → Run Negotiation → Save A_final → Done
```

### 5.2 Implementation Strategy

**Option A: Modify main.py directly**
- Add flag: `--stage2` or `--negotiation` to enable Stage 2
- By default, run both stages

**Option B: Create orchestrator file**
- Create `multi_agent_scheduler.py` as Stage 2 orchestrator
- `main.py` calls Stage 1, then calls orchestrator for Stage 2

**Recommendation: Option A (simpler)**
- Extend `main.py` to support both stages
- Add command-line argument: `--stages 1|2|both` (default: "both")
- Keep code modular with clear stage separation

### 5.3 Data Flow

```
Stage 1 Output (A0):
  initial_schedule_A0.json: {course: [time_slot, room]}

Stage 2 Input:
  - Load A0 schedule
  - Load preferences (from data or generated)
  - Load student enrollments
  - Create agents with their data

Stage 2 Output (A_final):
  final_schedule_negotiated.json: {course: [time_slot, room]}
  negotiation_metrics.json: {rounds, final_cost, improvement_history, ...}
```

---

## Step 6: Evaluation Metrics System

### 6.1 Metrics to Track

1. **Student Conflict Rate**
   - Percentage of students with at least one schedule conflict
   - Formula: `(students_with_conflicts / total_students) * 100`

2. **Professor Preference Satisfaction**
   - Average preference score across all professors
   - Higher = better (preferences more satisfied)
   - Normalized score: 0.0 (worst) to 1.0 (best)

3. **Room Utilization**
   - Ratio of occupied classroom capacity to total available capacity
   - Formula: `sum(enrollments) / sum(room_capacities * time_slots)`

4. **Computation Time**
   - Time to complete CSP solving (Stage 1)
   - Time to complete negotiation (Stage 2)
   - Total time

5. **Negotiation Convergence**
   - Number of rounds until convergence
   - Number of proposals accepted/rejected
   - Cost improvement trajectory

### 6.2 Implementation

**File: `evaluation.py`**

**Functions:**
- `calculate_student_conflict_rate(schedule, student_enrollments, time_slot_details)`
- `calculate_professor_satisfaction(schedule, professor_preferences)`
- `calculate_room_utilization(schedule, enrollments, room_capacities, time_slots)`
- `generate_evaluation_report(stage1_metrics, stage2_metrics, negotiation_history)`

**Output Format:**
```json
{
  "student_conflict_rate": 0.15,
  "professor_satisfaction": 0.72,
  "room_utilization": 0.68,
  "stage1_time_seconds": 2.3,
  "stage2_time_seconds": 45.7,
  "negotiation_rounds": 7,
  "proposals_accepted": 23,
  "proposals_rejected": 12,
  "initial_cost": 145.2,
  "final_cost": 98.5,
  "improvement_percentage": 32.1
}
```

---

## Step 7: Visualization Dashboard

### 7.1 Visualization Components

**A. Timetable Grid View**
- Room × Time Slot matrix
- Each cell shows: Course ID, Enrollment, Professor
- Color coding:
  - Green: No conflicts
  - Yellow: Soft constraint violations (preference issues)
  - Red: Hard constraint violations (shouldn't happen in final)

**B. Metrics Dashboard**
- Bar charts: Before (A0) vs After (A_final) comparison
- Line chart: Cost improvement over negotiation rounds
- Pie chart: Room utilization breakdown

**C. Conflict Analysis**
- List of student conflicts (if any remain)
- List of unsatisfied preferences

### 7.2 Implementation

**File: `visualization.py`**

**Functions:**
- `plot_timetable(schedule, data, output_file="timetable.png")`
- `plot_metrics_comparison(a0_metrics, final_metrics, output_file="metrics.png")`
- `plot_negotiation_history(round_costs, output_file="negotiation_history.png")`
- `generate_dashboard(schedule_a0, schedule_final, metrics, output_dir="dashboard/")`

**Libraries:**
- Primary: `matplotlib` (simpler, faster to implement)
- Optional (if time): `dash` for interactive web dashboard

**Output:**
- Static images saved to `output/` directory
- Or HTML dashboard if using Dash

---

## Step 8: Baseline Comparison

### 8.1 Baselines to Compare

1. **Baseline 1: Centralized CSP (Current Stage 1)**
   - This is already implemented
   - Only satisfies hard constraints
   - No optimization for preferences or student conflicts

2. **Baseline 2: Random/Greedy Heuristic** (Optional)
   - Greedy assignment by enrollment size
   - Random assignment
   - Simple benchmark

### 8.2 Comparison Metrics

Run all systems on the same input data and compare:
- Student conflict rate (lower is better)
- Professor satisfaction (higher is better)
- Room utilization (higher is better)
- Computation time (lower is better)

**Expected Outcome:**
- MACSS (Stage 1 + Stage 2) should:
  - Match or improve on student conflicts vs Baseline 1
  - Significantly improve professor satisfaction vs Baseline 1
  - Similar or better room utilization
  - Acceptable computation time (within minutes)

### 8.3 Implementation

**File: `comparison.py` or add to `evaluation.py`**

**Function:**
- `compare_baselines(input_data, output_dir="comparison/")`
  - Runs CSP-only (Baseline 1)
  - Runs MACSS full (Stage 1 + Stage 2)
  - Generates comparison report

**Output:**
- Side-by-side comparison table
- Visualization comparing metrics
- Summary report (which is better and why)

---

## Implementation Timeline

### Week 1: Foundation
- ✅ Step 1: Agent architecture (ProfessorAgent, StudentAggregatorAgent)
- ✅ Step 2: Preference and student data generation
- ✅ Step 3: Cost/objective function

### Week 2: Core Negotiation
- ✅ Step 4: Negotiation protocol implementation
- ✅ Step 5: Integration with Stage 1

### Week 3: Evaluation & Visualization
- ✅ Step 6: Evaluation metrics
- ✅ Step 7: Visualization dashboard
- ✅ Step 8: Baseline comparison

---

## Key Design Decisions Summary

1. **Agent Priority**: Professors with higher total enrollment negotiate first
2. **Proposal Types**: Support both single reassignment AND swaps (recommend 70/30 split)
3. **Convergence**: 5-10 rounds max, stop if no improvement for 3 rounds
4. **Professor Limit**: Max 2 classes per professor (must be enforced/checked)
5. **Student Simulation**: Random generation similar to course generation
6. **Preference Generation**: Random but realistic (time-of-day, day preferences)
7. **Cost Weights**: w_student = 1.0, w_prof = 0.5 (adjustable)

---

## Questions & Recommendations

### Clarifications Needed:
1. **Professor teaching limit**: Should the constraint "max 2 classes" be enforced during:
   - Data generation (synthetic_data.py) - ensure no prof gets >2 courses?
   - CSP solver - add as hard constraint?
   - Or just checked during negotiation?

2. **Student count**: Should total student count be:
   - Sum of all course enrollments (students may be counted multiple times)?
   - Unique students (each student ID appears once)?
   - Recommendation: Unique students with realistic enrollment patterns

3. **Preference file format**: Separate JSON file or add to existing input files?
   - Recommendation: Separate `preferences.json` for modularity

### Recommendations:
- Start simple: Single reassignment proposals first, add swaps later
- Use priority queue for agent ordering (by enrollment)
- Log everything: All proposals, acceptances, rejections for analysis
- Make weights/configurable: Easy to tune w_student and w_prof
- Test incrementally: Unit tests for each component before integration

---


