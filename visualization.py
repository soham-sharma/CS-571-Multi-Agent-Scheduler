# visualization.py
import matplotlib.pyplot as plt
import numpy as np


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

    def overlap(ts1, ts2):
        d1, d2 = time_slot_details[ts1], time_slot_details[ts2]
        common = set(d1["days"]) & set(d2["days"])
        if not common:
            return False
        def to_min(t):
            h, m = t.split(":")
            return int(h) * 60 + int(m)
        s1, s2 = to_min(d1["start_time"]), to_min(d2["start_time"])
        e1, e2 = s1 + d1["duration_min"], s2 + d2["duration_min"]
        return s1 < e2 and s2 < e1

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

                if overlap(tsi, tsj):
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
