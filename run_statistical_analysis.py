#!/usr/bin/env python3
"""
Statistical Analysis Runner for MACSS

Runs the complete MACSS system multiple times with different random seeds
and collects statistics to evaluate robustness and consistency.

Usage:
    python run_statistical_analysis.py [num_trials]

Default: 10 trials
"""

import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from data_model import load_data
from csp_solver import find_initial_assignment
from negotiation import NegotiationProtocol
from objective import (
    calculate_total_cost,
    calculate_student_conflicts,
    calculate_professor_penalty,
    calculate_student_preference_penalty
)


def run_single_trial(data, trial_num, seed):
    """
    Run a single trial of the complete MACSS system.

    Returns a dictionary of metrics for this trial.
    """
    print(f"\n--- Trial {trial_num + 1} (seed={seed}) ---")

    # Run CSP solver
    print("  Solving CSP...")
    A0 = find_initial_assignment(data)
    if not A0:
        print("  FAILED: No CSP solution found")
        return None

    A0_norm = {c: {"time": v[0], "room": v[1]} for c, v in A0.items()}

    # Calculate A0 metrics
    A0_conflicts = calculate_student_conflicts(
        A0_norm, data["student_enrollments"], data["time_slot_details"]
    )
    A0_prof_penalty = calculate_professor_penalty(
        A0_norm, data["professor_preferences"], data["professors"],
        data["time_slot_details"], data["enrollments"]
    )
    A0_student_penalty = calculate_student_preference_penalty(
        A0_norm, data.get("student_preferences", {}),
        data["student_enrollments"], data["time_slot_details"]
    )
    A0_cost = calculate_total_cost(A0_norm, data)

    # Run negotiation
    print("  Running negotiation...")
    proto = NegotiationProtocol(A0, data, rng_seed=seed + 1000)
    final_sched, cost_history = proto.run()

    # Calculate final metrics
    final_conflicts = calculate_student_conflicts(
        final_sched, data["student_enrollments"], data["time_slot_details"]
    )
    final_prof_penalty = calculate_professor_penalty(
        final_sched, data["professor_preferences"], data["professors"],
        data["time_slot_details"], data["enrollments"]
    )
    final_student_penalty = calculate_student_preference_penalty(
        final_sched, data.get("student_preferences", {}),
        data["student_enrollments"], data["time_slot_details"]
    )
    final_cost = calculate_total_cost(final_sched, data)

    improvement = ((A0_cost - final_cost) / A0_cost * 100) if A0_cost > 0 else 0

    print(f"  Results: Conflicts {A0_conflicts}→{final_conflicts}, " +
          f"Cost {A0_cost:.1f}→{final_cost:.1f} ({improvement:.1f}% improvement)")

    return {
        "trial": trial_num,
        "seed": seed,
        "A0_conflicts": A0_conflicts,
        "A0_prof_penalty": A0_prof_penalty,
        "A0_student_penalty": A0_student_penalty,
        "A0_cost": A0_cost,
        "final_conflicts": final_conflicts,
        "final_prof_penalty": final_prof_penalty,
        "final_student_penalty": final_student_penalty,
        "final_cost": final_cost,
        "negotiation_rounds": len(cost_history) - 1,
        "improvement_percent": improvement,
        "cost_history": cost_history
    }


def plot_distributions(results, outfile="statistical_distributions.png"):
    """
    Plot distributions of key metrics across all trials.
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle("Statistical Analysis: Distribution of Metrics Across Trials", fontsize=14, fontweight='bold')

    # Extract data
    final_conflicts = [r["final_conflicts"] for r in results]
    final_costs = [r["final_cost"] for r in results]
    improvements = [r["improvement_percent"] for r in results]
    negotiation_rounds = [r["negotiation_rounds"] for r in results]
    prof_penalties = [r["final_prof_penalty"] for r in results]
    student_penalties = [r["final_student_penalty"] for r in results]

    # Plot 1: Final conflicts
    axes[0, 0].hist(final_conflicts, bins=max(5, len(set(final_conflicts))), edgecolor='black', color='steelblue')
    axes[0, 0].axvline(np.mean(final_conflicts), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(final_conflicts):.1f}')
    axes[0, 0].set_xlabel('Final Student Conflicts')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Student Conflicts Distribution')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    # Plot 2: Final total cost
    axes[0, 1].hist(final_costs, bins=10, edgecolor='black', color='coral')
    axes[0, 1].axvline(np.mean(final_costs), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(final_costs):.1f}')
    axes[0, 1].set_xlabel('Final Total Cost')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Total Cost Distribution')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    # Plot 3: Improvement percentage
    axes[0, 2].hist(improvements, bins=10, edgecolor='black', color='lightgreen')
    axes[0, 2].axvline(np.mean(improvements), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(improvements):.1f}%')
    axes[0, 2].set_xlabel('Improvement (%)')
    axes[0, 2].set_ylabel('Frequency')
    axes[0, 2].set_title('Cost Improvement Distribution')
    axes[0, 2].legend()
    axes[0, 2].grid(alpha=0.3)

    # Plot 4: Negotiation rounds
    axes[1, 0].hist(negotiation_rounds, bins=range(min(negotiation_rounds), max(negotiation_rounds) + 2),
                   edgecolor='black', color='orchid')
    axes[1, 0].axvline(np.mean(negotiation_rounds), color='red', linestyle='--', linewidth=2,
                      label=f'Mean: {np.mean(negotiation_rounds):.1f}')
    axes[1, 0].set_xlabel('Negotiation Rounds')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Convergence Speed Distribution')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    # Plot 5: Professor penalties
    axes[1, 1].hist(prof_penalties, bins=10, edgecolor='black', color='gold')
    axes[1, 1].axvline(np.mean(prof_penalties), color='red', linestyle='--', linewidth=2,
                      label=f'Mean: {np.mean(prof_penalties):.1f}')
    axes[1, 1].set_xlabel('Professor Penalty')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Professor Satisfaction Distribution')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)

    # Plot 6: Student penalties
    axes[1, 2].hist(student_penalties, bins=10, edgecolor='black', color='skyblue')
    axes[1, 2].axvline(np.mean(student_penalties), color='red', linestyle='--', linewidth=2,
                      label=f'Mean: {np.mean(student_penalties):.1f}')
    axes[1, 2].set_xlabel('Student Preference Penalty')
    axes[1, 2].set_ylabel('Frequency')
    axes[1, 2].set_title('Student Satisfaction Distribution')
    axes[1, 2].legend()
    axes[1, 2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Distribution plots saved to {outfile}")


def generate_report(results, outfile="statistical_report.json"):
    """
    Generate comprehensive statistical report.
    """
    # Calculate statistics
    metrics = {
        "final_conflicts": [r["final_conflicts"] for r in results],
        "final_cost": [r["final_cost"] for r in results],
        "improvement_percent": [r["improvement_percent"] for r in results],
        "negotiation_rounds": [r["negotiation_rounds"] for r in results],
        "final_prof_penalty": [r["final_prof_penalty"] for r in results],
        "final_student_penalty": [r["final_student_penalty"] for r in results]
    }

    report = {
        "num_trials": len(results),
        "statistics": {}
    }

    for metric_name, values in metrics.items():
        report["statistics"][metric_name] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "median": float(np.median(values))
        }

    # Save report
    with open(outfile, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Statistical report saved to {outfile}")

    # Print summary
    print("\n" + "=" * 60)
    print("STATISTICAL ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Number of trials: {len(results)}")
    print("\nKey Metrics (Mean ± Std):")
    print(f"  Final Conflicts:      {report['statistics']['final_conflicts']['mean']:.2f} ± {report['statistics']['final_conflicts']['std']:.2f}")
    print(f"  Final Cost:           {report['statistics']['final_cost']['mean']:.2f} ± {report['statistics']['final_cost']['std']:.2f}")
    print(f"  Improvement:          {report['statistics']['improvement_percent']['mean']:.2f}% ± {report['statistics']['improvement_percent']['std']:.2f}%")
    print(f"  Negotiation Rounds:   {report['statistics']['negotiation_rounds']['mean']:.2f} ± {report['statistics']['negotiation_rounds']['std']:.2f}")
    print(f"  Professor Penalty:    {report['statistics']['final_prof_penalty']['mean']:.2f} ± {report['statistics']['final_prof_penalty']['std']:.2f}")
    print(f"  Student Penalty:      {report['statistics']['final_student_penalty']['mean']:.2f} ± {report['statistics']['final_student_penalty']['std']:.2f}")
    print("=" * 60)

    return report


def main():
    parser = argparse.ArgumentParser(description="Run statistical analysis of MACSS")
    parser.add_argument("num_trials", nargs="?", type=int, default=10,
                       help="Number of trials to run (default: 10)")
    parser.add_argument("--input", default="input_synthetic.json",
                       help="Input data file (default: input_synthetic.json)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"MACSS Statistical Analysis")
    print(f"Running {args.num_trials} trials with different random seeds")
    print(f"{'='*60}")

    # Load data once
    print(f"\nLoading data from {args.input}...")
    data = load_data(args.input, "preferences.json")
    if not data:
        print("ERROR: Failed to load data")
        return

    # Run trials
    results = []
    base_seed = 12345
    for i in range(args.num_trials):
        seed = base_seed + i * 100
        result = run_single_trial(data, i, seed)
        if result:
            results.append(result)

    if not results:
        print("\nERROR: All trials failed!")
        return

    print(f"\n✓ Completed {len(results)}/{args.num_trials} successful trials")

    # Generate outputs
    print("\nGenerating analysis outputs...")
    plot_distributions(results, "statistical_distributions.png")
    report = generate_report(results, "statistical_report.json")

    print("\n✓ Statistical analysis complete!")
    print("\nOutput files:")
    print("  • statistical_report.json - Detailed statistics")
    print("  • statistical_distributions.png - Distribution plots")


if __name__ == "__main__":
    main()
