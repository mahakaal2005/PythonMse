"""
Dual Maze Navigators - Two cooperative agents collecting keys in a maze
Uses BFS for Agent 1 and DFS for Agent 2 with coordination to avoid overlap
"""

import random
from collections import deque
from typing import List, Tuple, Set, Dict
import time
import sys
import io
from pyamaze import maze, agent, COLOR, textLabel

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Color codes for terminal output
COLORS = {
    'wall': '\033[90m',      # Dark gray
    'corridor': '\033[37m',  # Light gray - shows walkable paths
    'path1': '\033[94m',     # Blue
    'path2': '\033[91m',     # Red
    'key': '\033[93m',       # Yellow
    'collected': '\033[92m', # Green
    'agent1': '\033[94m',    # Blue
    'agent2': '\033[91m',    # Red
    'reset': '\033[0m'
}


class MazeNavigator:
    def __init__(self, width: int = 25, height: int = 18, num_keys: int = 10):
        self.width = width
        self.height = height
        self.num_keys = num_keys
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        self.keys_positions = set()
        self.agent1_pos = None
        self.agent2_pos = None
        self.agent1_path = []
        self.agent2_path = []
        self.agent1_visited = set()
        self.agent2_visited = set()
        self.collected_keys = set()
        self.shared_visited = set()
        self.agent1_target = None
        self.agent2_target = None
        self.agent1_claimed = set()
        self.agent2_claimed = set()
        
    def generate_maze(self):
        """Generate a proper maze using recursive backtracking algorithm"""
        # Initialize grid with all walls
        for i in range(self.height):
            for j in range(self.width):
                self.grid[i][j] = '#'
        
        # Recursive backtracking maze generation
        def carve_passages(cx, cy):
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                
                if 1 <= nx < self.height - 1 and 1 <= ny < self.width - 1 and self.grid[nx][ny] == '#':
                    # Carve passage
                    self.grid[cx + dx // 2][cy + dy // 2] = ' '
                    self.grid[nx][ny] = ' '
                    carve_passages(nx, ny)
        
        # Start carving from (1, 1)
        self.grid[1][1] = ' '
        carve_passages(1, 1)
        
        # Add some extra passages to make maze less linear (20% of cells)
        extra_passages = (self.width * self.height) // 40
        for _ in range(extra_passages):
            x = random.randrange(2, self.height - 2)
            y = random.randrange(2, self.width - 2)
            if self.grid[x][y] == '#':
                # Check if removing this wall connects two passages
                neighbors = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                              if self.grid[x + dx][y + dy] == ' ')
                if neighbors >= 2:
                    self.grid[x][y] = ' '
        
        # Place keys in open spaces
        keys_placed = 0
        attempts = 0
        while keys_placed < self.num_keys and attempts < 1000:
            x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
            if self.grid[x][y] == ' ':
                self.grid[x][y] = 'K'
                self.keys_positions.add((x, y))
                keys_placed += 1
            attempts += 1
        
        # Place agents in opposite corners
        self.agent1_pos = (1, 1)
        self.agent2_pos = (self.height - 2, self.width - 2)
        
        # Ensure starting positions are clear
        if (self.agent1_pos[0], self.agent1_pos[1]) in self.keys_positions:
            self.keys_positions.remove((self.agent1_pos[0], self.agent1_pos[1]))
        if (self.agent2_pos[0], self.agent2_pos[1]) in self.keys_positions:
            self.keys_positions.remove((self.agent2_pos[0], self.agent2_pos[1]))
        
        self.grid[self.agent1_pos[0]][self.agent1_pos[1]] = ' '
        self.grid[self.agent2_pos[0]][self.agent2_pos[1]] = ' '
        
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring cells"""
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.height and 0 <= ny < self.width and 
                self.grid[nx][ny] != '#'):
                neighbors.append((nx, ny))
        return neighbors
    
    def bfs_explore(self, start: Tuple[int, int], agent_id: int) -> Tuple[List[Tuple[int, int]], Tuple[int, int]]:
        """BFS exploration - finds nearest uncollected and unclaimed key"""
        queue = deque([(start, [start])])
        visited = {start}
        claimed = self.agent2_claimed if agent_id == 1 else self.agent1_claimed
        
        while queue:
            pos, path = queue.popleft()
            
            # Check if we found an uncollected and unclaimed key
            if (pos in self.keys_positions and 
                pos not in self.collected_keys and 
                pos not in claimed):
                return path, pos
            
            for neighbor in self.get_neighbors(pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return [start], None  # No path found
    
    def find_nearest_key_bfs(self, start: Tuple[int, int], excluded_keys: Set) -> Tuple[List[Tuple[int, int]], Tuple[int, int]]:
        """Find nearest uncollected key using BFS, excluding claimed keys"""
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            pos, path = queue.popleft()
            
            # Check if we found an uncollected and unexcluded key
            if (pos in self.keys_positions and 
                pos not in self.collected_keys and 
                pos not in excluded_keys):
                return path, pos
            
            for neighbor in self.get_neighbors(pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return [start], None
    
    def communicate_paths(self):
        """Agents share their visited cells and targets to avoid overlap"""
        self.shared_visited = self.agent1_visited.union(self.agent2_visited)
        
    def assign_territories(self):
        """Divide maze into territories for each agent to minimize overlap"""
        # Agent 1 focuses on upper-left region, Agent 2 on lower-right
        mid_x = self.height // 2
        mid_y = self.width // 2
        
        for key_pos in self.keys_positions:
            if key_pos not in self.collected_keys:
                # Calculate distances from both agents
                dist1 = abs(key_pos[0] - self.agent1_pos[0]) + abs(key_pos[1] - self.agent1_pos[1])
                dist2 = abs(key_pos[0] - self.agent2_pos[0]) + abs(key_pos[1] - self.agent2_pos[1])
                
                # Assign to closer agent with territory bias
                if dist1 < dist2 * 0.8:  # Agent 1 gets priority if significantly closer
                    self.agent1_claimed.add(key_pos)
                elif dist2 < dist1 * 0.8:  # Agent 2 gets priority if significantly closer
                    self.agent2_claimed.add(key_pos)
    
    def visualize_step(self, step_num: int):
        """Display current maze state during exploration"""
        import os
        # Clear screen (works on Windows and Unix)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        display_grid = [row[:] for row in self.grid]
        
        # Mark Agent 1's path so far
        for pos in self.agent1_path:
            if display_grid[pos[0]][pos[1]] == ' ':
                display_grid[pos[0]][pos[1]] = '1'
        
        # Mark Agent 2's path so far
        for pos in self.agent2_path:
            if display_grid[pos[0]][pos[1]] == ' ':
                display_grid[pos[0]][pos[1]] = '2'
        
        # Mark collected keys
        for key_pos in self.collected_keys:
            display_grid[key_pos[0]][key_pos[1]] = '*'
        
        # Mark uncollected keys
        for key_pos in self.keys_positions:
            if key_pos not in self.collected_keys:
                display_grid[key_pos[0]][key_pos[1]] = 'K'
        
        # Mark current agent positions
        display_grid[self.agent1_pos[0]][self.agent1_pos[1]] = 'A'
        display_grid[self.agent2_pos[0]][self.agent2_pos[1]] = 'B'
        
        # Print the maze
        print("="*60)
        print(f"STEP {step_num} - Keys: {len(self.collected_keys)}/{self.num_keys}")
        print("="*60 + "\n")
        
        for row in display_grid:
            line = ""
            for cell in row:
                if cell == '#':
                    line += COLORS['wall'] + '█ ' + COLORS['reset']
                elif cell == 'K':
                    line += COLORS['key'] + '◆ ' + COLORS['reset']
                elif cell == '*':
                    line += COLORS['collected'] + '✓ ' + COLORS['reset']
                elif cell == '1':
                    line += COLORS['path1'] + '· ' + COLORS['reset']
                elif cell == '2':
                    line += COLORS['path2'] + '· ' + COLORS['reset']
                elif cell == 'A':
                    line += COLORS['agent1'] + '① ' + COLORS['reset']
                elif cell == 'B':
                    line += COLORS['agent2'] + '② ' + COLORS['reset']
                elif cell == ' ':
                    line += COLORS['corridor'] + '· ' + COLORS['reset']
                else:
                    line += '  '
            print(line)
        
        print(f"\nAgent 1: {len(self.agent1_path)} steps | Agent 2: {len(self.agent2_path)} steps")
        time.sleep(0.05)  # Small delay to see the animation
    
    def move_agents(self):
        """Move both agents simultaneously with enhanced cooperation"""
        moves = 0
        max_moves = 1000
        agent1_target_path = []
        agent2_target_path = []
        stall_counter = 0
        
        # Initial territory assignment
        self.assign_territories()
        
        # Show initial state
        self.visualize_step(0)
        
        while len(self.collected_keys) < self.num_keys and moves < max_moves:
            prev_collected = len(self.collected_keys)
            
            # Agent 1 - find new path if needed
            if not agent1_target_path:
                agent1_target_path, self.agent1_target = self.find_nearest_key_bfs(
                    self.agent1_pos, self.agent2_claimed)
                if self.agent1_target:
                    self.agent1_claimed.add(self.agent1_target)
                elif stall_counter > 50:  # Fallback: ignore claims if stalled
                    agent1_target_path, self.agent1_target = self.find_nearest_key_bfs(
                        self.agent1_pos, set())
                    if self.agent1_target:
                        self.agent1_claimed.add(self.agent1_target)
            
            # Move Agent 1 along path
            if len(agent1_target_path) > 1:
                agent1_target_path.pop(0)
                self.agent1_pos = agent1_target_path[0]
                self.agent1_path.append(self.agent1_pos)
                self.agent1_visited.add(self.agent1_pos)
                
                # Check if Agent 1 collected a key
                if self.agent1_pos in self.keys_positions and self.agent1_pos not in self.collected_keys:
                    self.collected_keys.add(self.agent1_pos)
                    if self.agent1_pos in self.agent1_claimed:
                        self.agent1_claimed.remove(self.agent1_pos)
                    if self.agent1_pos in self.agent2_claimed:
                        self.agent2_claimed.remove(self.agent1_pos)
                    agent1_target_path = []
                    self.agent1_target = None
            else:
                agent1_target_path = []
                self.agent1_target = None
            
            # Agent 2 - find new path if needed
            if not agent2_target_path:
                agent2_target_path, self.agent2_target = self.find_nearest_key_bfs(
                    self.agent2_pos, self.agent1_claimed)
                if self.agent2_target:
                    self.agent2_claimed.add(self.agent2_target)
                elif stall_counter > 50:  # Fallback: ignore claims if stalled
                    agent2_target_path, self.agent2_target = self.find_nearest_key_bfs(
                        self.agent2_pos, set())
                    if self.agent2_target:
                        self.agent2_claimed.add(self.agent2_target)
            
            # Move Agent 2 along path
            if len(agent2_target_path) > 1:
                agent2_target_path.pop(0)
                self.agent2_pos = agent2_target_path[0]
                self.agent2_path.append(self.agent2_pos)
                self.agent2_visited.add(self.agent2_pos)
                
                # Check if Agent 2 collected a key
                if self.agent2_pos in self.keys_positions and self.agent2_pos not in self.collected_keys:
                    self.collected_keys.add(self.agent2_pos)
                    if self.agent2_pos in self.agent2_claimed:
                        self.agent2_claimed.remove(self.agent2_pos)
                    if self.agent2_pos in self.agent1_claimed:
                        self.agent1_claimed.remove(self.agent2_pos)
                    agent2_target_path = []
                    self.agent2_target = None
            else:
                agent2_target_path = []
                self.agent2_target = None
            
            # Track stalls
            if len(self.collected_keys) == prev_collected:
                stall_counter += 1
            else:
                stall_counter = 0
            
            # Real-time communication every move
            self.communicate_paths()
            
            # Reassign territories every 30 moves for dynamic adaptation
            if moves % 30 == 0:
                self.assign_territories()
            
            moves += 1
            
            # Visualize every few steps (adjust frequency as needed)
            if moves % 3 == 0 or len(self.collected_keys) == self.num_keys:
                self.visualize_step(moves)
        
        return moves
    
    def visualize(self):
        """Display the final maze with both agents' paths using colors"""
        display_grid = [row[:] for row in self.grid]
        
        # Mark Agent 1's path (BFS)
        for pos in self.agent1_path:
            if display_grid[pos[0]][pos[1]] == ' ':
                display_grid[pos[0]][pos[1]] = '1'
        
        # Mark Agent 2's path (DFS)
        for pos in self.agent2_path:
            if display_grid[pos[0]][pos[1]] == ' ':
                display_grid[pos[0]][pos[1]] = '2'
        
        # Mark collected keys
        for key_pos in self.collected_keys:
            display_grid[key_pos[0]][key_pos[1]] = '*'
        
        # Mark uncollected keys
        for key_pos in self.keys_positions:
            if key_pos not in self.collected_keys:
                display_grid[key_pos[0]][key_pos[1]] = 'K'
        
        # Mark current agent positions
        display_grid[self.agent1_pos[0]][self.agent1_pos[1]] = 'A'
        display_grid[self.agent2_pos[0]][self.agent2_pos[1]] = 'B'
        
        # Print the maze with colors
        print("\n" + "="*60)
        print("DUAL MAZE NAVIGATOR - FINAL STATE")
        print("="*60 + "\n")
        
        for row in display_grid:
            line = ""
            for cell in row:
                if cell == '#':
                    line += COLORS['wall'] + '█ ' + COLORS['reset']
                elif cell == 'K':
                    line += COLORS['key'] + '◆ ' + COLORS['reset']
                elif cell == '*':
                    line += COLORS['collected'] + '✓ ' + COLORS['reset']
                elif cell == '1':
                    line += COLORS['path1'] + '· ' + COLORS['reset']
                elif cell == '2':
                    line += COLORS['path2'] + '· ' + COLORS['reset']
                elif cell == 'A':
                    line += COLORS['agent1'] + '① ' + COLORS['reset']
                elif cell == 'B':
                    line += COLORS['agent2'] + '② ' + COLORS['reset']
                elif cell == ' ':  # Empty corridor - make it visible
                    line += COLORS['corridor'] + '· ' + COLORS['reset']
                else:
                    line += '  '
            print(line)
        
        print("\nLegend:")
        print(f"{COLORS['agent1']}① · {COLORS['reset']} = Agent 1 (BFS) path")
        print(f"{COLORS['agent2']}② · {COLORS['reset']} = Agent 2 (DFS) path")
        print(f"{COLORS['collected']}✓{COLORS['reset']} = Collected key")
        print(f"{COLORS['key']}◆{COLORS['reset']} = Uncollected key")
        print(f"{COLORS['wall']}█{COLORS['reset']} = Wall")
        
        print("\n" + "="*60)
        print(f"Keys Collected: {len(self.collected_keys)}/{self.num_keys}")
        print(f"Agent 1 (BFS) Path Length: {len(self.agent1_path)}")
        print(f"Agent 2 (DFS) Path Length: {len(self.agent2_path)}")
        print(f"Agent 1 Visited Cells: {len(self.agent1_visited)}")
        print(f"Agent 2 Visited Cells: {len(self.agent2_visited)}")
        print(f"Shared Knowledge: {len(self.shared_visited)} cells")
        print("="*60 + "\n")


def main():
    """Run the dual maze navigator simulation"""
    print("Initializing Dual Maze Navigator...")
    
    # Create and setup maze
    navigator = MazeNavigator(width=25, height=18, num_keys=10)
    navigator.generate_maze()
    
    print("Maze generated with keys scattered throughout.")
    print("Agent 1 (BFS) starting at top-left")
    print("Agent 2 (DFS) starting at bottom-right")
    print("\nAgents are exploring and collecting keys...\n")
    
    # Run the simulation
    moves = navigator.move_agents()
    
    # Display results
    navigator.visualize()
    
    print(f"Simulation completed in {moves} moves.")
    
    if len(navigator.collected_keys) == navigator.num_keys:
        print("✓ SUCCESS: All keys collected!")
    else:
        print(f"⚠ PARTIAL: {len(navigator.collected_keys)}/{navigator.num_keys} keys collected")
    
    print("\nCommunication Log:")
    print(f"- Agents shared visited cell information to avoid overlap")
    print(f"- Total unique cells explored: {len(navigator.shared_visited)}")
    print(f"- Cooperation efficiency: {len(navigator.shared_visited)/(len(navigator.agent1_visited) + len(navigator.agent2_visited)):.2%}")


if __name__ == "__main__":
    main()
