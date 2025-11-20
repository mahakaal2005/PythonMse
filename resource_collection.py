"""Resource Collection Team - Multiple agents collecting resources cooperatively
Uses shared task queue and distributed decision logic - Terminal only version"""

import random
from collections import deque
from typing import List, Tuple, Set, Dict
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

class ResourceCollectionTeam:
    def __init__(self, maze_size: int = 20, num_agents: int = 4, num_resources: int = 15):
        self.maze_size = maze_size
        self.num_agents = num_agents
        self.num_resources = num_resources
        
        # Create simple grid maze
        self.grid = [[' ' for _ in range(maze_size + 1)] for _ in range(maze_size + 1)]
        self.walls = set()
        
        # Shared task queue and coordination
        self.resource_positions = set()
        self.task_queue = deque()
        self.claimed_resources = {}  # resource_pos -> agent_id
        self.collected_resources = {}  # agent_id -> count
        
        # Agent data
        self.agent_positions = {}
        self.agent_paths = {}
        self.agent_symbols = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧']
        
        # Statistics
        self.collection_history = {i: [] for i in range(num_agents)}
        self.move_count = 0
        
    def generate_maze(self):
        """Generate a simple maze with walls"""
        # Create border walls
        for i in range(self.maze_size + 1):
            self.walls.add((0, i))
            self.walls.add((self.maze_size, i))
            self.walls.add((i, 0))
            self.walls.add((i, self.maze_size))
        
        # Add some random internal walls
        num_walls = (self.maze_size * self.maze_size) // 10
        for _ in range(num_walls):
            x = random.randint(1, self.maze_size - 1)
            y = random.randint(1, self.maze_size - 1)
            self.walls.add((x, y))
    
    def initialize_agents(self):
        """Initialize agents at different starting positions"""
        # Place agents in corners and edges
        start_positions = [
            (1, 1),                              # Top-left
            (self.maze_size - 1, self.maze_size - 1),  # Bottom-right
            (1, self.maze_size - 1),             # Top-right
            (self.maze_size - 1, 1)              # Bottom-left
        ]
        
        # Add more positions if needed
        if self.num_agents > 4:
            mid = self.maze_size // 2
            extra_positions = [
                (mid, 1), (mid, self.maze_size - 1),
                (1, mid), (self.maze_size - 1, mid)
            ]
            start_positions.extend(extra_positions[:self.num_agents - 4])
        
        for i in range(self.num_agents):
            pos = start_positions[i % len(start_positions)]
            # Ensure not on wall
            while pos in self.walls:
                pos = (pos[0] + 1, pos[1])
            self.agent_positions[i] = pos
            self.collected_resources[i] = 0
            self.agent_paths[i] = []
            
    def place_resources(self):
        """Place resources randomly in the maze, ensuring they're reachable"""
        placed = 0
        attempts = 0
        max_attempts = 1000
        
        while placed < self.num_resources and attempts < max_attempts:
            x = random.randint(1, self.maze_size - 1)
            y = random.randint(1, self.maze_size - 1)
            pos = (x, y)
            
            # Avoid agent starting positions and walls
            if (pos not in self.agent_positions.values() and 
                pos not in self.resource_positions and 
                pos not in self.walls):
                # Verify it's reachable from at least one agent
                reachable = False
                for agent_pos in self.agent_positions.values():
                    path = self.get_path_bfs(agent_pos, pos)
                    if len(path) > 1 or (len(path) == 1 and path[0] == pos):
                        reachable = True
                        break
                
                if reachable:
                    self.resource_positions.add(pos)
                    self.task_queue.append(pos)
                    placed += 1
            attempts += 1
    
    def get_path_bfs(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find shortest path using BFS in the maze"""
        if start == goal:
            return [start]
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            pos, path = queue.popleft()
            
            if pos == goal:
                return path
            
            # Get valid neighbors (4 directions)
            x, y = pos
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                
                # Check if valid position (not wall, in bounds, not visited)
                if (neighbor not in self.walls and 
                    0 <= neighbor[0] <= self.maze_size and 
                    0 <= neighbor[1] <= self.maze_size and
                    neighbor not in visited):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return [start]  # No path found
    
    def assign_task(self, agent_id: int) -> Tuple[int, int]:
        """Distributed decision logic - agent selects best task from queue"""
        current_pos = self.agent_positions[agent_id]
        best_resource = None
        best_distance = float('inf')
        
        # Check unclaimed resources in queue
        available_resources = [r for r in self.task_queue 
                               if r not in self.claimed_resources 
                               and r in self.resource_positions]
        
        if not available_resources:
            return None
        
        # Select nearest unclaimed resource
        for resource_pos in available_resources:
            distance = abs(current_pos[0] - resource_pos[0]) + abs(current_pos[1] - resource_pos[1])
            if distance < best_distance:
                best_distance = distance
                best_resource = resource_pos
        
        if best_resource:
            self.claimed_resources[best_resource] = agent_id
            
        return best_resource
    
    def move_agent(self, agent_id: int, target: Tuple[int, int]) -> bool:
        """Move agent one step towards target, return True if reached"""
        current_pos = self.agent_positions[agent_id]
        
        if current_pos == target:
            return True
        
        # Get path to target
        path = self.get_path_bfs(current_pos, target)
        
        if len(path) > 1:
            next_pos = path[1]
            self.agent_positions[agent_id] = next_pos
            self.agent_paths[agent_id].append(next_pos)
            return next_pos == target
        
        return False
    
    def collect_resource(self, agent_id: int, resource_pos: Tuple[int, int]):
        """Agent collects a resource"""
        if resource_pos in self.resource_positions:
            self.resource_positions.remove(resource_pos)
            self.collected_resources[agent_id] += 1
            self.collection_history[agent_id].append(self.move_count)
            
            # Remove from queue and claims
            if resource_pos in self.task_queue:
                self.task_queue.remove(resource_pos)
            if resource_pos in self.claimed_resources:
                del self.claimed_resources[resource_pos]
    
    def run_simulation(self):
        """Run the cooperative resource collection simulation"""
        agent_targets = {i: None for i in range(self.num_agents)}
        max_moves = 2000
        
        print(f"\nStarting simulation with {self.num_agents} agents collecting {self.num_resources} resources...")
        
        while self.resource_positions and self.move_count < max_moves:
            self.move_count += 1
            
            for agent_id in range(self.num_agents):
                # Assign new task if agent has no target
                if agent_targets[agent_id] is None:
                    target = self.assign_task(agent_id)
                    if target:
                        agent_targets[agent_id] = target
                
                # Move towards target
                if agent_targets[agent_id]:
                    reached = self.move_agent(agent_id, agent_targets[agent_id])
                    
                    if reached:
                        # Collect resource
                        self.collect_resource(agent_id, agent_targets[agent_id])
                        agent_targets[agent_id] = None
            
            # Progress update
            if self.move_count % 100 == 0:
                collected = sum(self.collected_resources.values())
                print(f"Move {self.move_count}: {collected}/{self.num_resources} resources collected")
        
        print(f"\nSimulation completed in {self.move_count} moves")
        print(f"Total resources collected: {sum(self.collected_resources.values())}/{self.num_resources}")
    
    def visualize_maze_terminal(self):
        """Display maze in terminal with agents and resources using colors"""
        # ANSI color codes
        COLORS = {
            'reset': '\033[0m',
            'wall': '\033[90m',        # Dark gray
            'path': '\033[36m',        # Cyan
            'resource': '\033[93m',    # Bright yellow
            'agent1': '\033[94m',      # Bright blue
            'agent2': '\033[91m',      # Bright red
            'agent3': '\033[92m',      # Bright green
            'agent4': '\033[95m',      # Bright magenta
            'empty': '\033[37m',       # Light gray
            'header': '\033[96m',      # Bright cyan
            'success': '\033[92m',     # Bright green
        }
        
        # Create display grid
        display = [[' ' for _ in range(self.maze_size + 1)] for _ in range(self.maze_size + 1)]
        
        # Add walls
        for wall in self.walls:
            if 0 <= wall[0] <= self.maze_size and 0 <= wall[1] <= self.maze_size:
                display[wall[0]][wall[1]] = '█'
        
        # Add resources
        for res in self.resource_positions:
            if 0 <= res[0] <= self.maze_size and 0 <= res[1] <= self.maze_size:
                display[res[0]][res[1]] = '◆'
        
        # Add agent paths
        for agent_id in range(self.num_agents):
            for pos in self.agent_paths[agent_id]:
                if (0 <= pos[0] <= self.maze_size and 0 <= pos[1] <= self.maze_size and
                    display[pos[0]][pos[1]] == ' '):
                    display[pos[0]][pos[1]] = '·'
        
        # Add current agent positions
        for agent_id, pos in self.agent_positions.items():
            if 0 <= pos[0] <= self.maze_size and 0 <= pos[1] <= self.maze_size:
                display[pos[0]][pos[1]] = self.agent_symbols[agent_id]
        
        # Print the maze with colors
        print("\n" + COLORS['header'] + "╔" + "═"*60 + "╗" + COLORS['reset'])
        print(COLORS['header'] + "║" + " "*15 + "RESOURCE COLLECTION - MAZE VIEW" + " "*14 + "║" + COLORS['reset'])
        print(COLORS['header'] + "╚" + "═"*60 + "╝" + COLORS['reset'])
        print()
        
        for row in display:
            line = ""
            for cell in row:
                if cell == '█':
                    line += COLORS['wall'] + '█ ' + COLORS['reset']
                elif cell == '◆':
                    line += COLORS['resource'] + '◆ ' + COLORS['reset']
                elif cell == '·':
                    line += COLORS['path'] + '· ' + COLORS['reset']
                elif cell == '①':
                    line += COLORS['agent1'] + '① ' + COLORS['reset']
                elif cell == '②':
                    line += COLORS['agent2'] + '② ' + COLORS['reset']
                elif cell == '③':
                    line += COLORS['agent3'] + '③ ' + COLORS['reset']
                elif cell == '④':
                    line += COLORS['agent4'] + '④ ' + COLORS['reset']
                elif cell in ['⑤', '⑥', '⑦', '⑧']:
                    line += COLORS['agent1'] + cell + ' ' + COLORS['reset']
                else:
                    line += COLORS['empty'] + '  ' + COLORS['reset']
            print(line)
        
        print("\n" + COLORS['header'] + "Legend:" + COLORS['reset'])
        print(f"  {COLORS['agent1']}①{COLORS['reset']} {COLORS['agent2']}②{COLORS['reset']} {COLORS['agent3']}③{COLORS['reset']} {COLORS['agent4']}④{COLORS['reset']} = Agents")
        print(f"  {COLORS['resource']}◆{COLORS['reset']} = Resource (uncollected)")
        print(f"  {COLORS['path']}·{COLORS['reset']} = Agent paths")
        print(f"  {COLORS['wall']}█{COLORS['reset']} = Wall")
        print(COLORS['header'] + "─"*60 + COLORS['reset'] + "\n")
    
    def plot_statistics(self):
        """Plot resource collection statistics"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Bar chart - resources per agent
        agents = [f'Agent {i+1}' for i in range(self.num_agents)]
        counts = [self.collected_resources[i] for i in range(self.num_agents)]
        colors_plot = ['blue', 'red', 'green', 'cyan', 'magenta', 'yellow', 'orange', 'purple']
        
        bars = ax1.bar(agents, counts, color=colors_plot[:self.num_agents], alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Agent', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Resources Collected', fontsize=12, fontweight='bold')
        ax1.set_title('Resources Collected by Each Agent', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')
        
        # Timeline - cumulative collection
        ax2.set_xlabel('Move Count', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Cumulative Resources Collected', fontsize=12, fontweight='bold')
        ax2.set_title('Resource Collection Timeline', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        for agent_id in range(self.num_agents):
            if self.collection_history[agent_id]:
                cumulative = list(range(1, len(self.collection_history[agent_id]) + 1))
                ax2.plot(self.collection_history[agent_id], cumulative, 
                        marker='o', label=f'Agent {agent_id + 1}',
                        color=colors_plot[agent_id], linewidth=2, markersize=6)
        
        ax2.legend(loc='best', fontsize=10)
        
        plt.tight_layout()
        plt.savefig('resource_collection_stats.png', dpi=150, bbox_inches='tight')
        print("\n✓ Statistics plot saved as 'resource_collection_stats.png'")
        plt.close('all')
    
    def print_summary(self):
        """Print simulation summary with colors"""
        # ANSI color codes
        COLORS = {
            'reset': '\033[0m',
            'header': '\033[96m',      # Bright cyan
            'success': '\033[92m',     # Bright green
            'agent1': '\033[94m',      # Bright blue
            'agent2': '\033[91m',      # Bright red
            'agent3': '\033[92m',      # Bright green
            'agent4': '\033[95m',      # Bright magenta
            'info': '\033[93m',        # Bright yellow
            'bold': '\033[1m',
        }
        
        agent_colors = [COLORS['agent1'], COLORS['agent2'], COLORS['agent3'], COLORS['agent4']]
        
        print("\n" + COLORS['header'] + "╔" + "═"*60 + "╗" + COLORS['reset'])
        print(COLORS['header'] + "║" + " "*12 + "RESOURCE COLLECTION TEAM - SUMMARY" + " "*13 + "║" + COLORS['reset'])
        print(COLORS['header'] + "╚" + "═"*60 + "╝" + COLORS['reset'])
        
        print(f"\n{COLORS['info']}📊 Simulation Statistics:{COLORS['reset']}")
        print(f"   • Maze Size: {COLORS['bold']}{self.maze_size}x{self.maze_size}{COLORS['reset']}")
        print(f"   • Number of Agents: {COLORS['bold']}{self.num_agents}{COLORS['reset']}")
        print(f"   • Total Resources: {COLORS['bold']}{self.num_resources}{COLORS['reset']}")
        print(f"   • Total Moves: {COLORS['bold']}{self.move_count}{COLORS['reset']}")
        
        print(f"\n{COLORS['info']}🤖 Resources Collected by Agent:{COLORS['reset']}")
        for agent_id in range(self.num_agents):
            count = self.collected_resources[agent_id]
            percentage = (count / self.num_resources * 100) if self.num_resources > 0 else 0
            color = agent_colors[agent_id % len(agent_colors)]
            
            # Create progress bar
            bar_length = 20
            filled = int(bar_length * count / max(self.collected_resources.values())) if max(self.collected_resources.values()) > 0 else 0
            bar = '█' * filled + '░' * (bar_length - filled)
            
            print(f"   {color}Agent {agent_id + 1}:{COLORS['reset']} {color}{bar}{COLORS['reset']} {COLORS['bold']}{count}{COLORS['reset']} resources ({percentage:.1f}%)")
        
        total_collected = sum(self.collected_resources.values())
        efficiency = (total_collected / self.num_resources * 100) if self.num_resources > 0 else 0
        
        print(f"\n{COLORS['success']}✓ Total Collected: {COLORS['bold']}{total_collected}/{self.num_resources}{COLORS['reset']} {COLORS['success']}({efficiency:.1f}%){COLORS['reset']}")
        print(f"{COLORS['success']}✓ Average per Agent: {COLORS['bold']}{total_collected / self.num_agents:.2f}{COLORS['reset']}")
        print(f"{COLORS['success']}✓ Efficiency: {COLORS['bold']}{self.move_count / total_collected:.2f}{COLORS['reset']} moves per resource")
        print(COLORS['header'] + "─"*60 + COLORS['reset'] + "\n")


def main():
    """Run the resource collection team simulation"""
    # ANSI color codes
    COLORS = {
        'reset': '\033[0m',
        'header': '\033[96m',
        'success': '\033[92m',
        'info': '\033[93m',
        'bold': '\033[1m',
    }
    
    print(COLORS['header'] + "\n╔" + "═"*60 + "╗" + COLORS['reset'])
    print(COLORS['header'] + "║" + " "*10 + "RESOURCE COLLECTION TEAM SIMULATION" + " "*14 + "║" + COLORS['reset'])
    print(COLORS['header'] + "╚" + "═"*60 + "╝" + COLORS['reset'])
    
    # Create simulation
    team = ResourceCollectionTeam(maze_size=20, num_agents=4, num_resources=15)
    
    # Generate maze
    print(f"\n{COLORS['info']}⚙️  Generating maze...{COLORS['reset']}")
    team.generate_maze()
    
    # Initialize agents and resources
    team.initialize_agents()
    team.place_resources()
    
    print(f"{COLORS['success']}✓ Maze created: {COLORS['bold']}{team.maze_size}x{team.maze_size}{COLORS['reset']}")
    print(f"{COLORS['success']}✓ Agents deployed: {COLORS['bold']}{team.num_agents}{COLORS['reset']}")
    print(f"{COLORS['success']}✓ Resources placed: {COLORS['bold']}{team.num_resources}{COLORS['reset']}")
    
    # Run simulation
    team.run_simulation()
    
    # Visualize in terminal
    team.visualize_maze_terminal()
    
    # Print summary
    team.print_summary()
    
    # Plot statistics (saved to file, no GUI)
    team.plot_statistics()


if __name__ == "__main__":
    main()
