# visualization.py
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from utils import timeslots_overlap


def plot_cost_history(cost_history, outfile="cost_history.png"):
    # Plots cost per round
    plt.figure(figsize=(7, 4))
    plt.plot(cost_history, marker="o")
    plt.title("Negotiation Cost History")
    plt.xlabel("Round")
    plt.ylabel("Cost")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close()


def plot_basic_comparison(A0_conf, A0_prof, A_final_conf, A_final_prof, outfile="comparison.png"):
    # Bar chart for A0 vs Final costs
    labels = ["Student Conflicts", "Professor Penalty"]
    before = [A0_conf, A0_prof]
    after = [A_final_conf, A_final_prof]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(7, 4))
    plt.bar(x - width/2, before, width, label="A0")
    plt.bar(x + width/2, after, width, label="Final")

    plt.xticks(x, labels)
    plt.ylabel("Value")
    plt.title("A0 vs Final Schedule Comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close()


def plot_conflict_heatmap(schedule, student_enrollments, time_slot_details, outfile="conflicts_heatmap.png"):
    # Shows conflict count for each time slot
    slots = list(time_slot_details.keys())
    slot_index = {ts: i for i, ts in enumerate(slots)}

    matrix = np.zeros((len(slots), len(slots)))

    for sid, courses in student_enrollments.items():
        for i in range(len(courses)):
            ci = courses[i]
            if ci not in schedule:
                continue
            tsi = schedule[ci]["time"]

            for j in range(i + 1, len(courses)):
                cj = courses[j]
                if cj not in schedule:
                    continue
                tsj = schedule[cj]["time"]

                if timeslots_overlap(tsi, tsj, time_slot_details):
                    a, b = slot_index[tsi], slot_index[tsj]
                    matrix[a][b] += 1
                    matrix[b][a] += 1

    plt.figure(figsize=(8, 6))
    plt.imshow(matrix, cmap="hot", interpolation="nearest")
    plt.colorbar(label="Conflict Count")
    plt.title("Student Conflict Heatmap by Time Slot")
    plt.xticks(range(len(slots)), slots, rotation=90)
    plt.yticks(range(len(slots)), slots)
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close()


def plot_timetable_grid(schedule, data, title="Schedule Timetable", outfile="timetable.png"):
    """
    Create a room × time grid visualization of the schedule.

    Each cell shows the course ID, enrollment, and professor.
    Color-coded by room utilization efficiency.
    """
    time_slots = sorted(data["time_slot_details"].keys())
    rooms = sorted(data["room_capacities"].keys())

    # Create a mapping of (room, time_slot) -> course
    grid = {}
    for course, info in schedule.items():
        room = info["room"]
        time = info["time"]
        grid[(room, time)] = {
            "course": course,
            "professor": data["professors"][course],
            "enrollment": data["enrollments"][course]
        }

    # Create figure
    fig, ax = plt.figure(figsize=(max(14, len(time_slots) * 1.2), max(8, len(rooms) * 0.8))), plt.gca()

    # Set up grid
    ax.set_xlim(0, len(time_slots))
    ax.set_ylim(0, len(rooms))
    ax.set_xticks(np.arange(len(time_slots)) + 0.5)
    ax.set_yticks(np.arange(len(rooms)) + 0.5)
    ax.set_xticklabels(time_slots, rotation=45, ha='right')
    ax.set_yticklabels(rooms)
    ax.grid(True, which='both', color='gray', linewidth=0.5)
    ax.set_axisbelow(True)

    # Fill cells
    for i, room in enumerate(rooms):
        for j, ts in enumerate(time_slots):
            if (room, ts) in grid:
                course_info = grid[(room, ts)]
                course = course_info["course"]
                prof = course_info["professor"]
                enroll = course_info["enrollment"]
                room_cap = data["room_capacities"][room]

                # Color based on utilization
                utilization = enroll / room_cap if room_cap > 0 else 0
                if utilization > 0.9:
                    color = '#90EE90'  # Light green - excellent utilization
                elif utilization > 0.7:
                    color = '#FFFFE0'  # Light yellow - good utilization
                elif utilization > 0.4:
                    color = '#FFE4B5'  # Moccasin - okay utilization
                else:
                    color = '#FFB6C1'  # Light pink - poor utilization (wasted space)

                rect = mpatches.Rectangle((j, i), 1, 1, linewidth=1,
                                          edgecolor='black', facecolor=color)
                ax.add_patch(rect)

                # Add text
                text = f"{course}\n{prof}\n{enroll}/{room_cap}"
                ax.text(j + 0.5, i + 0.5, text, ha='center', va='center',
                       fontsize=7, wrap=True)

    ax.set_xlabel("Time Slot", fontsize=10)
    ax.set_ylabel("Room", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='#90EE90', edgecolor='black', label='Excellent (>90%)'),
        mpatches.Patch(facecolor='#FFFFE0', edgecolor='black', label='Good (70-90%)'),
        mpatches.Patch(facecolor='#FFE4B5', edgecolor='black', label='Okay (40-70%)'),
        mpatches.Patch(facecolor='#FFB6C1', edgecolor='black', label='Poor (<40%)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1),
             title='Room Utilization', fontsize=8)

    plt.tight_layout()
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    plt.close()


def plot_room_utilization(schedule, data, outfile="room_utilization.png"):
    """
    Visualize room utilization metrics.

    Shows:
    1. Bar chart of utilization rate per room
    2. Overall utilization statistics
    """
    # Calculate utilization for each room
    room_usage = {room: [] for room in data["room_capacities"].keys()}

    for course, info in schedule.items():
        room = info["room"]
        enrollment = data["enrollments"][course]
        capacity = data["room_capacities"][room]
        utilization = enrollment / capacity if capacity > 0 else 0
        room_usage[room].append(utilization)

    # Calculate average utilization per room
    room_avg_util = {}
    for room, utils in room_usage.items():
        if utils:
            room_avg_util[room] = np.mean(utils)
        else:
            room_avg_util[room] = 0

    # Sort by utilization
    sorted_rooms = sorted(room_avg_util.keys(), key=lambda r: room_avg_util[r], reverse=True)
    sorted_utils = [room_avg_util[r] for r in sorted_rooms]

    # Create plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Bar chart
    colors = ['#90EE90' if u > 0.7 else '#FFFFE0' if u > 0.4 else '#FFB6C1' for u in sorted_utils]
    ax1.barh(sorted_rooms, sorted_utils, color=colors, edgecolor='black')
    ax1.set_xlabel('Average Utilization Rate', fontsize=10)
    ax1.set_ylabel('Room', fontsize=10)
    ax1.set_title('Room Utilization by Room', fontsize=12, fontweight='bold')
    ax1.set_xlim(0, 1.0)
    ax1.axvline(x=0.7, color='green', linestyle='--', linewidth=1, label='Good threshold')
    ax1.axvline(x=0.4, color='orange', linestyle='--', linewidth=1, label='Poor threshold')
    ax1.legend(fontsize=8)
    ax1.grid(axis='x', alpha=0.3)

    # Statistics summary
    overall_util = np.mean(sorted_utils)
    num_excellent = sum(1 for u in sorted_utils if u > 0.9)
    num_good = sum(1 for u in sorted_utils if 0.7 < u <= 0.9)
    num_okay = sum(1 for u in sorted_utils if 0.4 < u <= 0.7)
    num_poor = sum(1 for u in sorted_utils if u <= 0.4)

    ax2.axis('off')
    stats_text = f"""
    ROOM UTILIZATION STATISTICS

    Overall Average: {overall_util:.1%}

    Breakdown:
    • Excellent (>90%): {num_excellent} rooms
    • Good (70-90%):    {num_good} rooms
    • Okay (40-70%):    {num_okay} rooms
    • Poor (<40%):      {num_poor} rooms

    Total Rooms: {len(sorted_rooms)}
    """
    ax2.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
             verticalalignment='center')

    plt.tight_layout()
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    plt.close()
