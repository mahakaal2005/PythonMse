# =======================
# WAREHOUSE PICKUP TEAM - TERMINAL VISUALIZATION
# =======================

import os
import time
import random
from typing import List, Tuple, Dict, Set
from heapq import heappush, heappop

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


class WarehouseCooperative:
    """
    Two cooperative agents in a warehouse grid.
    - Items = '*'
    - Drop zone = 'D'
    - Agents: A (blue), B (red)
    - Step-by-step terminal visualization similar to pymaze output.
    """

    def __init__(self, rows: int = 8, cols: int = 10, num_items: int = 6, seed: int | None = 1):
        if seed is not None:
            random.seed(seed)

        self.rows = rows
        self.cols = cols
        self.num_items = num_items

        # We use a simple open warehouse (no internal obstacles),
        # but draw all cell walls in the ASCII view to look like a maze grid.
        # Positions are 1-based: (1,1) .. (rows, cols)

        # Drop zone near top middle
        self.drop: Coord = (1, self.cols // 2)

        # Agents start at bottom-left and bottom-right
        self.startA: Coord = (self.rows, 1)
        self.startB: Coord = (self.rows, self.cols)

        # Place items randomly inside (not on agents or drop)
        self.items: Set[Coord] = set()
        attempts = 0
        while len(self.items) < self.num_items and attempts < 1000:
            r = random.randint(2, self.rows - 1)  # avoid very top row
            c = random.randint(1, self.cols)
            if (r, c) not in (self.drop, self.startA, self.startB):
                self.items.add((r, c))
            attempts += 1

    # ---------- Basic grid utilities ----------

    def in_bounds(self, pos: Coord) -> bool:
        r, c = pos
        return 1 <= r <= self.rows and 1 <= c <= self.cols

    def neighbors(self, pos: Coord) -> List[Coord]:
        r, c = pos
        moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        res: List[Coord] = []
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if self.in_bounds((nr, nc)):
                res.append((nr, nc))
        return res

    def manhattan(self, a: Coord, b: Coord) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def astar(self, start: Coord, goal: Coord) -> List[Coord]:
        """Standard A* on open grid (no obstacles)."""
        open_heap: List[Tuple[int, int, Coord]] = []
        heappush(open_heap, (self.manhattan(start, goal), 0, start))
        came_from: Dict[Coord, Coord] = {}
        g_score: Dict[Coord, int] = {start: 0}
        visited: Set[Coord] = set()

        while open_heap:
            f, g, cur = heappop(open_heap)
            if cur in visited:
                continue
            visited.add(cur)

            if cur == goal:
                path = [cur]
                while cur in came_from:
                    cur = came_from[cur]
                    path.append(cur)
                return list(reversed(path))

            for nb in self.neighbors(cur):
                tentative = g + 1
                if nb not in g_score or tentative < g_score[nb]:
                    g_score[nb] = tentative
                    came_from[nb] = cur
                    heappush(open_heap, (tentative + self.manhattan(nb, goal), tentative, nb))

        raise RuntimeError(f"No path from {start} to {goal}")

    # ---------- Cooperative task planning ----------

    class AgentPlan:
        def __init__(self, start: Coord):
            self.pos: Coord = start
            self.time: int = 0
            self.path: List[Coord] = [start]
            self.distance: int = 0

    def plan_cooperative_paths(self):
        """Assign items to agents and build complete paths."""
        items_remaining = set(self.items)

        agentA = self.AgentPlan(self.startA)
        agentB = self.AgentPlan(self.startB)
        agents = [agentA, agentB]

        # Ideal (lower bound) distance: choose best initial agent per item
        ideal_distance = 0
        for item in items_remaining:
            best = min(
                (len(self.astar(start, item)) - 1) + (len(self.astar(item, self.drop)) - 1)
                for start in (self.startA, self.startB)
            )
            ideal_distance += best

        # Cooperative greedy assignment
        while items_remaining:
            best_cost = None
            best_choice = None  # (agent_idx, item, path_to_item, path_to_drop)

            for idx, ag in enumerate(agents):
                for item in items_remaining:
                    p1 = self.astar(ag.pos, item)
                    p2 = self.astar(item, self.drop)
                    travel = (len(p1) - 1) + (len(p2) - 1)
                    finish_time = ag.time + travel
                    if best_cost is None or finish_time < best_cost:
                        best_cost = finish_time
                        best_choice = (idx, item, p1, p2)

            idx, item, p1, p2 = best_choice
            items_remaining.remove(item)
            ag = agents[idx]

            # Append paths (avoiding double count of starting cell)
            for pos in p1[1:]:
                ag.path.append(pos)
            for pos in p2[1:]:
                ag.path.append(pos)

            travel_steps = (len(p1) - 1) + (len(p2) - 1)
            ag.distance += travel_steps
            ag.time += travel_steps
            ag.pos = self.drop

        pathA, pathB = agentA.path, agentB.path

        # Equalize lengths for synchronized simulation
        L = max(len(pathA), len(pathB))
        while len(pathA) < L:
            pathA.append(pathA[-1])
        while len(pathB) < L:
            pathB.append(pathB[-1])

        total_distance = agentA.distance + agentB.distance
        efficiency = (ideal_distance / total_distance * 100) if total_distance > 0 else 0.0

        return pathA, pathB, agentA, agentB, ideal_distance, total_distance, efficiency

    # ---------- Rendering (similar to pymaze style) ----------

    def render_warehouse_terminal(
        self,
        posA: Coord,
        posB: Coord,
        remaining_items: Set[Coord],
        step: int,
    ) -> str:
        lines: List[str] = []
        lines.append(f"\n{CYAN}{'='*60}{RESET}")
        lines.append(
            f"{CYAN}Step {step:3d}{RESET} | "
            f"{BLUE}Agent A: {posA}{RESET} | "
            f"{RED}Agent B: {posB}{RESET} | "
            f"{YELLOW}Items left: {len(remaining_items)}{RESET}"
        )
        lines.append(f"{CYAN}{'='*60}{RESET}\n")

        # Each cell is boxed: +---+   | A |
        for r in range(1, self.rows + 1):
            # Top border of row
            row_top = ""
            row_mid = ""

            for c in range(1, self.cols + 1):
                coord = (r, c)

                # Cell content
                if coord == posA and coord == posB:
                    content = f"{YELLOW}@{RESET}"
                elif coord == posA:
                    content = f"{BLUE}A{RESET}"
                elif coord == posB:
                    content = f"{RED}B{RESET}"
                elif coord == self.drop:
                    content = f"{GREEN}D{RESET}"
                elif coord in remaining_items:
                    content = f"{YELLOW}*{RESET}"
                else:
                    content = " "

                # Top walls (everywhere, full grid look)
                row_top += "+" + "---"

                # Middle row: left wall + content + right wall
                if c == 1:
                    row_mid += "|"
                row_mid += f" {content} "
                row_mid += "|"

            row_top += "+"
            lines.append(row_top)
            lines.append(row_mid)

        # Bottom border
        row_bottom = ""
        for c in range(1, self.cols + 1):
            row_bottom += "+" + "---"
        row_bottom += "+"
        lines.append(row_bottom)

        return "\n".join(lines)

    def simulate_terminal(self, delay: float = 0.3):
        pathA, pathB, agentA, agentB, ideal_dist, total_dist, eff = self.plan_cooperative_paths()

        steps = len(pathA)
        remaining_items = set(self.items)

        clear = (lambda: os.system("cls")) if os.name == "nt" else (lambda: os.system("clear"))

        for step in range(steps):
            posA = pathA[step]
            posB = pathB[step]

            # Collect items if stepped on
            if posA in remaining_items:
                remaining_items.remove(posA)
            if posB in remaining_items:
                remaining_items.remove(posB)

            clear()
            print(self.render_warehouse_terminal(posA, posB, remaining_items, step))
            time.sleep(delay)

        print(f"\n{GREEN}Simulation Complete!{RESET}")
        print(f"Agent A path steps (moves): {len(pathA)-1}")
        print(f"Agent B path steps (moves): {len(pathB)-1}")
        print(f"Ideal total distance : {ideal_dist}")
        print(f"Actual total distance: {total_dist}")
        print(f"Efficiency           : {eff:.2f}%")
        print()


def run_warehouse_sim():
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}WAREHOUSE PICKUP TEAM - TERMINAL MODE{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")
    print("\nTwo agents (A & B) will collect '*' items and deliver them to 'D'.")
    input("Press Enter to start...")

    sim = WarehouseCooperative(rows=8, cols=10, num_items=6, seed=3)
    try:
        sim.simulate_terminal(delay=0.3)
    except Exception as e:
        print("Simulation failed:", e)


if __name__ == "__main__":
    run_warehouse_sim()
