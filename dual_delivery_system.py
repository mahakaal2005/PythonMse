# =======================
# DUAL DRONE DELIVERY - TERMINAL VISUALIZATION
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


class DualDroneDelivery:
    """
    Two drones deliver packages 'P' to different locations with minimal overlap.
    - Drones: A (blue), B (red)
    - Packages: P (yellow)
    - Uses A* and greedy task assignment
    - Output: step-by-step terminal maze + total delivery time + coverage heatmap
    """

    def __init__(
        self,
        rows: int = 10,
        cols: int = 14,
        num_packages: int = 6,
        seed: int | None = 5,
    ):
        if seed is not None:
            random.seed(seed)

        self.rows = rows
        self.cols = cols
        self.num_packages = num_packages

        # Drones start near bottom-left and bottom-right
        self.startA: Coord = (rows, 2)
        self.startB: Coord = (rows, cols - 1)

        # Packages: each package is just a delivery location
        self.packages: Set[Coord] = set()
        attempts = 0
        while len(self.packages) < self.num_packages and attempts < 1000:
            r = random.randint(2, self.rows - 1)
            c = random.randint(1, self.cols)
            if (r, c) not in (self.startA, self.startB):
                self.packages.add((r, c))
            attempts += 1

    # ---------- Grid + A* utilities ----------

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
        """Standard A* pathfinding on open grid."""
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

        raise RuntimeError(f"No path found from {start} to {goal}")

    # ---------- Cooperative planning (greedy assignment) ----------

    class DronePlan:
        def __init__(self, start: Coord):
            self.pos: Coord = start
            self.time: int = 0          # schedule time
            self.path: List[Coord] = [start]
            self.distance: int = 0

    def plan_deliveries(self):
        """
        Cooperative greedy task assignment:
        at each step, pick (drone, package) pair that finishes earliest.
        Also compute an 'ideal' lower bound for efficiency.
        """
        drones = [self.DronePlan(self.startA), self.DronePlan(self.startB)]
        remaining = set(self.packages)

        # Ideal lower bound: sum of minimum distances from each package to nearest starting drone
        ideal_distance = 0
        for p in remaining:
            distA = len(self.astar(self.startA, p)) - 1
            distB = len(self.astar(self.startB, p)) - 1
            ideal_distance += min(distA, distB)

        while remaining:
            best_cost = None
            best_choice = None  # (drone_idx, package, path)

            for i, dr in enumerate(drones):
                for pkg in remaining:
                    path = self.astar(dr.pos, pkg)
                    cost = len(path) - 1
                    finish_time = dr.time + cost
                    if best_cost is None or finish_time < best_cost:
                        best_cost = finish_time
                        best_choice = (i, pkg, path)

            i, pkg, path = best_choice
            remaining.remove(pkg)
            dr = drones[i]

            # Append path (excluding starting cell to avoid duplicates)
            for pos in path[1:]:
                dr.path.append(pos)

            steps = len(path) - 1
            dr.distance += steps
            dr.time += steps
            dr.pos = pkg  # finished delivery at package location

        pathA, pathB = drones[0].path, drones[1].path

        # Equalize length for synchronous step-by-step simulation
        L = max(len(pathA), len(pathB))
        while len(pathA) < L:
            pathA.append(pathA[-1])
        while len(pathB) < L:
            pathB.append(pathB[-1])

        total_distance = drones[0].distance + drones[1].distance
        makespan = max(drones[0].time, drones[1].time)
        # Efficiency: 100% when we achieve the theoretical minimum
        efficiency = (ideal_distance / total_distance * 100) if total_distance > 0 else 100.0
        # Cap at 100% in case of rounding errors
        efficiency = min(efficiency, 100.0)

        return pathA, pathB, ideal_distance, total_distance, makespan, efficiency

    # ---------- Rendering (similar to your other projects) ----------

    def render_step(
        self,
        posA: Coord,
        posB: Coord,
        undelivered: Set[Coord],
        step: int,
        prevA: Coord = None,
        prevB: Coord = None,
        delivered_this_step: List[Coord] = None
    ) -> str:
        """Render the grid in pymaze-like box style with detailed status."""
        lines: List[str] = []
        lines.append(f"\n{CYAN}{'='*70}{RESET}")
        lines.append(
            f"{CYAN}Step {step:3d}{RESET} | "
            f"{BLUE}Drone A: {posA}{RESET} | "
            f"{RED}Drone B: {posB}{RESET} | "
            f"{YELLOW}Packages left: {len(undelivered)}{RESET}"
        )
        lines.append(f"{CYAN}{'='*70}{RESET}")
        
        # Add movement and action details
        if prevA and prevB:
            moveA = "STATIONARY" if posA == prevA else f"MOVED from {prevA} to {posA}"
            moveB = "STATIONARY" if posB == prevB else f"MOVED from {prevB} to {posB}"
            lines.append(f"{BLUE}Drone A:{RESET} {moveA}")
            lines.append(f"{RED}Drone B:{RESET} {moveB}")
            
            # Show deliveries
            if delivered_this_step:
                for pkg in delivered_this_step:
                    if pkg == posA:
                        lines.append(f"{GREEN}✓ Drone A delivered package at {pkg}!{RESET}")
                    if pkg == posB:
                        lines.append(f"{GREEN}✓ Drone B delivered package at {pkg}!{RESET}")
            
            # Calculate distances traveled
            distA = self.manhattan(prevA, posA)
            distB = self.manhattan(prevB, posB)
            lines.append(f"Distance this step: A={distA}, B={distB}")
        
        lines.append(f"Remaining packages: {sorted(list(undelivered))}")
        lines.append("")

        for r in range(1, self.rows + 1):
            row_top = ""
            row_mid = ""
            for c in range(1, self.cols + 1):
                coord = (r, c)

                # content
                if coord == posA and coord == posB:
                    content = f"{YELLOW}@{RESET}"
                elif coord == posA:
                    content = f"{BLUE}A{RESET}"
                elif coord == posB:
                    content = f"{RED}B{RESET}"
                elif coord in undelivered:
                    content = f"{YELLOW}P{RESET}"
                else:
                    content = " "

                # top border cell
                row_top += "+" + "---"

                # middle row with vertical separators
                if c == 1:
                    row_mid += "|"
                row_mid += f" {content} |"

            lines.append(row_top + "+")
            lines.append(row_mid)

        # bottom border
        bottom = "+" + ("---+" * self.cols)
        lines.append(bottom)

        return "\n".join(lines)

    # ---------- Heatmap rendering ----------

    def render_heatmap(self, coverage: Dict[Coord, int]) -> str:
        """
        Enhanced heatmap with better visibility and statistics.
        Uses background colors and intensity symbols for better visualization.
        """
        lines: List[str] = []
        lines.append(f"\n{MAGENTA}{'='*70}{RESET}")
        lines.append(f"{MAGENTA}DRONE COVERAGE HEATMAP - TRAFFIC ANALYSIS{RESET}")
        lines.append(f"{MAGENTA}{'='*70}{RESET}")
        
        # Calculate statistics
        max_visits = max(coverage.values()) if coverage else 0
        total_visits = sum(coverage.values())
        unique_cells = len([v for v in coverage.values() if v > 0])
        total_cells = self.rows * self.cols
        coverage_percent = (unique_cells / total_cells) * 100
        
        lines.append(f"Statistics:")
        lines.append(f"  • Total cell visits: {total_visits}")
        lines.append(f"  • Unique cells visited: {unique_cells}/{total_cells} ({coverage_percent:.1f}%)")
        lines.append(f"  • Maximum visits per cell: {max_visits}")
        lines.append(f"  • Average visits per visited cell: {total_visits/unique_cells:.1f}" if unique_cells > 0 else "")
        lines.append("")

        # Enhanced color mapping with background colors
        def get_cell_display(visits):
            if visits == 0:
                return "   "  # Empty space
            elif visits == 1:
                return f"\033[42m 1 \033[0m"  # Green background
            elif visits == 2:
                return f"\033[43m 2 \033[0m"  # Yellow background
            elif visits == 3:
                return f"\033[45m 3 \033[0m"  # Magenta background
            elif visits <= 5:
                return f"\033[41m {visits} \033[0m"  # Red background
            else:
                return f"\033[41;1m{visits:2d}\033[0m"  # Bright red background

        for r in range(1, self.rows + 1):
            row_top = ""
            row_mid = ""
            for c in range(1, self.cols + 1):
                coord = (r, c)
                visits = coverage.get(coord, 0)
                content = get_cell_display(visits)

                # top border
                row_top += "+" + "---"
                # middle
                if c == 1:
                    row_mid += "|"
                row_mid += content + "|"

            lines.append(row_top + "+")
            lines.append(row_mid)

        bottom = "+" + ("---+" * self.cols)
        lines.append(bottom)

        # Enhanced legend with color samples
        lines.append("\nLegend (visits per cell):")
        lines.append(f"  \033[42m 1 \033[0m = 1 visit (low traffic)")
        lines.append(f"  \033[43m 2 \033[0m = 2 visits (moderate traffic)")
        lines.append(f"  \033[45m 3 \033[0m = 3 visits (high traffic)")
        lines.append(f"  \033[41m 4+ \033[0m = 4+ visits (very high traffic)")
        lines.append(f"     = 0 visits (unused space)")
        
        # Efficiency analysis
        if unique_cells > 0:
            overlap_cells = len([v for v in coverage.values() if v > 1])
            overlap_percent = (overlap_cells / unique_cells) * 100
            lines.append(f"\nEfficiency Analysis:")
            lines.append(f"  • Cells with overlap: {overlap_cells}/{unique_cells} ({overlap_percent:.1f}%)")
            if overlap_percent < 20:
                lines.append(f"  • {GREEN}Excellent coordination - minimal overlap!{RESET}")
            elif overlap_percent < 40:
                lines.append(f"  • {YELLOW}Good coordination - some overlap{RESET}")
            else:
                lines.append(f"  • {RED}High overlap - coordination could be improved{RESET}")
        
        return "\n".join(lines)

    # ---------- Simulation ----------

    def simulate_terminal(self, delay: float = 0.25):
        pathA, pathB, ideal_dist, total_dist, makespan, eff = self.plan_deliveries()

        undelivered = set(self.packages)
        coverage: Dict[Coord, int] = {}
        total_distA = 0
        total_distB = 0

        clear = (lambda: os.system("cls")) if os.name == "nt" else (lambda: os.system("clear"))

        for step in range(len(pathA)):
            posA = pathA[step]
            posB = pathB[step]
            
            prevA = pathA[step-1] if step > 0 else None
            prevB = pathB[step-1] if step > 0 else None

            # Mark coverage
            coverage[posA] = coverage.get(posA, 0) + 1
            coverage[posB] = coverage.get(posB, 0) + 1
            
            # Track distances
            if prevA:
                total_distA += self.manhattan(prevA, posA)
            if prevB:
                total_distB += self.manhattan(prevB, posB)

            # Check for deliveries this step
            delivered_this_step = []
            if posA in undelivered:
                undelivered.remove(posA)
                delivered_this_step.append(posA)
            if posB in undelivered:
                undelivered.remove(posB)
                delivered_this_step.append(posB)

            clear()
            print(self.render_step(posA, posB, undelivered, step, prevA, prevB, delivered_this_step))
            
            # Show cumulative stats
            print(f"Cumulative distance: A={total_distA}, B={total_distB}, Total={total_distA + total_distB}")
            print(f"Progress: {len(self.packages) - len(undelivered)}/{len(self.packages)} packages delivered")
            
            time.sleep(delay)

        print(f"\n{GREEN}DELIVERIES COMPLETE!{RESET}")
        print(f"Total delivery time (makespan): {makespan} steps")
        print(f"Ideal distance (lower bound)   : {ideal_dist}")
        print(f"Actual total distance          : {total_dist}")
        print(f"Efficiency                     : {eff:.1f}%")
        if eff >= 99.9:
            print(f"{GREEN}Perfect efficiency achieved!{RESET}")
        elif eff >= 90:
            print(f"{GREEN}Excellent efficiency!{RESET}")
        elif eff >= 80:
            print(f"{YELLOW}Good efficiency{RESET}")
        else:
            print(f"{RED}Room for improvement{RESET}")

        # Enhanced heatmap with statistics
        print(self.render_heatmap(coverage))
        
        # Final efficiency summary
        print(f"\n{CYAN}FINAL PERFORMANCE SUMMARY:{RESET}")
        print(f"{'='*50}")
        print(f"Makespan (completion time): {makespan} steps")
        print(f"Total distance traveled   : {total_dist} units")
        print(f"Theoretical minimum       : {ideal_dist} units")
        print(f"Algorithm efficiency      : {eff:.1f}%")
        if eff >= 99.9:
            print(f"Performance rating        : {GREEN}OPTIMAL{RESET}")
        elif eff >= 90:
            print(f"Performance rating        : {GREEN}EXCELLENT{RESET}")
        elif eff >= 80:
            print(f"Performance rating        : {YELLOW}GOOD{RESET}")
        else:
            print(f"Performance rating        : {RED}NEEDS IMPROVEMENT{RESET}")
        print(f"Drone A distance          : {total_distA} units")
        print(f"Drone B distance          : {total_distB} units")
        print(f"Load balance ratio        : {min(total_distA, total_distB)/max(total_distA, total_distB):.2f}" if max(total_distA, total_distB) > 0 else "N/A")


def run_dual_drone_delivery():
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}DUAL DRONE DELIVERY - ENHANCED VISUALIZATION{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")
    print("Two drones (A=Blue, B=Red) deliver packages (P=Yellow) with optimal coordination.")
    print("Features: Real-time tracking, coverage heatmap, efficiency analysis")
    print("Goal: Achieve 100% efficiency with minimal path overlap\n")
    input("Press Enter to start...")

    sim = DualDroneDelivery(rows=10, cols=14, num_packages=6, seed=5)
    try:
        sim.simulate_terminal(delay=0.25)
    except Exception as e:
        print("Simulation failed:", e)


if __name__ == "__main__":
    run_dual_drone_delivery()