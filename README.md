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
