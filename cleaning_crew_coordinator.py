"""
Cleaning Crew Coordination - Two cleaning bots dividing rooms and cleaning efficiently
Uses A* for Bot 1 and Greedy Search for Bot 2 with shared task lists
"""

import random
import heapq
from typing import List, Tuple, Set, Dict
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Color codes for terminal output
COLORS = {
    'wall': '\033[90m',      # Dark gray
    'floor': '\033[37m',     # Light gray - shows cleanable floor
    'path1': '\033[94m',     # Blue
    'path2': '\033[91m',     # Red
    'dirty': '\033[93m',     # Yellow
    'clean1': '\033[94m',    # Blue
    'clean2': '\033[91m',    # Red
    'bot1': '\033[94m',      # Blue
    'bot2': '\033[91m',      # Red
    'reset': '\033[0m'
}


class CleaningCrewCoordinator:
    def __init__(self, width: int = 30, height: int = 20, dirty_percentage: float = 0.4):
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        self.dirty_cells = set()
        self.bot1_pos = None
        self.bot2_pos = None
        self.bot1_path = []
        self.bot2_path = []
        self.bot1_cleaned = set()
        self.bot2_cleaned = set()
        self.bot1_assigned = set()  # Shared task list for bot 1
        self.bot2_assigned = set()  # Shared task list for bot 2
        self.obstacles = set()
        self.total_dirty = 0
        self.bot1_cleaning_moves = 0  # Count only productive moves
        self.bot2_cleaning_moves = 0
        
    def generate_environment(self):
        """Generate a 2D grid with dirty cells and obstacles"""
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
        
        # Add random obstacles (furniture)
        num_obstacles = (self.width * self.height) // 20
        for _ in range(num_obstacles):
            x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
            self.grid[x][y] = '#'
            self.obstacles.add((x, y))
        
        # Place dirty cells
        total_cells = (self.width - 2) * (self.height - 2)
        num_dirty = int(total_cells * 0.4)
        
        while len(self.dirty_cells) < num_dirty:
            x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
            if (x, y) not in self.obstacles:
                self.dirty_cells.add((x, y))
                self.grid[x][y] = 'D'
        
        self.total_dirty = len(self.dirty_cells)
        
        # Place bots in opposite corners
        self.bot1_pos = (1, 1)
        self.bot2_pos = (self.height - 2, self.width - 2)
        
        # Ensure starting positions are clear
        if self.bot1_pos in self.dirty_cells:
            self.dirty_cells.remove(self.bot1_pos)
        if self.bot2_pos in self.dirty_cells:
            self.dirty_cells.remove(self.bot2_pos)
        self.grid[self.bot1_pos[0]][self.bot1_pos[1]] = ' '
        self.grid[self.bot2_pos[0]][self.bot2_pos[1]] = ' '
        
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring cells"""
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in self.obstacles:
                neighbors.append((nx, ny))
        return neighbors
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def astar_search(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """A* pathfinding algorithm"""
        if goal is None:
            return []
        
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            _, current = heapq.heappop(frontier)
            
            if current == goal:
                # Reconstruct path
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            for neighbor in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.manhattan_distance(neighbor, goal)
                    heapq.heappush(frontier, (priority, neighbor))
                    came_from[neighbor] = current
        
        return []  # No path found
    
    def greedy_search(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Greedy Best-First Search - prioritizes getting closer to goal"""
        if goal is None:
            return []
        
        frontier = [(self.manhattan_distance(start, goal), start)]
        came_from = {start: None}
        visited = {start}
        
        while frontier:
            _, current = heapq.heappop(frontier)
            
            if current == goal:
                # Reconstruct path
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    priority = self.manhattan_distance(neighbor, goal)
                    heapq.heappush(frontier, (priority, neighbor))
                    came_from[neighbor] = current
        
        return []  # No path found
    
    def find_nearest_dirty_cell(self, pos: Tuple[int, int], excluded: Set) -> Tuple[int, int]:
        """Find nearest dirty cell not in excluded set"""
        uncleaned = self.dirty_cells - self.bot1_cleaned - self.bot2_cleaned - excluded
        if not uncleaned:
            return None
        
        nearest = min(uncleaned, key=lambda cell: self.manhattan_distance(pos, cell))
        return nearest
    
    def assign_territories(self):
        """Divide dirty cells between bots based on proximity and workload balance"""
        self.bot1_assigned.clear()
        self.bot2_assigned.clear()
        
        uncleaned = self.dirty_cells - self.bot1_cleaned - self.bot2_cleaned
        
        # Sort cells by distance from midpoint for better distribution
        cells_list = list(uncleaned)
        
        for cell in cells_list:
            dist1 = self.manhattan_distance(cell, self.bot1_pos)
            dist2 = self.manhattan_distance(cell, self.bot2_pos)
            
            # Strict assignment to closer bot
            if dist1 < dist2:
                self.bot1_assigned.add(cell)
            elif dist2 < dist1:
                self.bot2_assigned.add(cell)
            # If equal distance, balance workload
            elif len(self.bot1_assigned) <= len(self.bot2_assigned):
                self.bot1_assigned.add(cell)
            else:
                self.bot2_assigned.add(cell)
    
    def visualize_step(self, step_num: int):
        """Display current cleaning state during operation"""
        import os
        import time as t
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        display_grid = [row[:] for row in self.grid]
        
        # Mark Bot 1's path
        for pos in self.bot1_path:
            if display_grid[pos[0]][pos[1]] == ' ':
                display_grid[pos[0]][pos[1]] = '1'
        
        # Mark Bot 2's path
        for pos in self.bot2_path:
            if display_grid[pos[0]][pos[1]] == ' ':
                display_grid[pos[0]][pos[1]] = '2'
        
        # Mark cleaned cells
        for pos in self.bot1_cleaned:
            display_grid[pos[0]][pos[1]] = 'A'
        for pos in self.bot2_cleaned:
            if pos in self.bot1_cleaned:
                display_grid[pos[0]][pos[1]] = 'X'
            else:
                display_grid[pos[0]][pos[1]] = 'B'
        
        # Mark remaining dirty cells
        for pos in self.dirty_cells:
            if pos not in self.bot1_cleaned and pos not in self.bot2_cleaned:
                display_grid[pos[0]][pos[1]] = 'D'
        
        # Mark current bot positions
        display_grid[self.bot1_pos[0]][self.bot1_pos[1]] = 'P'
        display_grid[self.bot2_pos[0]][self.bot2_pos[1]] = 'Q'
        
        # Print
        unique_cleaned = len(self.bot1_cleaned.union(self.bot2_cleaned))
        print("="*60)
        print(f"STEP {step_num} - Cleaned: {unique_cleaned}/{self.total_dirty}")
        print("="*60 + "\n")
        
        for row in display_grid:
            line = ""
            for cell in row:
                if cell == '#':
                    line += COLORS['wall'] + '█ ' + COLORS['reset']
                elif cell == 'D':
                    line += COLORS['dirty'] + '◆ ' + COLORS['reset']
                elif cell == 'A':
                    line += COLORS['clean1'] + '✓ ' + COLORS['reset']
                elif cell == 'B':
                    line += COLORS['clean2'] + '✓ ' + COLORS['reset']
                elif cell == 'X':
                    line += '\033[95m' + '✗ ' + COLORS['reset']
                elif cell == '1':
                    line += COLORS['path1'] + '· ' + COLORS['reset']
                elif cell == '2':
                    line += COLORS['path2'] + '· ' + COLORS['reset']
                elif cell == 'P':
                    line += COLORS['bot1'] + '① ' + COLORS['reset']
                elif cell == 'Q':
                    line += COLORS['bot2'] + '② ' + COLORS['reset']
                elif cell == ' ':
                    line += COLORS['floor'] + '· ' + COLORS['reset']
                else:
                    line += '  '
            print(line)
        
        print(f"\nBot 1: {self.bot1_cleaning_moves} moves | Bot 2: {self.bot2_cleaning_moves} moves")
        t.sleep(0.05)
    
    def coordinate_cleaning(self):
        """Coordinate both bots to clean efficiently with zero overlap"""
        moves = 0
        max_moves = 2000
        bot1_target_path = []
        bot2_target_path = []
        bot1_target = None
        bot2_target = None
        stall_counter = 0
        
        # Initial territory assignment
        self.assign_territories()
        
        total_cleaned = len(self.bot1_cleaned.union(self.bot2_cleaned))
        
        # Show initial state
        self.visualize_step(0)
        
        while total_cleaned < self.total_dirty and moves < max_moves:
            prev_cleaned = total_cleaned
            
            # Bot 1 uses A* - find new target if needed
            if not bot1_target_path or bot1_target in self.bot1_cleaned or bot1_target in self.bot2_cleaned:
                # Exclude both bot2's assigned cells AND already cleaned cells
                excluded = self.bot2_assigned.union(self.bot2_cleaned)
                bot1_target = self.find_nearest_dirty_cell(self.bot1_pos, excluded)
                if bot1_target:
                    self.bot1_assigned.add(bot1_target)
                    bot1_target_path = self.astar_search(self.bot1_pos, bot1_target)
                elif stall_counter > 30:  # Fallback: only exclude already cleaned
                    bot1_target = self.find_nearest_dirty_cell(self.bot1_pos, self.bot2_cleaned)
                    if bot1_target:
                        bot1_target_path = self.astar_search(self.bot1_pos, bot1_target)
            
            # Move Bot 1
            if len(bot1_target_path) > 1:
                bot1_target_path.pop(0)
                self.bot1_pos = bot1_target_path[0]
                self.bot1_path.append(self.bot1_pos)
                self.bot1_cleaning_moves += 1
                
                # Check if Bot 1 cleaned a cell
                if self.bot1_pos in self.dirty_cells and self.bot1_pos not in self.bot1_cleaned and self.bot1_pos not in self.bot2_cleaned:
                    self.bot1_cleaned.add(self.bot1_pos)
                    if self.bot1_pos in self.bot1_assigned:
                        self.bot1_assigned.remove(self.bot1_pos)
                    if self.bot1_pos in self.bot2_assigned:
                        self.bot2_assigned.remove(self.bot1_pos)
                    bot1_target_path = []
                    bot1_target = None
                elif self.bot1_pos in self.bot2_cleaned:
                    # Bot 2 already cleaned this, find new target
                    bot1_target_path = []
                    bot1_target = None
            else:
                bot1_target_path = []
                bot1_target = None
            
            # Bot 2 uses Greedy Search - find new target if needed
            if not bot2_target_path or bot2_target in self.bot2_cleaned or bot2_target in self.bot1_cleaned:
                # Exclude both bot1's assigned cells AND already cleaned cells
                excluded = self.bot1_assigned.union(self.bot1_cleaned)
                bot2_target = self.find_nearest_dirty_cell(self.bot2_pos, excluded)
                if bot2_target:
                    self.bot2_assigned.add(bot2_target)
                    bot2_target_path = self.greedy_search(self.bot2_pos, bot2_target)
                elif stall_counter > 30:  # Fallback: only exclude already cleaned
                    bot2_target = self.find_nearest_dirty_cell(self.bot2_pos, self.bot1_cleaned)
                    if bot2_target:
                        bot2_target_path = self.greedy_search(self.bot2_pos, bot2_target)
            
            # Move Bot 2
            if len(bot2_target_path) > 1:
                bot2_target_path.pop(0)
                self.bot2_pos = bot2_target_path[0]
                self.bot2_path.append(self.bot2_pos)
                self.bot2_cleaning_moves += 1
                
                # Check if Bot 2 cleaned a cell
                if self.bot2_pos in self.dirty_cells and self.bot2_pos not in self.bot2_cleaned and self.bot2_pos not in self.bot1_cleaned:
                    self.bot2_cleaned.add(self.bot2_pos)
                    if self.bot2_pos in self.bot2_assigned:
                        self.bot2_assigned.remove(self.bot2_pos)
                    if self.bot2_pos in self.bot1_assigned:
                        self.bot1_assigned.remove(self.bot2_pos)
                    bot2_target_path = []
                    bot2_target = None
                elif self.bot2_pos in self.bot1_cleaned:
                    # Bot 1 already cleaned this, find new target
                    bot2_target_path = []
                    bot2_target = None
            else:
                bot2_target_path = []
                bot2_target = None
            
            # Update total cleaned (unique cells)
            total_cleaned = len(self.bot1_cleaned.union(self.bot2_cleaned))
            
            # Track stalls
            if total_cleaned == prev_cleaned:
                stall_counter += 1
            else:
                stall_counter = 0
            
            # Reassign territories more frequently for better coordination
            if moves % 25 == 0:
                self.assign_territories()
            
            moves += 1
            
            # Visualize every few steps
            if moves % 10 == 0 or total_cleaned == self.total_dirty:
                self.visualize_step(moves)
        
        return moves
    
    def calculate_efficiency(self) -> float:
        """Calculate cleaning efficiency score based on cooperation"""
        # Count unique cells cleaned (no double counting)
        unique_cleaned = len(self.bot1_cleaned.union(self.bot2_cleaned))
        
        # Total cells each bot cleaned (individual work)
        bot1_work = len(self.bot1_cleaned)
        bot2_work = len(self.bot2_cleaned)
        total_work = bot1_work + bot2_work
        
        if total_work == 0:
            return 0.0
        
        # Efficiency = unique cleaned / total work * 100
        # If no overlap, this equals 100%
        efficiency = (unique_cleaned / total_work) * 100
        return efficiency
    
    def visualize(self):
        """Display the final grid with cleaned cells and efficiency score using colors"""
        display_grid = [row[:] for row in self.grid]
        
        # Mark Bot 1's path
        for pos in self.bot1_path:
            if display_grid[pos[0]][pos[1]] == ' ':
                display_grid[pos[0]][pos[1]] = '1'
        
        # Mark Bot 2's path
        for pos in self.bot2_path:
            if display_grid[pos[0]][pos[1]] == ' ':
                display_grid[pos[0]][pos[1]] = '2'
        
        # Mark cleaned cells by Bot 1
        for pos in self.bot1_cleaned:
            display_grid[pos[0]][pos[1]] = 'A'
        
        # Mark cleaned cells by Bot 2
        for pos in self.bot2_cleaned:
            if pos in self.bot1_cleaned:
                display_grid[pos[0]][pos[1]] = 'X'  # Overlap
            else:
                display_grid[pos[0]][pos[1]] = 'B'
        
        # Mark remaining dirty cells
        for pos in self.dirty_cells:
            if pos not in self.bot1_cleaned and pos not in self.bot2_cleaned:
                display_grid[pos[0]][pos[1]] = 'D'
        
        # Mark current bot positions
        display_grid[self.bot1_pos[0]][self.bot1_pos[1]] = 'P'
        display_grid[self.bot2_pos[0]][self.bot2_pos[1]] = 'Q'
        
        # Print the grid with colors
        print("\n" + "="*70)
        print("CLEANING CREW COORDINATOR - FINAL STATE")
        print("="*70 + "\n")
        
        for row in display_grid:
            line = ""
            for cell in row:
                if cell == '#':
                    line += COLORS['wall'] + '█ ' + COLORS['reset']
                elif cell == 'D':
                    line += COLORS['dirty'] + '◆ ' + COLORS['reset']
                elif cell == 'A':
                    line += COLORS['clean1'] + '✓ ' + COLORS['reset']
                elif cell == 'B':
                    line += COLORS['clean2'] + '✓ ' + COLORS['reset']
                elif cell == 'X':
                    line += '\033[95m' + '✗ ' + COLORS['reset']  # Magenta for overlap
                elif cell == '1':
                    line += COLORS['path1'] + '· ' + COLORS['reset']
                elif cell == '2':
                    line += COLORS['path2'] + '· ' + COLORS['reset']
                elif cell == 'P':
                    line += COLORS['bot1'] + '① ' + COLORS['reset']
                elif cell == 'Q':
                    line += COLORS['bot2'] + '② ' + COLORS['reset']
                elif cell == ' ':  # Empty floor - make it visible
                    line += COLORS['floor'] + '· ' + COLORS['reset']
                else:
                    line += '  '
            print(line)
        
        print("\nLegend:")
        print(f"{COLORS['bot1']}① · {COLORS['reset']} = Bot 1 (A*) path")
        print(f"{COLORS['bot2']}② · {COLORS['reset']} = Bot 2 (Greedy) path")
        print(f"{COLORS['clean1']}✓{COLORS['reset']} = Bot 1 cleaned")
        print(f"{COLORS['clean2']}✓{COLORS['reset']} = Bot 2 cleaned")
        print(f"{COLORS['dirty']}◆{COLORS['reset']} = Dirty cell")
        print(f"\033[95m✗{COLORS['reset']} = Overlap")
        print(f"{COLORS['wall']}█{COLORS['reset']} = Obstacle")
        
        # Calculate statistics
        unique_cleaned = len(self.bot1_cleaned.union(self.bot2_cleaned))
        overlap = len(self.bot1_cleaned.intersection(self.bot2_cleaned))
        efficiency = self.calculate_efficiency()
        
        print("\n" + "="*70)
        print(f"Total Dirty Cells: {self.total_dirty}")
        print(f"Unique Cells Cleaned: {unique_cleaned}/{self.total_dirty}")
        print(f"Bot 1 (A*) Cleaned: {len(self.bot1_cleaned)} cells")
        print(f"Bot 2 (Greedy) Cleaned: {len(self.bot2_cleaned)} cells")
        print(f"Bot 1 Total Moves: {self.bot1_cleaning_moves}")
        print(f"Bot 2 Total Moves: {self.bot2_cleaning_moves}")
        print(f"Total Moves: {self.bot1_cleaning_moves + self.bot2_cleaning_moves}")
        print(f"Overlap (cells cleaned by both): {overlap}")
        print(f"Cooperation Efficiency: {efficiency:.2f}%")
        print("="*70 + "\n")


def main():
    """Run the cleaning crew coordination simulation"""
    print("Initializing Cleaning Crew Coordinator...")
    
    # Create and setup environment
    coordinator = CleaningCrewCoordinator(width=35, height=22, dirty_percentage=0.4)
    coordinator.generate_environment()
    
    print(f"Environment generated with {coordinator.total_dirty} dirty cells.")
    print("Bot 1 (A*) starting at top-left")
    print("Bot 2 (Greedy Search) starting at bottom-right")
    print("\nBots are coordinating and cleaning...\n")
    
    # Run the simulation
    moves = coordinator.coordinate_cleaning()
    
    # Display results
    coordinator.visualize()
    
    print(f"Simulation completed in {moves} coordination cycles.")
    
    total_cleaned = len(coordinator.bot1_cleaned) + len(coordinator.bot2_cleaned)
    if total_cleaned == coordinator.total_dirty:
        print("✓ SUCCESS: All cells cleaned!")
    else:
        print(f"⚠ PARTIAL: {total_cleaned}/{coordinator.total_dirty} cells cleaned")
    
    print("\nCoordination Summary:")
    print(f"- Bots used shared task lists to divide work")
    print(f"- Territory reassignment every 40 moves for dynamic adaptation")
    print(f"- Bot 1 used A* for optimal pathfinding")
    print(f"- Bot 2 used Greedy Search for faster exploration")


if __name__ == "__main__":
    main()
