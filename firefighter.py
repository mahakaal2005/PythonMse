import time
from collections import deque

class Firefighter:
    def init(self, agent_id, start_pos, symbol):
        self.id, self.pos, self.symbol, self.extinguished, self.path = agent_id, start_pos, symbol, [], []
    
    def bfs(self, start, goals, grid):
        if not goals: return None, []
        queue, visited = deque([(start, [])]), {start}
        while queue:
            pos, path = queue.popleft()
            if pos in goals: return pos, path + [pos]
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                nx, ny = pos[0] + dx, pos[1] + dy
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [pos]))
        return None, []


class FirefightingSystem:
    def init(self):
        self.rows = 10
        self.cols = 16
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Initial fires
        self.fires = [(1, 2), (3, 8), (7, 5), (2, 14), (8, 12), (5, 10)]
        self.all_fires = list(self.fires)
        
        # Firefighters
        self.agent1 = Firefighter(1, (0, 0), "🚒")
        self.agent2 = Firefighter(2, (self.rows-1, self.cols-1), "🚑")
        
        self.step = 0
        self.spread_interval = 8
        self.time_log = []
        
        self.assign_zones()
    
    def assign_zones(self):
        fires_with_dist = [(f, abs(f[0]-self.agent1.pos[0])+abs(f[1]-self.agent1.pos[1]), 
                           abs(f[0]-self.agent2.pos[0])+abs(f[1]-self.agent2.pos[1])) for f in self.fires]
        fires_with_dist.sort(key=lambda x: x[1] - x[2])
        mid = len(fires_with_dist) // 2
        self.agent1_fires, self.agent2_fires = [f[0] for f in fires_with_dist[:mid]], [f[0] for f in fires_with_dist[mid:]]
    
    def spread_fire(self):
        new_fires = [(fire[0]+dx, fire[1]+dy) for fire in self.fires for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)] 
                     if 0 <= fire[0]+dx < self.rows and 0 <= fire[1]+dy < self.cols and (fire[0]+dx, fire[1]+dy) not in self.fires]
        if new_fires:
            fire = new_fires[0]
            self.fires.append(fire)
            self.all_fires.append(fire)
            (self.agent1_fires if abs(fire[0]-self.agent1.pos[0])+abs(fire[1]-self.agent1.pos[1]) < 
             abs(fire[0]-self.agent2.pos[0])+abs(fire[1]-self.agent2.pos[1]) else self.agent2_fires).append(fire)
            return True
        return False
    
    def visualize(self):
        print("\n" * 2)
        print(f"{'='*60}")
        print(f"COOPERATIVE FIREFIGHTERS - Step {self.step}")
        print(f"{'='*60}\n")
        
        for i in range(self.rows):
            row = ""
            for j in range(self.cols):
                if (i, j) == self.agent1.pos:
                    row += "🚒 "
                elif (i, j) == self.agent2.pos:
                    row += "🚑 "
                elif (i, j) in self.fires:
                    row += "🔥 "
                elif (i, j) in self.agent1.extinguished:
                    row += "\033[94m·\033[0m "
                elif (i, j) in self.agent2.extinguished:
                    row += "\033[92m·\033[0m "
                else:
                    row += "⬜ "
            print(row)
        
        print(f"\n🚒 Agent 1 at {self.agent1.pos}, extinguished: {len(self.agent1.extinguished)}")
        print(f"🚑 Agent 2 at {self.agent2.pos}, extinguished: {len(self.agent2.extinguished)}")
        print(f"🔥 Active fires: {len(self.fires)}")
        time.sleep(0.15)
    
    def extinguish(self, agent, fires_list, symbol):
        if not fires_list: return False
        target, path = agent.bfs(agent.pos, fires_list, self.grid)
        if target and path:
            for pos in path:
                self.step += 1
                agent.pos = pos
                if pos not in agent.path: agent.path.append(pos)
                self.visualize()
                if self.step % self.spread_interval == 0 and self.spread_fire():
                    print(f"\n🔥 Fire spread at step {self.step}")
            agent.extinguished.append(target)
            self.fires.remove(target)
            fires_list.remove(target)
            self.time_log.append((self.step, len(self.fires)))
            print(f"\n{symbol} extinguished fire at {target}!")
            time.sleep(0.3)
            return True
        return False
    
    def run(self):
        print(f"\nStarting Cooperative Firefighting System...\n🚒 Agent 1: {self.agent1.pos}\n🚑 Agent 2: {self.agent2.pos}\n🔥 Fires: {len(self.fires)}")
        self.visualize()
        while self.fires:
            if self.step > 0 and self.step % self.spread_interval == 0 and self.spread_fire():
                print(f"\n🔥 Fire spread at step {self.step}")
            if not (self.extinguish(self.agent1, self.agent1_fires, "🚒") or self.extinguish(self.agent2, self.agent2_fires, "🚑")):
                break
        self.show_results()
    
    def show_results(self):
        print(f"\n{'='*60}\nALL FIRES EXTINGUISHED!\n{'='*60}")
        print(f"Total time: {self.step} steps\n🚒 Agent 1: {len(self.agent1.extinguished)}\n🚑 Agent 2: {len(self.agent2.extinguished)}\nSpread events: {len(self.all_fires)-6}")
        print(f"\n{'='*60}\nFIRE PROGRESS GRAPH\n{'='*60}\n")
        if self.time_log:
            max_fires = max(max(log[1] for log in self.time_log) + 1, len(self.all_fires))
            print("Fires")
            for fc in range(max_fires, -1, -1):
                print(f"{fc:2d} |" + "".join("🔥" if fires >= fc else "  " for _, fires in self.time_log))
            print("   +" + "-" * (len(self.time_log) * 2) + "\n    Time (steps)")
        print(f"{'='*60}\n")


if name == "main":
    system = FirefightingSystem()
    system.run()