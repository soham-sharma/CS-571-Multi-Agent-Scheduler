# agents.py
from __future__ import annotations
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

Schedule = Dict[str, Dict[str, Any]]    # course -> {"time": ts_id, "room": room_id}
Assignment = Tuple[str, str]            # (time_slot_id, room_id)


@dataclass
class Proposal:
    proposal_type: str        # "single" or "swap"
    course_a: str
    new_assignment_a: Assignment
    course_b: Optional[str] = None
    new_assignment_b: Optional[Assignment] = None


class BaseAgent:
    def __init__(self, agent_id: str, rng: Optional[random.Random] = None):
        self.agent_id = agent_id
        self.rng = rng or random.Random(0)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.agent_id})"


class RegistrarAgent(BaseAgent):
    """
    Checks feasibility of schedule changes: room capacity + no overlapping use of same room.
    """
    def __init__(
        self,
        agent_id: str,
        time_slot_details: Dict[str, Dict],
        room_capacities: Dict[str, int],
        enrollments: Dict[str, int]
    ):
        super().__init__(agent_id)
        self.time_slot_details = time_slot_details
        self.room_capacities = room_capacities
        self.enrollments = enrollments

    def _timeslots_overlap(self, ts1: str, ts2: str) -> bool:
        d1, d2 = self.time_slot_details[ts1], self.time_slot_details[ts2]
        common = set(d1["days"]) & set(d2["days"])
        if not common:
            return False

        def to_min(t: str):
            h, m = t.split(":")
            return int(h) * 60 + int(m)

        s1, e1 = to_min(d1["start_time"]), None
        s2, e2 = to_min(d2["start_time"]), None
        e1 = s1 + d1["duration_min"]
        e2 = s2 + d2["duration_min"]

        return s1 < e2 and s2 < e1

    def validates(self, schedule: Schedule, proposal: Proposal) -> bool:
        updated = {c: v.copy() for c, v in schedule.items()}

        if proposal.proposal_type == "single":
            c = proposal.course_a
            ts, room = proposal.new_assignment_a
            updated[c]["time"], updated[c]["room"] = ts, room

        else:  # swap
            c1, c2 = proposal.course_a, proposal.course_b
            ts1, room1 = proposal.new_assignment_a
            ts2, room2 = proposal.new_assignment_b
            updated[c1]["time"], updated[c1]["room"] = ts1, room1
            updated[c2]["time"], updated[c2]["room"] = ts2, room2

        usage = {}
        for course, info in updated.items():
            ts = info["time"]
            room = info["room"]

            if self.room_capacities[room] < self.enrollments[course]:
                return False

            usage.setdefault(room, []).append(ts)

        for room, ts_list in usage.items():
            for i in range(len(ts_list)):
                for j in range(i + 1, len(ts_list)):
                    if self._timeslots_overlap(ts_list[i], ts_list[j]):
                        return False

        return True


class ProfessorAgent(BaseAgent):
    """
    Proposes schedule adjustments for courses taught by a specific professor.
    """
    def __init__(
        self,
        prof_id: str,
        courses: List[str],
        preferences: Dict[str, Any],
        full_domain: Dict[str, List[Assignment]],
        rng: Optional[random.Random] = None
    ):
        super().__init__(prof_id, rng)
        self.courses = courses
        self.preferences = preferences
        self.full_domain = full_domain

    def generate_proposal(self, schedule: Schedule) -> Optional[Proposal]:
        if not self.courses:
            return None

        course = self.rng.choice(self.courses)
        domain = self.full_domain[course]

        if self.rng.random() < 0.7:
            new_ts, new_room = self.rng.choice(domain)
            if (new_ts == schedule[course]["time"]
                and new_room == schedule[course]["room"]):
                return None

            return Proposal(
                proposal_type="single",
                course_a=course,
                new_assignment_a=(new_ts, new_room)
            )

        if len(self.courses) < 2:
            return None

        c1, c2 = self.rng.sample(self.courses, 2)
        return Proposal(
            proposal_type="swap",
            course_a=c1,
            new_assignment_a=(schedule[c2]["time"], schedule[c2]["room"]),
            course_b=c2,
            new_assignment_b=(schedule[c1]["time"], schedule[c1]["room"])
        )


class StudentAggregatorAgent(BaseAgent):
    """
    Computes student schedule conflicts under a given schedule.
    """
    def __init__(
        self,
        agent_id: str,
        student_enrollments: Dict[str, List[str]],
        time_slot_details: Dict[str, Dict]
    ):
        super().__init__(agent_id)
        self.student_enrollments = student_enrollments
        self.time_slot_details = time_slot_details

    def _timeslots_overlap(self, ts1: str, ts2: str) -> bool:
        d1, d2 = self.time_slot_details[ts1], self.time_slot_details[ts2]
        common = set(d1["days"]) & set(d2["days"])
        if not common:
            return False

        def to_min(t: str):
            h, m = t.split(":")
            return int(h) * 60 + int(m)

        s1 = to_min(d1["start_time"])
        s2 = to_min(d2["start_time"])
        e1 = s1 + d1["duration_min"]
        e2 = s2 + d2["duration_min"]

        return s1 < e2 and s2 < e1

    def compute_conflicts(self, schedule: Schedule) -> int:
        total = 0
        for sid, courses in self.student_enrollments.items():
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

                    if self._timeslots_overlap(ts1, ts2):
                        total += 1
        return total
