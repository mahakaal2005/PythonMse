# =======================
# COOPERATIVE PATH PLANNING WITH PYMAZE - TERMINAL VISUALIZATION
# =======================

import heapq
import time
import os
from typing import List, Tuple, Dict, Set
from pyamaze import maze

Coord = Tuple[int, int]

# ANSI color codes
RESET = "\033[0m"
BLUE = "\033[94m"
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
GREY = "\033[90m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"


def neighbors(pos: Coord, m: maze):
    """Get valid neighbors for a position in the maze."""
    r, c = pos
    result = []
    
    # Check all four directions based on maze walls
    if (r, c) in m.maze_map:
        if m.maze_map[(r, c)]['E'] == 1 and c < m.cols:  # East
            result.append((r, c + 1))
        if m.maze_map[(r, c)]['W'] == 1 and c > 1:  # West
            result.append((r, c - 1))
        if m.maze_map[(r, c)]['S'] == 1 and r < m.rows:  # South
            result.append((r + 1, c))
        if m.maze_map[(r, c)]['N'] == 1 and r > 1:  # North
            result.append((r - 1, c))
    
    return result


def manhattan(a: Coord, b: Coord):
    """Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_with_reservations(start, goal, m, reserved, reserved_edges, max_time=200):
    """Space-Time A* with collision avoidance."""
    start_state = (0, start[0], start[1])
    open_heap = []
    heapq.heappush(open_heap, (manhattan(start, goal), 0, start_state))
    came_from = {}
    g_score = {start_state: 0}

    while open_heap:
        f, g, (t, r, c) = heapq.heappop(open_heap)

        if (r, c) == goal:
            # Reconstruct path
            path = [(r, c)]
            cur = (t, r, c)
            while cur in came_from:
                cur = came_from[cur]
                path.append((cur[1], cur[2]))
            return list(reversed(path))

        if t > max_time:
            continue

        # Include waiting at current position
        for nr, nc in neighbors((r, c), m) + [(r, c)]:
            nt = t + 1

            # Collision checks
            if nt in reserved and (nr, nc) in reserved[nt]:
                continue

            if t in reserved_edges and ((nr, nc), (r, c)) in reserved_edges[t]:
                continue

            state = (nt, nr, nc)
            tentative = g + 1

            if state not in g_score or tentative < g_score[state]:
                g_score[state] = tentative
                came_from[state] = (t, r, c)
                f_score = tentative + manhattan((nr, nc), goal)
                heapq.heappush(open_heap, (f_score, tentative, state))

    raise RuntimeError("No path found")


def cooperative_planning(m: maze, startA, goalA, startB, goalB):
    """Plan paths for both agents cooperatively."""
    # Plan Agent A first
    reserved = {}
    reserved_edges = {}

    pathA = astar_with_reservations(startA, goalA, m, reserved, reserved_edges)

    # Reserve A's path
    for t in range(len(pathA)):
        cell = pathA[t]
        reserved.setdefault(t, set()).add(cell)
        if t > 0:
            reserved_edges.setdefault(t-1, set()).add((pathA[t-1], cell))

    # Keep A's goal reserved
    endA = pathA[-1]
    for t in range(len(pathA), len(pathA) + 20):
        reserved.setdefault(t, set()).add(endA)

    # Plan Agent B avoiding A
    pathB = astar_with_reservations(startB, goalB, m, reserved, reserved_edges)

    # Pad both paths to equal length
    L = max(len(pathA), len(pathB))
    while len(pathA) < L:
        pathA.append(pathA[-1])
    while len(pathB) < L:
        pathB.append(pathB[-1])

    return pathA, pathB


def render_maze_terminal(m: maze, posA: Coord, posB: Coord, goalA: Coord, goalB: Coord, step: int):
    """Render the maze in terminal with agents."""
    lines = []
    lines.append(f"\n{CYAN}{'='*60}{RESET}")
    lines.append(f"{CYAN}Step {step:3d}{RESET} | {BLUE}Agent A: {posA}{RESET} | {RED}Agent B: {posB}{RESET}")
    lines.append(f"{CYAN}{'='*60}{RESET}\n")
    
    # Build the maze visualization
    for r in range(1, m.rows + 1):
        row_top = ""
        row_mid = ""
        
        for c in range(1, m.cols + 1):
            cell = m.maze_map.get((r, c), {})
            
            # Determine cell content
            if (r, c) == posA and (r, c) == posB:
                content = f"{YELLOW}@{RESET}"  # Both agents
            elif (r, c) == posA:
                content = f"{BLUE}A{RESET}"
            elif (r, c) == posB:
                content = f"{RED}B{RESET}"
            elif (r, c) == goalA:
                content = f"{GREEN}a{RESET}"
            elif (r, c) == goalB:
                content = f"{GREEN}b{RESET}"
            else:
                content = " "
            
            # Build walls
            # Top wall
            if r == 1:
                row_top += "+"
                if cell.get('N', 0) == 0:
                    row_top += "---"
                else:
                    row_top += "   "
            
            # Left wall and content
            if c == 1:
                if cell.get('W', 0) == 0:
                    row_mid += "|"
                else:
                    row_mid += " "
            
            row_mid += f" {content} "
            
            # Right wall
            if cell.get('E', 0) == 0:
                row_mid += "|"
            else:
                row_mid += " "
        
        if r == 1:
            row_top += "+"
            lines.append(row_top)
        
        lines.append(row_mid)
        
        # Bottom wall
        row_bottom = ""
        for c in range(1, m.cols + 1):
            cell = m.maze_map.get((r, c), {})
            row_bottom += "+"
            if cell.get('S', 0) == 0:
                row_bottom += "---"
            else:
                row_bottom += "   "
        row_bottom += "+"
        lines.append(row_bottom)
    
    return "\n".join(lines)


def simulate_terminal(m: maze, pathA: List[Coord], pathB: List[Coord], 
                     goalA: Coord, goalB: Coord, delay: float = 0.3):
    """Simulate the cooperative pathfinding in terminal."""
    clear = (lambda: os.system("cls")) if os.name == "nt" else (lambda: os.system("clear"))
    
    for step in range(len(pathA)):
        clear()
        print(render_maze_terminal(m, pathA[step], pathB[step], goalA, goalB, step))
        time.sleep(delay)
    
    print(f"\n{GREEN}Simulation Complete!{RESET}")
    print(f"Agent A completed in {len(pathA)-1} steps")
    print(f"Agent B completed in {len(pathB)-1} steps")


def run_cooperative_pathfinding():
    """Main function to run cooperative pathfinding with terminal visualization."""
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}COOPERATIVE PATH PLANNERS - TERMINAL MODE{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print("\nGenerating maze using pymaze...")
    
    # Create maze
    maze_size = 10
    m = maze(maze_size, maze_size)
    m.CreateMaze(loopPercent=30)
    
    # Define start and goal positions
    # In pymaze, (1,1) is top-left, (rows, cols) is bottom-right
    startA = (maze_size, maze_size)  # Bottom-right
    goalA = (1, 1)                    # Top-left
    
    startB = (maze_size, 1)           # Bottom-left
    goalB = (1, maze_size)            # Top-right
    
    print(f"\n{BLUE}Agent A:{RESET} Start {startA} → Goal {goalA}")
    print(f"{RED}Agent B:{RESET} Start {startB} → Goal {goalB}")
    print("\nPlanning cooperative paths...")
    
    # Plan cooperative paths
    pathA, pathB = cooperative_planning(m, startA, goalA, startB, goalB)
    
    print(f"\n{GREEN}✓ Paths found!{RESET}")
    print(f"Agent A: {len(pathA)-1} steps")
    print(f"Agent B: {len(pathB)-1} steps")
    
    print("\nStarting simulation in 2 seconds...")
    time.sleep(2)
    
    # Simulate in terminal
    simulate_terminal(m, pathA, pathB, goalA, goalB, delay=0.3)


if __name__ == "__main__":
    run_cooperative_pathfinding()
