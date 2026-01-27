#!/usr/bin/env python3
"""
Three-regime comparative analysis:
1. Baseline (no feedback)
2. Reciprocal Sensing (velocity feedback)  
3. Flocking (velocity feedback + information integration)

Detect whether flocking produces higher-order emergent phenomena
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

def analyze_direction_coherence(entries):
    """Measure whether agents are moving in aligned directions"""
    drone_directions = defaultdict(list)
    
    # We infer direction from position changes over time
    drone_positions = defaultdict(list)
    for entry in entries:
        drone_id = entry['drone_id']
        t = entry['time']
        pos = entry['position']
        drone_positions[drone_id].append((t, pos['x'], pos['y']))
    
    # Calculate heading for each drone over time windows
    direction_consistency = []
    for t_window in range(0, 1000, 100):
        drone_headings = []
        for drone_id, positions in drone_positions.items():
            valid_positions = [(t, x, y) for t, x, y in positions 
                             if t_window <= t < t_window + 100]
            if len(valid_positions) > 2:
                # Calculate dominant heading
                dx = valid_positions[-1][1] - valid_positions[0][1]
                dy = valid_positions[-1][2] - valid_positions[0][2]
                if abs(dx) + abs(dy) > 0.1:  # Significant movement
                    import math
                    heading = math.atan2(dy, dx)
                    drone_headings.append(heading)
        
        if drone_headings:
            # Check variance in headings - low variance = aligned
            # Circular statistics: check concentration
            import math
            cos_sum = sum(math.cos(h) for h in drone_headings)
            sin_sum = sum(math.sin(h) for h in drone_headings)
            r = (cos_sum**2 + sin_sum**2)**0.5 / len(drone_headings)
            direction_consistency.append(r)
    
    return mean(direction_consistency) if direction_consistency else 0

def analyze_formation_stability(entries):
    """Detect whether agents form stable spatial patterns"""
    drone_positions = defaultdict(list)
    
    for entry in entries:
        drone_id = entry['drone_id']
        pos = entry['position']
        drone_positions[drone_id].append((entry['time'], pos['x'], pos['y']))
    
    # Track neighbor consistency over time
    same_neighbors_count = 0
    total_checks = 0
    
    for t in range(100, 1000, 50):
        agents_t1 = [(positions[0][1], positions[0][2]) for drone_id, positions in drone_positions.items()
                    for time, x, y in positions if time == t]
        agents_t2 = [(positions[0][1], positions[0][2]) for drone_id, positions in drone_positions.items()
                    for time, x, y in positions if time == t + 1]
        
        if len(agents_t1) >= 5 and len(agents_t2) >= 5:
            # Find closest neighbors at t1 and t2
            persistent_pairs = 0
            import math
            for x1, y1 in agents_t1[:5]:
                # Find nearest neighbor at t2
                nearest_dist = float('inf')
                for x2, y2 in agents_t2:
                    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    if dist < nearest_dist:
                        nearest_dist = dist
                
                if nearest_dist < 10:  # Reasonable distance for persistent neighbor
                    persistent_pairs += 1
            
            same_neighbors_count += persistent_pairs / 5
            total_checks += 1
    
    return same_neighbors_count / total_checks if total_checks > 0 else 0

def analyze_polarization(entries):
    """Detect whether agents move in groups with opposite directions (polarization)"""
    drone_positions = defaultdict(list)
    
    for entry in entries:
        drone_id = entry['drone_id']
        pos = entry['position']
        drone_positions[drone_id].append((entry['time'], pos['x'], pos['y']))
    
    # Check if agents separate into distinct groups
    groups_detected = 0
    for t in [250, 500, 750]:
        positions_at_t = []
        for drone_id, positions in drone_positions.items():
            for time, x, y in positions:
                if time == t:
                    positions_at_t.append((x, y))
        
        if len(positions_at_t) > 10:
            # Simple clustering: check if some agents are far from grid center
            import math
            grid_center = 15
            center_dist = [math.sqrt((x - grid_center)**2 + (y - grid_center)**2) 
                          for x, y in positions_at_t]
            
            far_agents = len([d for d in center_dist if d > 12])
            if far_agents > len(positions_at_t) * 0.4:  # 40%+ far from center
                groups_detected += 1
    
    return groups_detected / 3

def analyze_cascade_events(entries):
    """Detect propagating events (one agent's action triggers neighbors)"""
    # Track when many agents change action simultaneously
    cascades = 0
    
    for t in range(1, 1000):
        actions_at_t = []
        actions_at_t_minus_1 = []
        
        for entry in entries:
            if entry['time'] == t:
                actions_at_t.append(entry['action'])
            elif entry['time'] == t - 1:
                actions_at_t_minus_1.append(entry['action'])
        
        if len(actions_at_t) == 30 and len(actions_at_t_minus_1) == 30:
            # Count agents that changed action
            changed = 0
            for i in range(30):
                if actions_at_t[i] != actions_at_t_minus_1[i]:
                    changed += 1
            
            if changed >= 15:  # 50%+ of agents change action
                cascades += 1
    
    return cascades

def main():
    print("\n" + "="*70)
    print("THREE-REGIME COMPARATIVE EMERGENCE ANALYSIS")
    print("="*70)
    
    # Load all regime data
    baseline = [load_jsonl(f"swarm_log_run{i}.jsonl") for i in range(3)]
    reciprocal = [load_jsonl(f"swarm_log_reciprocal_run{i}.jsonl") for i in range(3)]
    flocking = [load_jsonl(f"swarm_log_flocking_run{i}.jsonl") for i in range(3)]
    
    regimes = {
        'Baseline (No Feedback)': baseline,
        'Reciprocal Sensing (Velocity Feedback)': reciprocal,
        'Flocking (Velocity + Direction Integration)': flocking
    }
    
    metrics = {}
    
    for regime_name, regime_data in regimes.items():
        print(f"\n{'='*70}")
        print(f"REGIME: {regime_name}")
        print(f"{'='*70}")
        
        direction_coherence = []
        formation_stability = []
        polarization = []
        cascade_events = []
        avoidance_pcts = []
        
        for run_id, entries in enumerate(regime_data):
            # Compute metrics
            dir_coh = analyze_direction_coherence(entries)
            form_stab = analyze_formation_stability(entries)
            polar = analyze_polarization(entries)
            cascades = analyze_cascade_events(entries)
            avoid_pct = (sum(1 for e in entries if e['action'] == 'avoid_collision') / len(entries)) * 100
            
            direction_coherence.append(dir_coh)
            formation_stability.append(form_stab)
            polarization.append(polar)
            cascade_events.append(cascades)
            avoidance_pcts.append(avoid_pct)
            
            print(f"\nRun {run_id}:")
            print(f"  Direction Coherence: {dir_coh:.3f} (0=random, 1=aligned)")
            print(f"  Formation Stability: {form_stab:.3f} (0=chaotic, 1=stable)")
            print(f"  Polarization: {polar:.3f} (0=no groups, 1=separated)")
            print(f"  Cascade Events: {cascades} (synchronous group actions)")
            print(f"  Avoidance Frequency: {avoid_pct:.1f}%")
        
        # Regime summary
        print(f"\nRegime Summary:")
        print(f"  Direction Coherence (mean): {mean(direction_coherence):.3f}")
        print(f"  Formation Stability (mean): {mean(formation_stability):.3f}")
        print(f"  Polarization (mean): {mean(polarization):.3f}")
        print(f"  Cascade Events (mean): {mean(cascade_events):.1f}")
        print(f"  Avoidance Frequency (mean): {mean(avoidance_pcts):.1f}%")
        
        metrics[regime_name] = {
            'direction_coherence': mean(direction_coherence),
            'formation_stability': mean(formation_stability),
            'polarization': mean(polarization),
            'cascade_events': mean(cascade_events),
            'avoidance': mean(avoidance_pcts)
        }
    
    # Comparative analysis
    print(f"\n{'='*70}")
    print("EMERGENCE SIGNATURE COMPARISON")
    print(f"{'='*70}")
    
    print("\n✓ Direction Coherence (higher = more coordinated movement):")
    for regime in regimes.keys():
        val = metrics[regime]['direction_coherence']
        print(f"  {regime}: {val:.3f}")
    
    print("\n✓ Formation Stability (higher = agents maintain spatial patterns):")
    for regime in regimes.keys():
        val = metrics[regime]['formation_stability']
        print(f"  {regime}: {val:.3f}")
    
    print("\n✓ Polarization (higher = agents separate into groups):")
    for regime in regimes.keys():
        val = metrics[regime]['polarization']
        print(f"  {regime}: {val:.3f}")
    
    print("\n✓ Cascade Events (higher = synchronized group behavior):")
    for regime in regimes.keys():
        val = metrics[regime]['cascade_events']
        print(f"  {regime}: {val:.1f}")
    
    # Final determination
    print(f"\n{'='*70}")
    print("EMERGENCE VERDICT")
    print(f"{'='*70}")
    
    baseline_coherence = metrics['Baseline (No Feedback)']['direction_coherence']
    flocking_coherence = metrics['Flocking (Velocity + Direction Integration)']['direction_coherence']
    
    # Compare flocking to reciprocal
    reciprocal_stability = metrics['Reciprocal Sensing (Velocity Feedback)']['formation_stability']
    flocking_stability = metrics['Flocking (Velocity + Direction Integration)']['formation_stability']
    
    reciprocal_cascades = metrics['Reciprocal Sensing (Velocity Feedback)']['cascade_events']
    flocking_cascades = metrics['Flocking (Velocity + Direction Integration)']['cascade_events']
    
    print(f"\nFlocking vs Reciprocal Sensing:")
    if flocking_coherence > baseline_coherence:
        print(f"  ✓ FLOCKING ENABLES COORDINATED MOTION (coherence={flocking_coherence:.3f} vs baseline {baseline_coherence:.3f})")
    else:
        print(f"  ✗ Flocking does not improve direction alignment")
    
    if flocking_cascades < reciprocal_cascades - 5:
        print(f"  ✓ FLOCKING REDUCES CHAOTIC CASCADES (cascades={flocking_cascades:.1f} vs reciprocal {reciprocal_cascades:.1f})")
        print(f"     → Suggests more organized, less reactive behavior")
    else:
        print(f"  ~ Flocking cascade patterns similar to reciprocal sensing")
    
    print(f"\nRegime Hierarchy of Emergence:")
    print(f"  1. Baseline (No Feedback): Rule-driven, minimal coordination")
    print(f"     - Direction coherence: {metrics['Baseline (No Feedback)']['direction_coherence']:.3f}")
    print(f"     - Cascade events: {metrics['Baseline (No Feedback)']['cascade_events']:.1f}")
    print(f"\n  2. Reciprocal Sensing (Velocity Feedback): Positive feedback, increased reactivity")
    print(f"     - Direction coherence: {metrics['Reciprocal Sensing (Velocity Feedback)']['direction_coherence']:.3f}")
    print(f"     - Cascade events: {metrics['Reciprocal Sensing (Velocity Feedback)']['cascade_events']:.1f}")
    print(f"\n  3. Flocking (Velocity + Direction Integration): Information integration")
    print(f"     - Direction coherence: {metrics['Flocking (Velocity + Direction Integration)']['direction_coherence']:.3f}")
    print(f"     - Cascade events: {metrics['Flocking (Velocity + Direction Integration)']['cascade_events']:.1f}")
    print(f"     - Avoidance frequency: {metrics['Flocking (Velocity + Direction Integration)']['avoidance']:.1f}%")

if __name__ == "__main__":
    main()
