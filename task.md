Using the below text: 
```Multi-Agent Classroom Scheduling System
Overview of the Problem
Universities face a complex challenge in producing semester schedules that satisfy students, faculty, and administrators. In the Purdue CS Department, hundreds of students must register for overlapping required and elective courses, while instructors and rooms have limited availability. Even with partial automation, human schedulers still spend weeks resolving conflicts and balancing constraints.
Our project will design a Multi-Agent Classroom Scheduling System (MACSS) that treats course scheduling as a constraint satisfaction problem (CSP) solved through multi-agent negotiation. Each stakeholder—department, professor, registrar, or student representative—is modeled as an agent with individual goals and resources. Agents negotiate to assign classes to rooms and times while minimizing conflicts and maximizing course accessibility.
Formally, each class carries constraints on time, instructor, room capacity, and prerequisites. The objective is to (1) minimize student schedule overlaps, (2) satisfy room and instructor constraints, and (3) maximize student access to required courses. The project demonstrates how distributed AI reasoning can create flexible, transparent scheduling beyond traditional centralized solvers.

Motivation and Significance
Conventional scheduling tools rely on centralized optimization, yet real academic scheduling is inherently distributed—different groups hold conflicting priorities. Departmental schedulers, professors, and registrars each adjust parameters independently, often through negotiation. Modeling these stakeholders as intelligent agents mirrors this human process while enabling scalable automation.
A negotiation-based design improves modularity (new agents or policies can be added easily) and fairness, since each entity contributes preferences explicitly. A student-agent can advocate for high-demand courses, while professor-agents express soft preferences such as “prefer mornings” or “avoid Fridays.” A registrar-agent enforces hard institutional limits.
For Purdue CS, where room capacity frequently constrains enrollment, MACSS could illustrate how distributed AI coordination supports more equitable and efficient scheduling decisions.

Technical Approach
Architecture
The system combines CSP modeling with agent-based coordination. Hard constraints cover room capacities and instructor conflicts; soft constraints capture time and preference flexibility.
Agents
Department Agents propose initial course allocations.
Professor Agents accept or reject time slots based on preferences.
Student Aggregator Agent simulates collective enrollment to detect overlaps.
Registrar Agent ensures overall feasibility.
Constraint Solver
Implemented in Python using either the python-constraint library or a custom backtracking solver with heuristics such as Minimum Remaining Values (MRV) and Least Constraining Value (LCV).
Negotiation Protocol
Agents exchange proposals through a distributed message-passing process. When conflicts occur (e.g., two professors request the same slot), negotiation iteratively relaxes soft constraints until consensus or mediation by the registrar-agent.
Evaluation
The prototype will use a realistic subset of Purdue CS data (≈15 courses, 10 rooms, 10 time slots, 5 professors). Metrics include:
percentage of students with conflict-free schedules,
constraint satisfaction rate,
negotiation convergence time, and
overall balance among agent preferences.
Visualization
A simple dashboard (Matplotlib / Dash) will display the final timetable and highlight remaining conflicts or preference trade-offs.

Resources
Data: Purdue CS course listings (from public timetables) plus synthetic enrollment data representing student demand.
Tools: Python 3.x; libraries networkx, python-constraint, matplotlib/dash; GitHub for collaboration.
Optional Extension: integrate LangGraph to represent each agent as a node in a reasoning graph for future scalability.
Team Roles: members will divide responsibilities across constraint modeling, agent negotiation, data simulation, visualization, and testing.

Risk Management
Over-constrained data – some configurations may be infeasible.
Mitigation: relax soft constraints or use priority-based conflict resolution.
Negotiation deadlock – agents may fail to converge.
Mitigation: add a global mediator or fallback centralized CSP.
Data quality issues – missing or inconsistent schedule information.
Mitigation: clean and simplify data before integration.
Time limitations (6 weeks) – ambitious scope.
Mitigation: build the CSP core first; add negotiation and visualization later.

Plan of Activities and Timeline
Week
Milestone
Key Tasks
1 (Oct 28 – Nov 3)
Problem & Data Setup
Collect Purdue CS data, define agent roles, specify constraints, finalize architecture.
2 (Nov 4 – Nov 10)
Core CSP Solver
Implement and test base solver for room/time assignments.
3 (Nov 11 – Nov 17)
Multi-Agent Layer
Build negotiation logic and message-passing simulation.
4 (Nov 18 – Nov 24)
Integration & Testing
Combine solver + agents; run tests on realistic data.
5 (Nov 25 – Dec 1)
Visualization & Metrics
Develop timetable dashboard; compute evaluation statistics.
6 (Dec 2 – Dec 8)
Final Analysis & Report
Compare centralized vs multi-agent results; prepare final presentation.

This sequence ensures that the constraint engine is functional before adding communication and visualization features.

Conclusion
The Multi-Agent Classroom Scheduling System reimagines course scheduling through distributed artificial intelligence. By merging constraint satisfaction with negotiation-based coordination, MACSS captures the real dynamics of academic scheduling—balancing departmental needs, faculty preferences, and student access.
The project will provide hands-on experience applying search, reasoning, and planning methods from CS 571 to a tangible real-world problem. If successful, the framework could extend to other departments or institutions, incorporating richer preference models, dynamic adjustments, and interactive negotiation interfaces.


here is more infomration but in LaTeX ocde

\documentclass{article}
\usepackage{graphicx} 
\usepackage{times}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{amssymb}

\title{Multi-Agent Classroom Scheduling System}
\author{}
\date{}
\begin{document}

\maketitle

\section{Literature Survey}

One foundational work for our project is \textit{Distributed Constraint Optimization Problems and Applications: A Survey} by Fioretto, Pontelli, and Yeoh~\cite{fioretto2018dcop}. This survey outlines the core principles behind distributed constraint optimization, where multiple autonomous agents cooperatively search for assignments that satisfy global constraints while optimizing shared objectives. Distributed Constraint Optimization Problems (DCOPs) provide a formal model for agent communication, conflict resolution, and decentralized search, and they are widely applied in multi-agent resource allocation, scheduling, and coordination tasks. The paper highlights how DCOP frameworks enable agents to make local decisions while still contributing to a globally consistent solution, and it compares major algorithmic families including search-based, inference-based, and hybrid approaches. Our project builds on this foundation by framing classroom scheduling as a distributed constraint problem and extending these ideas to an academic environment with heterogeneous agents (professors, departments, registrar, and students) and domain-specific constraints not addressed in the survey.

One previous work that has worked on specifically on this topic is \textit{MAS\_UP-UCT: A Multi-Agent System for University Course Timetable Scheduling} by Mihaela Oprea \cite{oprea2007masuct}. This paper treats the scheduling problem as a distributed negotiation problem rather than a centralized optimization task. The system models the real structure of a university through layered agents: a main scheduler for room assignment, faculty schedulers for local course planning, expert assistants for each specialization, and personal agents for professors. These agents communicate with each other to resolve time and room conflicts by negotiating or persuading when preference conflicts occur. The author's work shows that multiple agents are able to satisfy conflicting constraints at a satisfactory level by mimicking the social negotiation process that is a part of academic scheduling. Our project expands on the work done in this paper by adding a formal constraint-satisfaction framework and quantitative evaluation metrics. This will allow the agents to both negotiate with each other and optimize conflict resolution based on measurable outcomes such as student access, room utilization, and schedule balance.

Another previous work on this subject is \textit{Modelling and Solving the University Course Timetabling Problem With Hybrid Teaching Considerations} by Matthew Davison, Ahmed Kheiri, and Konstantinos G.~Zografos \cite{davison2024hybrid}. In this paper, they extend the traditional course timetabling problem by incorporating hybrid teaching, where classes may be attended online, in person, or both. The authors solve this problem using a lexicographic optimization approach and test it on benchmark datasets that simulate COVID-19–era capacity constraints. Their results show that hybrid options introduce flexibility by easing room-capacity limits while preserving teaching quality and student satisfaction. Our project differs by adopting a decentralized, agent-based approach rather than a centralized mathematical optimization model. Instead of a single solver, we use negotiation among autonomous agents representing students, faculty, and administrators, allowing dynamic conflict resolution and adaptive decision-making across multiple stakeholders.

\section{Formal Model}

\subsection{CSP Components}
A CSP is defined by a set of variables, their domains, and the constraints on those variables.

\subsubsection{Variables (X)}
The set of variables $X$ consists of all the courses that need to be scheduled:
$$ X = \{c_1, c_2, ..., c_n\} $$
(where $n$ is the total number of courses).

\subsubsection{Domains (D)}
The domain $D$ represents the set of all possible values that can be assigned to each variable. We define:
\begin{itemize}
    \item $T = \{t_1, t_2, ..., t_k\}$: The set of all discrete time slots available.
    \item $R = \{r_1, r_2, ..., r_m\}$: The set of all available rooms.
\end{itemize}
The domain $D_i$ for any given course $c_i$ is the set of all possible (time, room) pairs:
$$ D_i = T \times R $$
The solution to the CSP is a complete assignment $A = \{a_1, a_2, ..., a_n\}$, where each $a_i$ is a pair $(t_j, r_k)$ from its domain $D_i$, such that all constraints are met.

\subsubsection{Constraints (C)}
The constraints are the rules that a valid schedule must follow.

\paragraph{A. Hard Constraints (Inviolable)}
These are constraints that \textit{must} be satisfied for a schedule to be considered valid.
\begin{itemize}
    \item \textbf{Unique Room-Time:} No two courses $c_i$ and $c_j$ (where $i \neq j$) can be assigned the same room $r_k$ at the same time slot $t_l$.
    $$ \text{If } A[c_i] = (t_l, r_k) \text{ and } A[c_j] = (t_l, r_k), \text{ then } i = j. $$
    
    \item \textbf{Instructor Conflict:} A professor cannot teach two different courses at the same time. Let $Prof(c_i)$ be the professor for course $c_i$.
    $$ \text{If } Prof(c_i) = Prof(c_j) \text{ and } i \neq j, \text{ then } Time(A[c_i]) \neq Time(A[c_j]). $$
    
    \item \textbf{Room Capacity:} The assigned room's capacity must meet or exceed the course's expected enrollment.
    $$ Capacity(Room(A[c_i])) \geq Enrollment(c_i) $$
    
    \item \textbf{Institutional Limits:} Courses must only be assigned to valid, registrar-approved time slots and rooms (enforced by the Registrar-Agent).
\end{itemize}

\paragraph{B. Soft Constraints (Preferences \& Optimization)}
These are constraints that are desirable but not strictly necessary. Violating them makes a schedule "worse."
\begin{itemize}
    \item \textbf{Professor Preferences:} Each professor $p$ has a preference function $Pref_p(t, r)$ that returns a score for any given time/room assignment.
    
    \item \textbf{Student Overlaps:} The primary objective is to minimize schedule conflicts for students. We define a $Conflict(A, S)$ function that counts the total number of conflicts for a set of simulated students $S$.
    $$ Conflict(A, S) = \sum_{s \in S} \sum_{c_i, c_j \in Req(s), i < j} [Time(A[c_i]) = Time(A[c_j])] $$
    (where $[\cdot]$ is 1 if true, 0 if false).
\end{itemize}

\subsection{The Multi-Agent Model}
This CSP is \textit{distributed} among the agents:
\begin{itemize}
    \item \textbf{Professor Agents} own their respective soft constraints ($Pref_p$).
    \item \textbf{Registrar Agent} owns and enforces the hard constraints.
    \item \textbf{Student Aggregator Agent} is responsible for calculating the $Conflict(A, S)$ objective function.
    \item \textbf{Department Agents} act as initiators, proposing initial assignments ($A$) to start the negotiation process.
\end{itemize}

\subsection{Objective Function}
The goal of the system is to find an assignment $A$ that satisfies all hard constraints and minimizes a weighted-sum objective function, $Cost(A)$:
$$ \text{Minimize  Cost}(A) = w_{student} \cdot Conflict(A, S) + w_{prof} \cdot \sum_{c_i \in X} \text{Penalty}(Pref_{Prof(c_i)}(A[c_i])) $$
Where $w_{student}$ and $w_{prof}$ are weights that balance the importance of minimizing student conflicts versus maximizing professor preferences.

\section{Initial Solution Direction}

Our solution approach will build a hybrid system combining a centralized
constraint-satisfaction engine with a decentralized negotiation protocol
among agents. The overall workflow proceeds in two stages: initialization
and distributed refinement.

\subsection{Stage 1: Centralized Initialization}
The system begins with a global CSP solver that generates an initial
feasible assignment \(A_0\) satisfying all hard constraints.  This ensures
a valid baseline schedule that respects room, instructor, and capacity
limits.  We plan to implement this solver using either the
\texttt{python-constraint} library or a custom backtracking search enhanced
by the Minimum Remaining Values (MRV) and Least Constraining Value (LCV)
heuristics.  The output \(A_0\) provides each agent with an initial proposal
for its local variables (courses).

\subsection{Stage 2: Multi-Agent Negotiation}
Once \(A_0\) is generated, autonomous agents iteratively exchange proposals
to improve the soft-constraint components of the objective function.
Professor Agents evaluate assignments according to their preference
functions \(Pref_p(t,r)\); the Student Aggregator Agent estimates global
conflicts \(Conflict(A,S)\); and the Registrar Agent maintains feasibility.
Negotiation follows a message-passing protocol inspired by Distributed
Constraint Optimization (DCOP) algorithms such as DPOP and Max-Sum.
Agents locally compute cost deltas for candidate swaps and accept proposals
that reduce the global cost \(Cost(A)\).

If no improving move exists, the Registrar Agent acts as a mediator to
relax lower-priority preferences or reinitialize subproblems.  This
two-stage approach ensures convergence to a near-optimal solution that
balances student accessibility and instructor satisfaction.

\subsection{Implementation Plan}
The implementation will be modular:
\begin{enumerate}
    \item \textbf{Constraint Layer:} CSP formulation and baseline solver.
    \item \textbf{Agent Layer:} Agent classes with local state and communication channels.
    \item \textbf{Negotiation Layer:} Protocol for proposal exchange and conflict resolution.
    \item \textbf{Visualization:} Real-time display of assignments using
    \texttt{matplotlib} or a lightweight web interface for debugging and
    analysis.
\end{enumerate}

This design allows incremental development---each module can be validated
independently and integrated during the testing phase.


\section{Evaluation Plan}

\subsection{Success Criteria}
The system will be considered successful if it can generate feasible,
conflict-free schedules that outperform a baseline centralized CSP in at
least one of the following metrics:
\begin{itemize}
    \item \textbf{Student Conflict Rate:} Fraction of students with overlapping courses.
    \item \textbf{Professor Preference Satisfaction:} Average preference score across all professors.
    \item \textbf{Room Utilization:} Ratio of occupied to available classroom capacity.
    \item \textbf{Computation Time:} Time required to converge to a feasible schedule.
\end{itemize}

\subsection{Baselines and Comparisons}
We will compare our Multi-Agent system to two baselines:
\begin{enumerate}
    \item \textbf{Baseline~1: Centralized CSP.}  A standard backtracking
    solver that optimizes all variables globally without negotiation.
    \item \textbf{Baseline~2: Random/Greedy Heuristic.}  Courses assigned
    greedily by enrollment size or at random to measure improvement over a
    naive strategy.
\end{enumerate}
The expectation is that MACSS will achieve comparable or better constraint
satisfaction while yielding higher preference scores and better scalability
as the number of agents increases.

\subsection{Experimental Setup}
Experiments will use realistic Purdue CS course data (approximately 15--20
classes, 10 rooms, and 10 time slots).  Synthetic student enrollment data
will simulate course demand distributions.  Each experiment will record:
execution time, number of negotiation rounds, and final objective value
\(Cost(A)\).

\subsection{Analysis}
Results will be summarized through comparative tables and visualizations of
schedule quality versus negotiation iterations.  Statistical metrics (mean
and variance over multiple runs) will quantify stability and repeatability.
We will also analyze agent-level behavior to examine which negotiation
patterns most effectively reduce conflicts.

A successful evaluation will demonstrate that distributed coordination can
achieve efficient, fair, and explainable scheduling decisions within
realistic computational limits.




\bibliographystyle{plain}
\bibliography{references}


\end{document}


