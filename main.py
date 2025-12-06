# main.py
import json
import argparse
from data_model import load_data
from csp_solver import find_initial_assignment
from negotiation import NegotiationProtocol
from objective import (
    calculate_total_cost,
    calculate_student_conflicts,
    calculate_professor_penalty,
    calculate_student_preference_penalty
)
from visualization import (
    plot_cost_history,
    plot_basic_comparison,
    plot_conflict_heatmap,
    plot_timetable_grid,
    plot_room_utilization
)

OUTPUT_A0 = "initial_schedule_A0.json"
OUTPUT_FINAL = "final_schedule_negotiated.json"


def normalize_schedule(raw):
    # Converts A0 raw JSON into internal dict format
    return {c: {"time": v[0], "room": v[1]} for c, v in raw.items()}


def print_basic_comparison(A0_sched, A_final_sched, data):
    # Computes all metrics for comparison
    sc0 = calculate_student_conflicts(A0_sched, data["student_enrollments"], data["time_slot_details"])
    scf = calculate_student_conflicts(A_final_sched, data["student_enrollments"], data["time_slot_details"])

    pp0 = calculate_professor_penalty(
        A0_sched, data["professor_preferences"], data["professors"],
        data["time_slot_details"], data["enrollments"]
    )
    ppf = calculate_professor_penalty(
        A_final_sched, data["professor_preferences"], data["professors"],
        data["time_slot_details"], data["enrollments"]
    )

    sp0 = calculate_student_preference_penalty(
        A0_sched, data.get("student_preferences", {}),
        data["student_enrollments"], data["time_slot_details"]
    )
    spf = calculate_student_preference_penalty(
        A_final_sched, data.get("student_preferences", {}),
        data["student_enrollments"], data["time_slot_details"]
    )

    c0 = calculate_total_cost(A0_sched, data)
    cf = calculate_total_cost(A_final_sched, data)

    print("\n--- Comparison (A0 vs Final) ---")
    print(f"Student conflicts:        {sc0} → {scf}")
    print(f"Student pref penalty:     {sp0:.2f} → {spf:.2f}")
    print(f"Professor penalty:        {pp0:.2f} → {ppf:.2f}")
    print(f"Total cost:               {c0:.2f} → {cf:.2f}")
    print(f"Improvement:              {((c0-cf)/c0*100) if c0 > 0 else 0:.1f}%")

    return sc0, scf, pp0, ppf, sp0, spf


def main():
    parser = argparse.ArgumentParser(description="Run MACSS Complete (CSP + Negotiation)")
    parser.add_argument(
        "input_file",
        nargs="?",
        default="input_synthetic.json",
        help="Path to input JSON"
    )
    args = parser.parse_args()

    data = load_data(args.input_file)
    if data is None:
        return

    # Run CSP for initial schedule
    print("\nSolving CSP...")
    A0 = find_initial_assignment(data)
    if not A0:
        print("No feasible CSP schedule found.")
        return

    with open(OUTPUT_A0, "w") as f:
        json.dump(A0, f, indent=4)
    print("Initial schedule saved to", OUTPUT_A0)

    # Run negotiation
    print("\nRunning negotiation...")
    proto = NegotiationProtocol(A0, data)
    final_sched, cost_history = proto.run()

    # Save final schedule
    final_out = {c: [v["time"], v["room"]] for c, v in final_sched.items()}
    with open(OUTPUT_FINAL, "w") as f:
        json.dump(final_out, f, indent=4)
    print("Final schedule saved to", OUTPUT_FINAL)

    # Normalize
    A0_norm = normalize_schedule(A0)
    A_final_norm = final_sched

    # Print comparison results
    sc0, scf, pp0, ppf, sp0, spf = print_basic_comparison(A0_norm, A_final_norm, data)

    # Generate plots
    print("\nGenerating visualization files...")
    plot_cost_history(cost_history, "cost_history.png")
    plot_basic_comparison(sc0, pp0, scf, ppf, "comparison.png")

    # Generate new visualizations
    print("Creating timetable grids...")
    plot_timetable_grid(A0_norm, data, title="Initial Schedule (A0)", outfile="timetable_A0.png")
    plot_timetable_grid(A_final_norm, data, title="Final Schedule (After Negotiation)", outfile="timetable_final.png")

    print("Creating room utilization analysis...")
    plot_room_utilization(A_final_norm, data, outfile="room_utilization.png")

    # Optional conflict heatmap
    # plot_conflict_heatmap(A_final_norm, data["student_enrollments"], data["time_slot_details"], "final_heatmap.png")

    print("\n✓ All visualization outputs saved:")
    print("  • cost_history.png - Cost improvement over negotiation rounds")
    print("  • comparison.png - A0 vs Final metrics comparison")
    print("  • timetable_A0.png - Initial schedule grid")
    print("  • timetable_final.png - Final schedule grid")
    print("  • room_utilization.png - Room utilization analysis")
    print("\n✓ Schedule files saved:")
    print(f"  • {OUTPUT_A0} - Initial CSP solution")
    print(f"  • {OUTPUT_FINAL} - Final negotiated schedule")


if __name__ == "__main__":
    main()
