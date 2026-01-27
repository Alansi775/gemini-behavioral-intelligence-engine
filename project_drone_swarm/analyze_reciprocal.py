#!/usr/bin/env python3
"""
Analyze multi-run reciprocal-sensing experiment
Compare against baseline (no reciprocal sensing) to detect emergence
"""

import json
from collections import defaultdict
from statistics import mean, variance

def load_jsonl(filename):
    """Load JSONL log file"""
    entries = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                entries.append(json.loads(line))
    except FileNotFoundError:
        return []
    return entries

def analyze_neighbor_distribution(entries):
    """Analyze neighbor count distribution"""
    neighbor_counts = defaultdict(int)
    avoidance_by_neighbors = defaultdict(lambda: {'total': 0, 'avoid': 0})
    
    for entry in entries:
        num_neighbors = len(entry['neighbors'])
        neighbor_counts[num_neighbors] += 1
        
        avoidance_by_neighbors[num_neighbors]['total'] += 1
        if entry['action'] == 'avoid_collision':
            avoidance_by_neighbors[num_neighbors]['avoid'] += 1
    
    return neighbor_counts, avoidance_by_neighbors

def analyze_spatial_dynamics(entries):
    """Detect spatial clustering patterns and oscillations"""
    drone_positions = defaultdict(list)
    
    for entry in entries:
        drone_id = entry['drone_id']
        pos = entry['position']
        drone_positions[drone_id].append((entry['time'], pos['x'], pos['y']))
    
    # Calculate average distance between agents at key timesteps
    clustering_at_times = {}
    for t in [100, 300, 500, 700, 900]:
        positions_at_t = []
        for drone_id, positions in drone_positions.items():
            for time, x, y in positions:
                if time == t:
                    positions_at_t.append((x, y))
        
        if len(positions_at_t) > 1:
            # Calculate average pairwise distance
            total_dist = 0
            count = 0
            for i in range(len(positions_at_t)):
                for j in range(i + 1, len(positions_at_t)):
                    x1, y1 = positions_at_t[i]
                    x2, y2 = positions_at_t[j]
                    dist = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
                    total_dist += dist
                    count += 1
            clustering_at_times[t] = total_dist / count if count > 0 else 0
    
    return clustering_at_times

def analyze_action_sequences(entries):
    """Detect temporal patterns in actions"""
    actions = [e['action'] for e in entries]
    action_runs = []
    
    current_action = actions[0]
    run_length = 1
    
    for action in actions[1:]:
        if action == current_action:
            run_length += 1
        else:
            action_runs.append((current_action, run_length))
            current_action = action
            run_length = 1
    
    action_runs.append((current_action, run_length))
    
    # Analyze run lengths
    avoid_runs = [r for a, r in action_runs if a == 'avoid_collision']
    move_runs = [r for a, r in action_runs if a == 'move_forward']
    
    return {
        'avoid_run_lengths': avoid_runs,
        'move_run_lengths': move_runs,
        'total_runs': len(action_runs)
    }

def detect_emergence_signatures(entries):
    """Look for signs of coordinated behavior that indicate emergence"""
    
    signatures = []
    
    # Signature 1: Multi-agent avoidance bursts
    # If many agents avoid simultaneously, suggests reactive coordination
    drone_actions = defaultdict(list)
    for entry in entries:
        drone_actions[entry['drone_id']].append((entry['time'], entry['action']))
    
    avoidance_concurrent = 0
    for t in range(100, 1000):
        agents_avoiding = 0
        for drone_id in drone_actions:
            for time, action in drone_actions[drone_id]:
                if time == t and action == 'avoid_collision':
                    agents_avoiding += 1
                    break
        if agents_avoiding >= 10:  # 10+ agents avoiding simultaneously
            avoidance_concurrent += 1
    
    if avoidance_concurrent > 50:
        signatures.append(f"[EMERGING] Synchronized avoidance events: {avoidance_concurrent} timesteps with 10+ agents avoiding simultaneously")
    
    # Signature 2: Neighbor count variance changes over time
    # Rising variance = clustering dynamics
    drone_neighbors_time = defaultdict(list)
    for entry in entries:
        t = entry['time']
        neighbors = len(entry['neighbors'])
        drone_neighbors_time[entry['drone_id']].append((t, neighbors))
    
    early_neighbor_counts = []
    late_neighbor_counts = []
    for drone_id in drone_neighbors_time:
        for t, n in drone_neighbors_time[drone_id]:
            if 0 <= t < 300:
                early_neighbor_counts.append(n)
            elif 700 <= t < 1000:
                late_neighbor_counts.append(n)
    
    if early_neighbor_counts and late_neighbor_counts:
        early_var = variance(early_neighbor_counts) if len(early_neighbor_counts) > 1 else 0
        late_var = variance(late_neighbor_counts) if len(late_neighbor_counts) > 1 else 0
        var_change = abs(late_var - early_var)
        
        if var_change > 0.5:
            signatures.append(f"[EMERGING] Neighbor variance shift: early={early_var:.2f}, late={late_var:.2f}, change={var_change:.2f}")
    
    # Signature 3: Oscillating cluster formation
    # Detect if neighbor counts show periodic patterns
    avg_neighbors_by_time = defaultdict(list)
    for entry in entries:
        t = entry['time']
        avg_neighbors_by_time[t].append(len(entry['neighbors']))
    
    neighbor_means = [mean(counts) for t, counts in sorted(avg_neighbors_by_time.items())]
    
    # Simple oscillation detection: count sign changes
    sign_changes = 0
    for i in range(1, len(neighbor_means) - 1):
        if (neighbor_means[i] - neighbor_means[i-1]) * (neighbor_means[i+1] - neighbor_means[i]) < 0:
            sign_changes += 1
    
    if sign_changes > 20:
        signatures.append(f"[EMERGING] Oscillatory clustering: {sign_changes} detected phase reversals")
    
    return signatures

def main():
    print("\n" + "="*70)
    print("RECIPROCAL SENSING EXPERIMENT ANALYSIS")
    print("Comparing baseline (no sensing) vs velocity-aware avoidance")
    print("="*70)
    
    baseline_files = [f"swarm_log_run{i}.jsonl" for i in range(3)]
    reciprocal_files = [f"swarm_log_reciprocal_run{i}.jsonl" for i in range(3)]
    
    # Load all data
    baseline_data = [load_jsonl(f) for f in baseline_files]
    reciprocal_data = [load_jsonl(f) for f in reciprocal_files]
    
    print("\n" + "="*70)
    print("BASELINE RESULTS (No Reciprocal Sensing)")
    print("="*70)
    
    baseline_avoidance_pcts = []
    for run_id, entries in enumerate(baseline_data):
        neighbor_dist, avoid_by_neighbors = analyze_neighbor_distribution(entries)
        action_seq = analyze_action_sequences(entries)
        
        total_avoid = sum(1 for e in entries if e['action'] == 'avoid_collision')
        avoidance_pct = (total_avoid / len(entries)) * 100
        baseline_avoidance_pcts.append(avoidance_pct)
        
        print(f"\nRun {run_id}:")
        print(f"  Avoidance frequency: {avoidance_pct:.1f}%")
        print(f"  Avg avoidance run length: {mean(action_seq['avoid_run_lengths']):.1f} timesteps")
    
    print(f"\nBaseline Avoidance (mean ± SD): {mean(baseline_avoidance_pcts):.1f}% ± {(variance(baseline_avoidance_pcts)**0.5):.2f}%")
    
    print("\n" + "="*70)
    print("RECIPROCAL SENSING RESULTS")
    print("="*70)
    
    reciprocal_avoidance_pcts = []
    emergence_found = False
    
    for run_id, entries in enumerate(reciprocal_data):
        neighbor_dist, avoid_by_neighbors = analyze_neighbor_distribution(entries)
        action_seq = analyze_action_sequences(entries)
        clustering = analyze_spatial_dynamics(entries)
        signatures = detect_emergence_signatures(entries)
        
        total_avoid = sum(1 for e in entries if e['action'] == 'avoid_collision')
        avoidance_pct = (total_avoid / len(entries)) * 100
        reciprocal_avoidance_pcts.append(avoidance_pct)
        
        print(f"\nRun {run_id}:")
        print(f"  Avoidance frequency: {avoidance_pct:.1f}%")
        print(f"  Avg avoidance run length: {mean(action_seq['avoid_run_lengths']):.1f} timesteps")
        print(f"  Clustering (avg pairwise distance):")
        for t, dist in sorted(clustering.items()):
            print(f"    t={t}: {dist:.2f}")
        
        if signatures:
            emergence_found = True
            print(f"  Emergence signatures detected:")
            for sig in signatures:
                print(f"    {sig}")
        else:
            print(f"  No emergence signatures detected")
    
    print(f"\nReciprocal Avoidance (mean ± SD): {mean(reciprocal_avoidance_pcts):.1f}% ± {(variance(reciprocal_avoidance_pcts)**0.5):.2f}%")
    
    print("\n" + "="*70)
    print("COMPARATIVE ANALYSIS")
    print("="*70)
    
    avoidance_diff = mean(reciprocal_avoidance_pcts) - mean(baseline_avoidance_pcts)
    print(f"\nAvoidance frequency change: {avoidance_diff:+.1f} percentage points")
    
    if abs(avoidance_diff) < 2:
        print("  → Minimal change in avoidance behavior")
    elif avoidance_diff > 5:
        print("  → Significantly increased avoidance (possible positive feedback)")
    elif avoidance_diff < -5:
        print("  → Significantly decreased avoidance (unexpected)")
    
    if emergence_found:
        print("\n✓ EMERGENCE SIGNATURES DETECTED")
        print("  Reciprocal sensing introduced feedback loops that triggered emergent behaviors")
    else:
        print("\n✗ NO EMERGENCE SIGNATURES DETECTED")
        print("  Reciprocal sensing alone was insufficient to cross emergence threshold")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    
    if emergence_found:
        print("\nHypothesis SUPPORTED: Velocity-aware avoidance creates feedback loops")
        print("Next step: Test local information integration (flocking) for stronger emergence")
    else:
        print("\nHypothesis UNSUPPORTED: Reciprocal sensing did not trigger emergence")
        print("Reason: Feedback is still local and instantaneous, lacks integration over time")
        print("Next step: Add flocking (neighbor velocity averaging) for coordinated motion")

if __name__ == "__main__":
    main()
