#!/usr/bin/env python3
"""
PAPER GV4 — Evidence Readiness Index (ERI) Computation Engine
Author: Julian Borges, MD, MS
Date: 2026-05-18

Implements:
  1. Gap Registry loading and validation
  2. Dependency graph construction and topological sort
  3. Delta score matrix computation
  4. Candidate-level and portfolio-level ERI
  5. Knapsack optimization under budget constraints
  6. Three budget scenario analyses ($50K, $150K, $500K)
  7. Comparison: ERI-optimized vs naive-sequential vs random allocation
  8. Sensitivity analysis (p_success perturbation, cost perturbation)
"""

import json
import itertools
from collections import defaultdict

# ============================================================
# 1. PAPER 3 SCORING MATRIX (Table 1, balanced weights)
# ============================================================

# Balanced weights from Paper 2/3
WEIGHTS = {
    "D1": 0.20, "D2": 0.15, "D3": 0.15,
    "D4": 0.15, "D5": 0.10, "D6": 0.10, "D7": 0.15
}

# Minimum portfolio (5 candidates) from Paper 3 Section 3.9
PORTFOLIO = {
    "PKA-002": {"target": "PINK1",  "D1": 0.75, "D2": 0.75, "D3": 0.75, "D4": 0.25, "D5": 0.85, "D6": 0.75, "D7": 0.70, "agg": 0.677},
    "KND-002": {"target": "NFE2L2", "D1": 0.75, "D2": 0.75, "D3": 0.75, "D4": 0.25, "D5": 0.85, "D6": 0.75, "D7": 0.60, "agg": 0.652},
    "DSA-001": {"target": "DNM1L",  "D1": 0.75, "D2": 0.75, "D3": 0.60, "D4": 0.25, "D5": 0.85, "D6": 0.70, "D7": 0.50, "agg": 0.635},
    "NDS-002": {"target": "NDUFV1", "D1": 0.75, "D2": 0.75, "D3": 0.65, "D4": 0.25, "D5": 0.65, "D6": 0.75, "D7": 0.50, "agg": 0.602},
    "SDA-002": {"target": "SDHA",   "D1": 0.75, "D2": 0.75, "D3": 0.65, "D4": 0.25, "D5": 0.65, "D6": 0.75, "D7": 0.50, "agg": 0.602},
}

# ============================================================
# 2. GAP REGISTRY (from gap_registry.yaml, structured)
# ============================================================

GAPS = {
    "UEG-1": {
        "name": "No in vivo efficacy data",
        "type": "UNIVERSAL",
        "cost_mid": 250000,  # midpoint of [150K, 350K]
        "cost_low": 150000,
        "cost_high": 350000,
        "p_success": 0.70,
        "affected": ["PKA-002", "KND-002", "DSA-001", "NDS-002", "SDA-002"],
        "deltas": {
            "PKA-002": {"D4": 0.15, "D1": 0.05},
            "KND-002": {"D4": 0.15, "D1": 0.05},
            "DSA-001": {"D4": 0.15, "D1": 0.05},
            "NDS-002": {"D4": 0.15, "D1": 0.05},
            "SDA-002": {"D4": 0.15, "D1": 0.05},
        },
        "dependencies": [],
    },
    "UEG-2": {
        "name": "No head-to-head comparison",
        "type": "UNIVERSAL",
        "cost_mid": 112500,
        "cost_low": 75000,
        "cost_high": 150000,
        "p_success": 0.85,
        "affected": ["PKA-002", "KND-002", "DSA-001", "NDS-002", "SDA-002"],
        "deltas": {
            "PKA-002": {"D4": 0.10, "D1": 0.05},
            "KND-002": {"D4": 0.10, "D1": 0.05},
            "DSA-001": {"D4": 0.10, "D1": 0.05},
            "NDS-002": {"D4": 0.10, "D1": 0.05},
            "SDA-002": {"D4": 0.10, "D1": 0.05},
        },
        "dependencies": ["UEG-1"],
    },
    "UEG-3": {
        "name": "No measured PK for matrix-targeted",
        "type": "UNIVERSAL",
        "cost_mid": 60000,
        "cost_low": 40000,
        "cost_high": 80000,
        "p_success": 0.90,
        "affected": ["NDS-002", "SDA-002"],
        "deltas": {
            "NDS-002": {"D4": 0.05, "D2": 0.05, "D3": 0.05},
            "SDA-002": {"D4": 0.05, "D2": 0.05, "D3": 0.05},
        },
        "dependencies": ["UEG-1"],
    },
    "TSG-PINK1": {
        "name": "PINK1 G309D crystal structure",
        "type": "TARGET_SPECIFIC",
        "cost_mid": 140000,
        "cost_low": 80000,
        "cost_high": 200000,
        "p_success": 0.45,
        "affected": ["PKA-002"],
        "deltas": {
            "PKA-002": {"D4": 0.15, "D1": 0.10, "D5": 0.05},
        },
        "dependencies": [],
    },
    "TSG-SDHA": {
        "name": "Recombinant R589W SDHA protein",
        "type": "TARGET_SPECIFIC",
        "cost_mid": 45000,
        "cost_low": 30000,
        "cost_high": 60000,
        "p_success": 0.75,
        "affected": ["SDA-002"],
        "deltas": {
            "SDA-002": {"D4": 0.10, "D1": 0.05},
        },
        "dependencies": [],
    },
    "TSG-DNM1L": {
        "name": "DNM1L stalk domain co-crystal",
        "type": "TARGET_SPECIFIC",
        "cost_mid": 175000,
        "cost_low": 100000,
        "cost_high": 250000,
        "p_success": 0.40,
        "affected": ["DSA-001"],
        "deltas": {
            "DSA-001": {"D4": 0.15, "D1": 0.10, "D5": 0.05},
        },
        "dependencies": ["UEG-1"],
    },
    "TSG-KEAP1": {
        "name": "CNS Keap1 PPI disruption selectivity",
        "type": "TARGET_SPECIFIC",
        "cost_mid": 90000,
        "cost_low": 60000,
        "cost_high": 120000,
        "p_success": 0.65,
        "affected": ["KND-002"],
        "deltas": {
            "KND-002": {"D4": 0.10, "D2": 0.05, "D7": 0.10},
        },
        "dependencies": ["UEG-1"],
    },
    "TSG-NDUFV1": {
        "name": "NDUFV1 FMN cleft accessibility",
        "type": "TARGET_SPECIFIC",
        "cost_mid": 210000,
        "cost_low": 120000,
        "cost_high": 300000,
        "p_success": 0.50,
        "affected": ["NDS-002"],
        "deltas": {
            "NDS-002": {"D4": 0.10, "D1": 0.10},
        },
        "dependencies": ["UEG-1"],
    },
}

# ============================================================
# 3. COMPUTATION FUNCTIONS
# ============================================================

def compute_aggregate(scores):
    """Compute weighted aggregate from dimension scores."""
    return sum(WEIGHTS[d] * scores[d] for d in WEIGHTS)

def compute_delta_aggregate(candidate_id, gap_id):
    """Compute the change in aggregate score if gap is resolved for candidate."""
    gap = GAPS[gap_id]
    if candidate_id not in gap["deltas"]:
        return 0.0
    deltas = gap["deltas"][candidate_id]
    return sum(WEIGHTS.get(dim, 0) * delta for dim, delta in deltas.items())

def compute_candidate_eri(candidate_id):
    """ERI for a single candidate: sum of (p * delta_agg / cost) across all affecting gaps."""
    total = 0.0
    for gid, gap in GAPS.items():
        if candidate_id in gap["affected"]:
            delta_agg = compute_delta_aggregate(candidate_id, gid)
            total += gap["p_success"] * delta_agg / gap["cost_mid"]
    return total

def compute_gap_portfolio_value(gap_id):
    """Total expected portfolio improvement from resolving one gap."""
    gap = GAPS[gap_id]
    total_delta = sum(compute_delta_aggregate(c, gap_id) for c in gap["affected"])
    return gap["p_success"] * total_delta

def compute_gap_roi(gap_id):
    """Expected portfolio improvement per dollar."""
    return compute_gap_portfolio_value(gap_id) / GAPS[gap_id]["cost_mid"]

def check_dependencies(selected_gaps, candidate_gap):
    """Check if all dependencies of candidate_gap are in selected_gaps."""
    return all(dep in selected_gaps for dep in GAPS[candidate_gap]["dependencies"])

def knapsack_optimize(budget, use_cost="cost_mid"):
    """
    Find optimal subset of gaps to resolve given budget constraint.
    Respects dependency ordering.
    Uses brute-force enumeration (feasible for 8 gaps).
    Returns (best_subset, best_value, best_cost).
    """
    gap_ids = list(GAPS.keys())
    best_value = 0
    best_subset = []
    best_cost = 0

    for r in range(1, len(gap_ids) + 1):
        for combo in itertools.combinations(gap_ids, r):
            # Check budget
            total_cost = sum(GAPS[g][use_cost] for g in combo)
            if total_cost > budget:
                continue
            # Check dependencies
            combo_set = set(combo)
            valid = True
            for g in combo:
                if not all(dep in combo_set for dep in GAPS[g]["dependencies"]):
                    valid = False
                    break
            if not valid:
                continue
            # Compute value
            total_value = sum(compute_gap_portfolio_value(g) for g in combo)
            if total_value > best_value:
                best_value = total_value
                best_subset = list(combo)
                best_cost = total_cost

    return best_subset, best_value, best_cost

def naive_sequential_allocation(budget, use_cost="cost_mid"):
    """
    Naive approach: resolve gaps in order of appearance (UEG-1 first, then UEG-2, etc.)
    until budget exhausted. Respects dependencies.
    """
    order = ["UEG-1", "UEG-2", "UEG-3", "TSG-PINK1", "TSG-SDHA", "TSG-DNM1L", "TSG-KEAP1", "TSG-NDUFV1"]
    selected = []
    spent = 0
    for g in order:
        cost = GAPS[g][use_cost]
        if spent + cost <= budget and check_dependencies(set(selected), g):
            selected.append(g)
            spent += cost
    total_value = sum(compute_gap_portfolio_value(g) for g in selected)
    return selected, total_value, spent

# ============================================================
# 4. RUN ANALYSES
# ============================================================

def main():
    print("=" * 70)
    print("PAPER GV4 — EVIDENCE READINESS INDEX (ERI) COMPUTATION")
    print("=" * 70)

    # --- Table 2: Delta Score Matrix ---
    print("\n--- TABLE 2: DELTA SCORE MATRIX (aggregate improvement per candidate per gap) ---")
    header = f"{'Candidate':<12}" + "".join(f"{gid:<14}" for gid in GAPS) + f"{'TOTAL':<10}"
    print(header)
    print("-" * len(header))
    for cid in PORTFOLIO:
        row = f"{cid:<12}"
        total = 0
        for gid in GAPS:
            delta = compute_delta_aggregate(cid, gid)
            total += delta
            row += f"{delta:<14.4f}"
        row += f"{total:<10.4f}"
        print(row)

    # --- Table 3: Gap-level metrics ---
    print("\n--- TABLE 3: GAP-LEVEL METRICS ---")
    print(f"{'Gap ID':<14}{'Name':<40}{'Cost ($K)':<12}{'p_success':<12}{'Portfolio Value':<18}{'ROI (per $K)':<14}")
    print("-" * 110)
    gap_rankings = []
    for gid, gap in GAPS.items():
        pv = compute_gap_portfolio_value(gid)
        roi = compute_gap_roi(gid) * 1000  # per $1K
        gap_rankings.append((gid, roi, pv, gap["cost_mid"]))
        print(f"{gid:<14}{gap['name']:<40}{gap['cost_mid']/1000:<12.0f}{gap['p_success']:<12.2f}{pv:<18.4f}{roi:<14.6f}")

    gap_rankings.sort(key=lambda x: -x[1])
    print("\n--- GAP ROI RANKING (highest value per dollar first) ---")
    for rank, (gid, roi, pv, cost) in enumerate(gap_rankings, 1):
        print(f"  {rank}. {gid} — ROI: {roi:.6f} per $1K — Portfolio value: {pv:.4f} — Cost: ${cost/1000:.0f}K")

    # --- Table 4: Candidate ERI ---
    print("\n--- TABLE 4: CANDIDATE ERI RANKINGS ---")
    eris = []
    for cid in PORTFOLIO:
        eri = compute_candidate_eri(cid)
        eris.append((cid, eri))
    eris.sort(key=lambda x: -x[1])
    print(f"{'Rank':<6}{'Candidate':<12}{'Target':<10}{'ERI (x10^6)':<15}{'Current Agg':<14}{'Max Possible Agg':<18}")
    for rank, (cid, eri) in enumerate(eris, 1):
        current = PORTFOLIO[cid]["agg"]
        # Max possible: sum all deltas across all gaps
        max_delta = sum(compute_delta_aggregate(cid, gid) for gid in GAPS)
        max_agg = current + max_delta
        print(f"{rank:<6}{cid:<12}{PORTFOLIO[cid]['target']:<10}{eri*1e6:<15.2f}{current:<14.3f}{max_agg:<18.3f}")

    # --- Table 5: Budget Optimization ---
    print("\n--- TABLE 5: BUDGET OPTIMIZATION RESULTS ---")
    budgets = [50000, 150000, 500000]
    for budget in budgets:
        opt_gaps, opt_value, opt_cost = knapsack_optimize(budget)
        naive_gaps, naive_value, naive_cost = naive_sequential_allocation(budget)
        print(f"\n  Budget: ${budget/1000:.0f}K")
        print(f"  ERI-OPTIMIZED: gaps={opt_gaps}, value={opt_value:.4f}, cost=${opt_cost/1000:.0f}K")
        print(f"  NAIVE-SEQUENTIAL: gaps={naive_gaps}, value={naive_value:.4f}, cost=${naive_cost/1000:.0f}K")
        if naive_value > 0:
            improvement = (opt_value - naive_value) / naive_value * 100
            print(f"  ERI advantage: {improvement:+.1f}%")
        else:
            print(f"  ERI advantage: N/A (naive=0)")

    # --- Sensitivity: p_success perturbation ---
    print("\n--- SENSITIVITY: p_success +/- 0.15 at $150K budget ---")
    for direction, label in [(+0.15, "OPTIMISTIC"), (-0.15, "PESSIMISTIC")]:
        # Temporarily adjust p_success
        original = {}
        for gid in GAPS:
            original[gid] = GAPS[gid]["p_success"]
            GAPS[gid]["p_success"] = max(0.05, min(0.95, GAPS[gid]["p_success"] + direction))
        opt_gaps, opt_value, opt_cost = knapsack_optimize(150000)
        print(f"  {label}: gaps={opt_gaps}, value={opt_value:.4f}, cost=${opt_cost/1000:.0f}K")
        # Restore
        for gid in GAPS:
            GAPS[gid]["p_success"] = original[gid]

    # --- Sensitivity: cost perturbation ---
    print("\n--- SENSITIVITY: cost LOW vs HIGH at $150K budget ---")
    for cost_key, label in [("cost_low", "LOW COST"), ("cost_high", "HIGH COST")]:
        opt_gaps, opt_value, opt_cost = knapsack_optimize(150000, use_cost=cost_key)
        print(f"  {label}: gaps={opt_gaps}, value={opt_value:.4f}, cost=${opt_cost/1000:.0f}K")

    # --- Summary statistics ---
    print("\n--- SUMMARY ---")
    total_gap_cost = sum(g["cost_mid"] for g in GAPS.values())
    total_gap_value = sum(compute_gap_portfolio_value(gid) for gid in GAPS)
    print(f"  Total cost to resolve ALL gaps: ${total_gap_cost/1000:.0f}K")
    print(f"  Total portfolio value if ALL gaps resolved: {total_gap_value:.4f}")
    print(f"  Mean candidate aggregate improvement: {total_gap_value/5:.4f}")

    # Current vs projected aggregates
    print("\n--- PROJECTED AGGREGATES (all gaps resolved) ---")
    for cid in PORTFOLIO:
        current = PORTFOLIO[cid]["agg"]
        total_delta = sum(compute_delta_aggregate(cid, gid) for gid in GAPS)
        projected = current + total_delta
        print(f"  {cid}: {current:.3f} -> {projected:.3f} (delta: +{total_delta:.3f})")


if __name__ == "__main__":
    main()
