"""Map Exploration Partners - Agents explore unknown regions cooperatively
Uses grid partitioning logic and generates exploration efficiency heatmap"""

import random
import heapq
from collections import deque
from typing import List, Tuple, Set, Dict
import sys
import io
import os
import time
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Color codes for terminal output
COLORS = {
    'wall': '\033[90m',           # Dark gray
    'unexplored': '\033[37m',     # Light gray
    'explored1': '\033[94m',      # Blue
    'explored2': '\033[91m',      # Red
    'explored3': '\033[92m',      # Green
    'explored4': '\033[95m',      # Magenta
    'agent1': '\033[48;5;21m\033[97m',     # White on blue
    'agent2': '\033[48;5;196m\033[97m',    # White on red
    'agent3': '\033[48;5;34m\033[97m',     # White on green
    'agent4': '\033[48;5;201m\033[97m',    # White on magenta
    'header': '\033[96m\033[1m',  # Bright cyan bold
    'success': '\033[92m',        # Bright green
    'info': '\033[93m',           # Bright yellow
    'border': '\033[93m',         # Yellow
    'reset': '\033[0m'
}


class MapExplorationTeam:
    def __init__(self, width: int = 40, height: int = 25, num_agents: int = 4):
        self.width = width
        self.height = height
        self.num_agents = num_agents
        
        # Grid setup
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        self.obstacles = set()
        self.unexplored = set()
        self.explored = set()
        
        # Agent data
        self.agent_positions = {}
        self.agent_paths = {}
        self.agent_explored = {i: set() for i in range(num_agents)}
        self.agent_territories = {i: set() for i in range(num_agents)}
        self.agent_symbols = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧']
        self.agent_colors = ['explored1', 'explored2', 'explored3', 'explored4']
        
        # Statistics
        self.total_explorable = 0
        self.move_count = 0
        self.exploration_efficiency = {i: [] for i in range(num_agents)}
        
    def generate_map(self):
        """Generate a map with obstacles and unexplored regions"""
        # Add borders
        for i in range(self.height):
            self.grid[i][0] = '#'
            self.grid[i][self.width - 1] = '#'
            self.obstacles.add((i, 0))
            self.obstacles.add((i, self.width - 1))
        
        for j in range(self.width):
            self.grid[0][j] = '#'
            self.grid[self.height - 1][j] = '#'
            self.obstacles.add((0, j))
            self.obstacles.add((self.height - 1, j))
        
        # Add random obstacles (walls, mountains, etc.)
        num_obstacles = (self.width * self.height) // 15
        for _ in range(num_obstacles):
            x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
            self.grid[x][y] = '#'
            self.obstacles.add((x, y))
        
        # Mark all non-obstacle cells as unexplored
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if (i, j) not in self.obstacles:
                    self.unexplored.add((i, j))
                    self.grid[i][j] = '?'
        
        self.total_explorable = len(self.unexplored)
    
    def initialize_agents(self):
        """Initialize agents at different corners"""
        start_positions = [
            (1, 1),                              # Top-left
            (self.height - 2, self.width - 2),   # Bottom-right
            (1, self.width - 2),                 # Top-right
            (self.height - 2, 1)                 # Bottom-left
        ]
        
        # Add more positions if needed
        if self.num_agents > 4:
            mid_x = self.height // 2
            mid_y = self.width // 2
            extra_positions = [
                (mid_x, 1), (mid_x, self.width - 2),
                (1, mid_y), (self.height - 2, mid_y)
            ]
            start_positions.extend(extra_positions[:self.num_agents - 4])
        
        for i in range(self.num_agents):
            pos = start_positions[i % len(start_positions)]
            # Ensure not on obstacle
            while pos in self.obstacles:
                pos = (pos[0] + 1, pos[1] + 1)
            
            self.agent_positions[i] = pos
            self.agent_paths[i] = [pos]
            
            # Mark starting position as explored
            if pos in self.unexplored:
                self.unexplored.remove(pos)
                self.explored.add(pos)
                self.agent_explored[i].add(pos)
    
    def partition_territories(self):
        """Divide unexplored regions using grid partitioning logic"""
        # Clear previous assignments
        for i in range(self.num_agents):
            self.agent_territories[i].clear()
        
        # Assign each unexplored cell to nearest agent
        for cell in self.unexplored:
            min_dist = float('inf')
            closest_agent = 0
            
            for agent_id in range(self.num_agents):
                agent_pos = self.agent_positions[agent_id]
                dist = abs(cell[0] - agent_pos[0]) + abs(cell[1] - agent_pos[1])
                
                if dist < min_dist:
                    min_dist = dist
                    closest_agent = agent_id
            
            self.agent_territories[closest_agent].add(cell)
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring cells"""
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in self.obstacles and 0 <= nx < self.height and 0 <= ny < self.width:
                neighbors.append((nx, ny))
        return neighbors
    
    def bfs_to_nearest_unexplored(self, start: Tuple[int, int], territory: Set) -> List[Tuple[int, int]]:
        """Find path to nearest unexplored cell in agent's territory using BFS"""
        if not territory:
            # If no territory assigned, explore any unexplored cell
            territory = self.unexplored
        
        if not territory:
            return []
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            pos, path = queue.popleft()
            
            # Check if we found an unexplored cell in territory
            if pos in territory and pos in self.unexplored:
                return path
            
            for neighbor in self.get_neighbors(pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    def explore_step(self):
        """One step of exploration for all agents"""
        for agent_id in range(self.num_agents):
            current_pos = self.agent_positions[agent_id]
            
            # Find path to nearest unexplored cell in territory
            path = self.bfs_to_nearest_unexplored(current_pos, self.agent_territories[agent_id])
            
            if len(path) > 1:
                # Move to next position
                next_pos = path[1]
                self.agent_positions[agent_id] = next_pos
                self.agent_paths[agent_id].append(next_pos)
                
                # Mark as explored
                if next_pos in self.unexplored:
                    self.unexplored.remove(next_pos)
                    self.explored.add(next_pos)
                    self.agent_explored[agent_id].add(next_pos)
                    self.grid[next_pos[0]][next_pos[1]] = str(agent_id + 1)
    
    def visualize_step(self, step_num: int):
        """Display current exploration state"""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        display_grid = [row[:] for row in self.grid]
        
        # Mark explored cells by each agent
        for agent_id in range(self.num_agents):
            for pos in self.agent_explored[agent_id]:
                if display_grid[pos[0]][pos[1]] not in ['#', '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧']:
                    display_grid[pos[0]][pos[1]] = str(agent_id + 1)
        
        # Mark current agent positions
        for agent_id, pos in self.agent_positions.items():
            display_grid[pos[0]][pos[1]] = self.agent_symbols[agent_id]
        
        # Print header
        explored_count = len(self.explored)
        progress = (explored_count / self.total_explorable * 100) if self.total_explorable > 0 else 0
        
        print(COLORS['header'] + "╔" + "═"*70 + "╗" + COLORS['reset'])
        print(COLORS['header'] + "║" + f" STEP {step_num:4d} - Explored: {explored_count}/{self.total_explorable} ({progress:.1f}%)".center(78) + "║" + COLORS['reset'])
        print(COLORS['header'] + "╚" + "═"*70 + "╝" + COLORS['reset'])
        print()
        
        # Print maze with colors
        print(COLORS['border'] + "  ┌" + "─" * (self.width * 2) + "┐" + COLORS['reset'])
        
        for row in display_grid:
            line = COLORS['border'] + "  │" + COLORS['reset']
            for cell in row:
                if cell == '#':
                    line += COLORS['wall'] + '██' + COLORS['reset']
                elif cell == '?':
                    line += COLORS['unexplored'] + '░░' + COLORS['reset']
                elif cell == '1':
                    line += COLORS['explored1'] + '··' + COLORS['reset']
                elif cell == '2':
                    line += COLORS['explored2'] + '··' + COLORS['reset']
                elif cell == '3':
                    line += COLORS['explored3'] + '··' + COLORS['reset']
                elif cell == '4':
                    line += COLORS['explored4'] + '··' + COLORS['reset']
                elif cell == '①':
                    line += COLORS['agent1'] + '①①' + COLORS['reset']
                elif cell == '②':
                    line += COLORS['agent2'] + '②②' + COLORS['reset']
                elif cell == '③':
                    line += COLORS['agent3'] + '③③' + COLORS['reset']
                elif cell == '④':
                    line += COLORS['agent4'] + '④④' + COLORS['reset']
                else:
                    line += COLORS['unexplored'] + '  ' + COLORS['reset']
            line += COLORS['border'] + "│" + COLORS['reset']
            print(line)
        
        print(COLORS['border'] + "  └" + "─" * (self.width * 2) + "┘" + COLORS['reset'])
        
        # Print agent stats
        print(f"\n{COLORS['info']}Agent Exploration:{COLORS['reset']}")
        for agent_id in range(self.num_agents):
            count = len(self.agent_explored[agent_id])
            percentage = (count / self.total_explorable * 100) if self.total_explorable > 0 else 0
            color = COLORS[self.agent_colors[agent_id % len(self.agent_colors)]]
            print(f"  {color}Agent {agent_id + 1}:{COLORS['reset']} {count} cells ({percentage:.1f}%)")
        
        time.sleep(0.05)
    
    def run_exploration(self):
        """Run the cooperative exploration simulation"""
        print(f"\n{COLORS['info']}Starting exploration with {self.num_agents} agents...{COLORS['reset']}\n")
        
        max_moves = 3000
        
        while self.unexplored and self.move_count < max_moves:
            self.move_count += 1
            
            # Repartition territories every 30 moves for dynamic adaptation
            if self.move_count % 30 == 0:
                self.partition_territories()
            
            # Explore step
            self.explore_step()
            
            # Visualize every 10 steps
            if self.move_count % 10 == 0 or not self.unexplored:
                self.visualize_step(self.move_count)
            
            # Track efficiency
            for agent_id in range(self.num_agents):
                efficiency = len(self.agent_explored[agent_id]) / max(1, len(self.agent_paths[agent_id]))
                self.exploration_efficiency[agent_id].append(efficiency)
        
        print(f"\n{COLORS['success']}✓ Exploration completed in {self.move_count} moves{COLORS['reset']}")
    
    def generate_heatmap(self):
        """Generate exploration efficiency heatmap"""
        # Create heatmap grid
        heatmap = np.zeros((self.height, self.width))
        
        # Fill heatmap with exploration data
        for agent_id in range(self.num_agents):
            for pos in self.agent_explored[agent_id]:
                heatmap[pos[0]][pos[1]] = agent_id + 1
        
        # Mark obstacles as -1
        for obs in self.obstacles:
            heatmap[obs[0]][obs[1]] = -1
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Heatmap
        cmap = plt.cm.get_cmap('tab10', self.num_agents + 2)
        im = ax1.imshow(heatmap, cmap=cmap, interpolation='nearest', vmin=-1, vmax=self.num_agents)
        ax1.set_title('Exploration Heatmap by Agent', fontsize=14, fontweight='bold')
        ax1.set_xlabel('X Coordinate', fontsize=12)
        ax1.set_ylabel('Y Coordinate', fontsize=12)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax1, ticks=range(-1, self.num_agents + 1))
        labels = ['Obstacle'] + [f'Agent {i+1}' for i in range(self.num_agents)] + ['Unexplored']
        cbar.set_ticklabels(labels[:self.num_agents + 2])
        
        # Bar chart - cells explored per agent
        agents = [f'Agent {i+1}' for i in range(self.num_agents)]
        counts = [len(self.agent_explored[i]) for i in range(self.num_agents)]
        colors_plot = ['#3498db', '#e74c3c', '#2ecc71', '#9b59b6', '#f39c12', '#1abc9c']
        
        bars = ax2.bar(agents, counts, color=colors_plot[:self.num_agents], alpha=0.7, edgecolor='black', linewidth=2)
        ax2.set_xlabel('Agent', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Cells Explored', fontsize=12, fontweight='bold')
        ax2.set_title('Exploration Efficiency by Agent', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        plt.tight_layout()
        plt.savefig('exploration_heatmap.png', dpi=150, bbox_inches='tight')
        print(f"\n{COLORS['success']}✓ Exploration heatmap saved as 'exploration_heatmap.png'{COLORS['reset']}")
        plt.close()
    
    def print_summary(self):
        """Print exploration summary"""
        print("\n" + COLORS['header'] + "╔" + "═"*70 + "╗" + COLORS['reset'])
        print(COLORS['header'] + "║" + " "*20 + "EXPLORATION SUMMARY" + " "*31 + "║" + COLORS['reset'])
        print(COLORS['header'] + "╚" + "═"*70 + "╝" + COLORS['reset'])
        
        print(f"\n{COLORS['info']}📊 Map Statistics:{COLORS['reset']}")
        print(f"   • Map Size: {COLORS['success']}{self.height}x{self.width}{COLORS['reset']}")
        print(f"   • Total Explorable Cells: {COLORS['success']}{self.total_explorable}{COLORS['reset']}")
        print(f"   • Obstacles: {COLORS['success']}{len(self.obstacles)}{COLORS['reset']}")
        print(f"   • Total Moves: {COLORS['success']}{self.move_count}{COLORS['reset']}")
        
        print(f"\n{COLORS['info']}🤖 Agent Performance:{COLORS['reset']}")
        
        total_explored = len(self.explored)
        
        for agent_id in range(self.num_agents):
            count = len(self.agent_explored[agent_id])
            percentage = (count / total_explored * 100) if total_explored > 0 else 0
            path_length = len(self.agent_paths[agent_id])
            efficiency = (count / path_length * 100) if path_length > 0 else 0
            
            color = COLORS[self.agent_colors[agent_id % len(self.agent_colors)]]
            
            # Progress bar
            bar_length = 30
            filled = int(bar_length * count / max([len(self.agent_explored[i]) for i in range(self.num_agents)]))
            bar = '█' * filled + '░' * (bar_length - filled)
            
            print(f"   {color}Agent {agent_id + 1}:{COLORS['reset']}")
            print(f"      {color}{bar}{COLORS['reset']} {count} cells ({percentage:.1f}%)")
            print(f"      Path Length: {path_length} | Efficiency: {efficiency:.1f}%")
        
        coverage = (total_explored / self.total_explorable * 100) if self.total_explorable > 0 else 0
        
        print(f"\n{COLORS['success']}✓ Total Coverage: {total_explored}/{self.total_explorable} ({coverage:.1f}%){COLORS['reset']}")
        print(f"{COLORS['success']}✓ Average Efficiency: {self.move_count / total_explored:.2f} moves per cell{COLORS['reset']}")
        
        # Check for overlap
        overlap_count = 0
        for i in range(self.num_agents):
            for j in range(i + 1, self.num_agents):
                overlap_count += len(self.agent_explored[i].intersection(self.agent_explored[j]))
        
        print(f"{COLORS['success']}✓ Territory Overlap: {overlap_count} cells{COLORS['reset']}")
        print(COLORS['header'] + "  " + "─"*68 + COLORS['reset'] + "\n")


def main():
    """Run the map exploration simulation"""
    print(COLORS['header'] + "\n╔" + "═"*70 + "╗" + COLORS['reset'])
    print(COLORS['header'] + "║" + " "*20 + "MAP EXPLORATION PARTNERS" + " "*27 + "║" + COLORS['reset'])
    print(COLORS['header'] + "╚" + "═"*70 + "╝" + COLORS['reset'])
    
    # Create simulation
    team = MapExplorationTeam(width=40, height=25, num_agents=4)
    
    # Generate map
    print(f"\n{COLORS['info']}⚙️  Generating map...{COLORS['reset']}")
    team.generate_map()
    
    # Initialize agents
    team.initialize_agents()
    
    # Initial territory partition
    team.partition_territories()
    
    print(f"{COLORS['success']}✓ Map created: {team.height}x{team.width}{COLORS['reset']}")
    print(f"{COLORS['success']}✓ Agents deployed: {team.num_agents}{COLORS['reset']}")
    print(f"{COLORS['success']}✓ Explorable cells: {team.total_explorable}{COLORS['reset']}")
    print(f"{COLORS['success']}✓ Territories partitioned using grid logic{COLORS['reset']}")
    
    # Run exploration
    team.run_exploration()
    
    # Final visualization
    team.visualize_step(team.move_count)
    
    # Print summary
    team.print_summary()
    
    # Generate heatmap
    team.generate_heatmap()
    
    print(f"\n{COLORS['info']}Exploration Strategy:{COLORS['reset']}")
    print(f"  • Grid partitioning divides unexplored regions among agents")
    print(f"  • Each agent explores nearest cells in their territory")
    print(f"  • Territories dynamically reassigned every 30 moves")
    print(f"  • BFS pathfinding ensures efficient exploration")


if __name__ == "__main__":
    main()
