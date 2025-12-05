# MACSS: Multi-Agent Classroom Scheduling System

Phase 1 (CSP Solver) is complete. This module generates a valid initial schedule satisfying Room Capacity, Instructor Conflict, and Unique Room-Time constraints.

Generate Test Data

```bash
python synthetic_data.py
```

Run Solver

```bash
python main.py input_synthetic.json
```

Output: `initial_schedule_A0.json` (Used for the Agent Negotiation Layer)


Phase 2 files:
preferences.json provides professor and student preferences and enrollments
agents.py defines professor, student, and registrar agents
objective.py computes student conflicts, professor penalties, and total cost
negotiation.py runs multi-agent negotiation to improve the schedule
visualization.py produces cost history and comparison plots
