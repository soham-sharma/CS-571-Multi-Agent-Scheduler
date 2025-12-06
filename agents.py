# agents.py
from __future__ import annotations
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from utils import timeslots_overlap

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
                    if timeslots_overlap(ts_list[i], ts_list[j], self.time_slot_details):
                        return False

        return True


class ProfessorAgent(BaseAgent):
    """
    Proposes schedule adjustments for courses taught by a specific professor.

    Now uses preference-driven proposal generation: instead of random selection,
    proposals are biased toward time slots that better match professor preferences.
    """
    def __init__(
        self,
        prof_id: str,
        courses: List[str],
        preferences: Dict[str, Any],
        full_domain: Dict[str, List[Assignment]],
        time_slot_details: Dict[str, Dict[str, Any]],
        rng: Optional[random.Random] = None
    ):
        super().__init__(prof_id, rng)
        self.courses = courses
        self.preferences = preferences
        self.full_domain = full_domain
        self.time_slot_details = time_slot_details

    def _score_time_slot(self, time_slot_id: str) -> float:
        """
        Score how well a time slot matches this professor's preferences.
        Uses a simple preference scoring (higher = better).

        Returns a score that can be used as a weight for probabilistic selection.
        """
        from preference_scoring import calculate_preference_score

        if not self.preferences:
            return 1.0  # No preferences, all equal

        score = calculate_preference_score(
            time_slot_id,
            self.preferences,
            self.time_slot_details
        )

        # Convert 0-1 score to weight (add small epsilon to avoid zero weights)
        # Higher score = higher weight = more likely to be selected
        return score + 0.1

    def generate_proposal(self, schedule: Schedule) -> Optional[Proposal]:
        if not self.courses:
            return None

        course = self.rng.choice(self.courses)
        domain = self.full_domain[course]

        # 70% single reassignment, 30% swap
        if self.rng.random() < 0.7:
            # Instead of purely random, use weighted selection based on preference scores
            time_slots_in_domain = list(set([ts for ts, room in domain]))

            # Score each time slot
            scores = [self._score_time_slot(ts) for ts in time_slots_in_domain]
            total_score = sum(scores)

            # Probabilistic selection weighted by preference scores
            r = self.rng.random() * total_score
            acc = 0.0
            selected_ts = time_slots_in_domain[0]  # fallback

            for ts, score in zip(time_slots_in_domain, scores):
                acc += score
                if r <= acc:
                    selected_ts = ts
                    break

            # Now pick a room that matches this time slot
            possible_rooms = [room for ts, room in domain if ts == selected_ts]
            if not possible_rooms:
                # Fallback to random if something goes wrong
                new_ts, new_room = self.rng.choice(domain)
            else:
                new_room = self.rng.choice(possible_rooms)
                new_ts = selected_ts

            # Don't propose if it's the same as current
            if (new_ts == schedule[course]["time"]
                and new_room == schedule[course]["room"]):
                return None

            return Proposal(
                proposal_type="single",
                course_a=course,
                new_assignment_a=(new_ts, new_room)
            )

        # Swap proposal
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

                    if timeslots_overlap(ts1, ts2, self.time_slot_details):
                        total += 1
        return total
