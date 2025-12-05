# negotiation.py
from __future__ import annotations
import random
from typing import Dict, Any, List
from copy import deepcopy

from agents import (
    Proposal,
    ProfessorAgent,
    StudentAggregatorAgent,
    RegistrarAgent
)
from objective import calculate_total_cost


class NegotiationProtocol:
    def __init__(self, schedule_A0: Dict[str, List[str]], data: Dict[str, Any], rng_seed: int = 0):
        # Convert A0 JSON format into internal schedule
        self.schedule = {c: {"time": v[0], "room": v[1]} for c, v in schedule_A0.items()}
        self.data = data
        self.rng = random.Random(rng_seed)

        # Create all agents
        self.prof_agents = self._make_professor_agents()
        self.student_agent = StudentAggregatorAgent("student_agent", data["student_enrollments"], data["time_slot_details"])
        self.registrar = RegistrarAgent("registrar", data["time_slot_details"], data["room_capacities"], data["enrollments"])

        # Sort professors by total student impact
        priorities = data["professor_priorities"]
        self.prof_agents.sort(key=lambda a: priorities.get(a.agent_id, 0), reverse=True)

        self.history_costs = []

    def _make_professor_agents(self) -> List[ProfessorAgent]:
        # Map professors to the courses they teach
        courses_by_prof = {}
        for course, prof in self.data["professors"].items():
            courses_by_prof.setdefault(prof, []).append(course)

        agents = []
        for prof, course_list in courses_by_prof.items():
            agents.append(
                ProfessorAgent(
                    prof,
                    course_list,
                    self.data["professor_preferences"].get(prof, {}),
                    full_domain=self._domain_dict(),
                    rng=random.Random(hash(prof) % (2**32))
                )
            )
        return agents

    def _domain_dict(self):
        # All courses share the same domain for now
        return {course: self.data["full_domain"] for course in self.data["course_ids"]}

    def run(self, max_rounds: int = 10, no_improve_limit: int = 3):
        # Start with cost of A0
        current_cost = calculate_total_cost(self.schedule, self.data)
        self.history_costs.append(current_cost)

        no_improve = 0

        for _ in range(max_rounds):
            improved = False

            for agent in self.prof_agents:
                prop = agent.generate_proposal(self.schedule)
                if not prop:
                    continue

                # Check proposal against hard constraints
                if not self.registrar.validates(self.schedule, prop):
                    continue

                # Evaluate proposal
                new_sched = self._apply_proposal(self.schedule, prop)
                new_cost = calculate_total_cost(new_sched, self.data)

                # Accept only improvements
                if new_cost < current_cost:
                    self.schedule = new_sched
                    current_cost = new_cost
                    improved = True

            self.history_costs.append(current_cost)

            if improved:
                no_improve = 0
            else:
                no_improve += 1
                if no_improve >= no_improve_limit:
                    break

        return self.schedule, self.history_costs

    def _apply_proposal(self, sched, proposal):
        # Returns a schedule with the proposal applied
        ns = deepcopy(sched)

        if proposal.proposal_type == "single":
            c = proposal.course_a
            ts, room = proposal.new_assignment_a
            ns[c]["time"] = ts
            ns[c]["room"] = room

        else:
            c1, c2 = proposal.course_a, proposal.course_b
            ts1, room1 = proposal.new_assignment_a
            ts2, room2 = proposal.new_assignment_b

            ns[c1]["time"], ns[c1]["room"] = ts1, room1
            ns[c2]["time"], ns[c2]["room"] = ts2, room2

        return ns
