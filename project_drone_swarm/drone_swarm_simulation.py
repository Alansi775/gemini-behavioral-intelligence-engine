import json
import random
import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Drone:
    """Represents a single drone in the swarm"""
    id: int
    x: float
    y: float
    battery: float  # 0-100%
    velocity: float  # units per timestep
    direction: float  # radians, heading direction
    
    def distance_to(self, other: 'Drone') -> float:
        """Calculate Euclidean distance to another drone"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class DroneSwarm:
    """Manages the drone swarm simulation"""
    
    def __init__(self, num_drones: int = 5, grid_size: int = 100):
        self.num_drones = num_drones
        self.grid_size = grid_size
        self.timestep = 0
        self.drones: List[Drone] = []
        self.log_file = "swarm_log.jsonl"
        
        # Configuration
        self.battery_drain_rate = 0.1  # battery % per timestep
        self.low_battery_threshold = 20  # %
        self.collision_distance = 5  # units
        self.max_velocity = 2.0  # units per timestep
        self.speed_reduction_factor = 0.5  # when low battery
        
        # Initialize drones
        self._initialize_drones()
        
        # Clear log file
        with open(self.log_file, 'w') as f:
            pass
    
    def _initialize_drones(self):
        """Create drones at random positions with random directions"""
        for i in range(self.num_drones):
            drone = Drone(
                id=i,
                x=random.uniform(0, self.grid_size),
                y=random.uniform(0, self.grid_size),
                battery=100.0,
                velocity=self.max_velocity,
                direction=random.uniform(0, 2 * math.pi)  # random initial heading
            )
            self.drones.append(drone)
    
    def _get_neighbors(self, drone: Drone) -> List[int]:
        """Get IDs of drones within collision distance"""
        neighbors = []
        for other in self.drones:
            if other.id != drone.id:
                if drone.distance_to(other) < self.collision_distance:
                    neighbors.append(other.id)
        return neighbors
    
    def _get_neighbor_velocity(self, drone: Drone, neighbor_id: int) -> float:
        """Get approach speed of neighbor (positive = approaching)"""
        neighbor = self.drones[neighbor_id]
        # Calculate relative velocity: negative = approaching, positive = receding
        dx = neighbor.x - drone.x
        dy = neighbor.y - drone.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist == 0:
            return 0
        
        # Estimate approach speed as change in distance per timestep
        # For this model, we use neighbor velocity in direction toward us
        approach_speed = neighbor.velocity  # simplified: all have same speed
        return approach_speed
    
    def _get_average_neighbor_direction(self, drone: Drone, neighbor_ids: list) -> float:
        """Get average heading direction of neighbors (FLOCKING RULE)"""
        if not neighbor_ids:
            return drone.direction
        
        # Sum up direction vectors from neighbors
        sum_x = 0
        sum_y = 0
        for neighbor_id in neighbor_ids:
            neighbor = self.drones[neighbor_id]
            sum_x += math.cos(neighbor.direction)
            sum_y += math.sin(neighbor.direction)
        
        # Average direction
        avg_direction = math.atan2(sum_y / len(neighbor_ids), sum_x / len(neighbor_ids))
        return avg_direction
    
    def _update_drone(self, drone: Drone) -> str:
        """Update single drone position and return action taken"""
        neighbors = self._get_neighbors(drone)
        action = "move_forward"
        
        # Rule 1: Low battery reduces speed
        current_velocity = drone.velocity
        if drone.battery < self.low_battery_threshold:
            current_velocity = drone.velocity * self.speed_reduction_factor
            action = "low_battery_slow"
        
        # Rule 2: Avoid nearby drones (with reciprocal velocity sensing)
        if neighbors:
            action = "avoid_collision"
            # Calculate direction away from nearest neighbor
            nearest = min(self.drones, key=lambda d: drone.distance_to(d) if d.id in neighbors else float('inf'))
            
            # NEW: Modulate avoidance intensity based on neighbor approach speed
            neighbor_speed = self._get_neighbor_velocity(drone, nearest.id)
            avoidance_multiplier = 1.0 + (neighbor_speed / self.max_velocity)  # 1.0 to 2.0
            
            # Calculate away direction
            away_x = drone.x - nearest.x
            away_y = drone.y - nearest.y
            distance = math.sqrt(away_x**2 + away_y**2)
            
            if distance > 0:
                # NEW: Apply flocking influence - mix avoidance with neighbor directions
                # 70% avoid from nearest neighbor, 30% align with neighbor flock direction
                avg_neighbor_dir = self._get_average_neighbor_direction(drone, neighbors)
                
                # Avoidance direction
                avoidance_dir = math.atan2(away_y, away_x)
                
                # Weighted average of avoidance and flocking
                flocking_weight = 0.3
                avoidance_weight = 1.0 - flocking_weight
                
                blended_x = (math.cos(avoidance_dir) * avoidance_weight + 
                            math.cos(avg_neighbor_dir) * flocking_weight)
                blended_y = (math.sin(avoidance_dir) * avoidance_weight + 
                            math.sin(avg_neighbor_dir) * flocking_weight)
                
                # Normalize
                blend_mag = math.sqrt(blended_x**2 + blended_y**2)
                if blend_mag > 0:
                    blended_x /= blend_mag
                    blended_y /= blend_mag
                
                # Move with modulated velocity and blended direction
                move_dist = current_velocity * avoidance_multiplier
                drone.x += blended_x * move_dist
                drone.y += blended_y * move_dist
                
                # Update heading for next timestep (for flocking)
                drone.direction = math.atan2(blended_y, blended_x)
        else:
            # Rule 3: Move forward with slight randomness
            angle = drone.direction + random.uniform(-0.2, 0.2)
            drone.direction = angle
            drone.x += current_velocity * math.cos(angle)
            drone.y += current_velocity * math.sin(angle)
        
        # Wrap around grid boundaries
        drone.x = drone.x % self.grid_size
        drone.y = drone.y % self.grid_size
        
        # Drain battery
        drone.battery = max(0, drone.battery - self.battery_drain_rate)
        
        return action
    
    def _log_state_with_actions(self, actions: dict):
        """Log state with actions taken"""
        with open(self.log_file, 'a') as f:
            for drone in self.drones:
                neighbors = self._get_neighbors(drone)
                
                log_entry = {
                    "time": self.timestep,
                    "drone_id": drone.id,
                    "position": {"x": round(drone.x, 2), "y": round(drone.y, 2)},
                    "battery": round(drone.battery, 2),
                    "neighbors": neighbors,
                    "action": actions.get(drone.id, "unknown")
                }
                
                f.write(json.dumps(log_entry) + '\n')
    
    def step(self):
        """Execute one simulation timestep"""
        actions = {}
        
        # Update all drones
        for drone in self.drones:
            action = self._update_drone(drone)
            actions[drone.id] = action
        
        # Log state with actions
        self._log_state_with_actions(actions)
        
        self.timestep += 1
    
    def run(self, num_steps: int = 1000):
        """Run simulation for specified number of timesteps"""
        print(f"Starting drone swarm simulation...")
        print(f"  - Drones: {self.num_drones}")
        print(f"  - Grid size: {self.grid_size}x{self.grid_size}")
        print(f"  - Timesteps: {num_steps}")
        print(f"  - Output: {self.log_file}")
        print()
        
        for _ in range(num_steps):
            self.step()
            
            # Progress indicator
            if (self.timestep + 1) % 100 == 0:
                avg_battery = sum(d.battery for d in self.drones) / self.num_drones
                print(f"Timestep {self.timestep}: avg battery = {avg_battery:.1f}%")
        
        print()
        print(f"Simulation complete! Logged {self.timestep} timesteps to {self.log_file}")
    
    def print_summary(self):
        """Print final state summary"""
        print("\n=== Final State ===")
        for drone in self.drones:
            print(f"Drone {drone.id}: pos=({drone.x:.1f}, {drone.y:.1f}), battery={drone.battery:.1f}%")


def main():
    """Main entry point - run flocking + reciprocal sensing experiment"""
    import sys
    
    # Run 3 simulations with 30 drones each, different random seeds
    # EXPERIMENT: Flocking (local information integration) + Reciprocal Sensing
    num_drones = 30
    grid_size = 30
    num_runs = 3
    
    print("\n" + "="*60)
    print("FLOCKING + RECIPROCAL SENSING EXPERIMENT")
    print("Hypothesis: Combined feedback + information integration triggers")
    print("            higher-order emergent behaviors (coherent formations)")
    print("="*60)
    
    for run_id in range(num_runs):
        random.seed(run_id * 42)  # Different seed per run
        
        # Create output filename
        output_file = f"swarm_log_flocking_run{run_id}.jsonl"
        
        # Create and run swarm simulation
        swarm = DroneSwarm(num_drones=num_drones, grid_size=grid_size)
        swarm.log_file = output_file
        
        print(f"\n{'='*60}")
        print(f"RUN {run_id + 1} of {num_runs}")
        print(f"{'='*60}")
        
        swarm.run(num_steps=1000)
        swarm.print_summary()
        
        print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
