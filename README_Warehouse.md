# Warehouse Pickup Team - README

## Overview
This program simulates a cooperative warehouse management system where two robotic agents work together to collect items and deliver them to a drop zone. The system uses intelligent task allocation and pathfinding algorithms to optimize efficiency.

---

## AI Concepts Used

### 1. **A* Pathfinding Algorithm**
- **What it is**: Optimal pathfinding algorithm that finds shortest path between two points
- **Components**:
  - **g(n)**: Actual cost from start to current node
  - **h(n)**: Heuristic estimate (Manhattan distance) to goal
  - **f(n) = g(n) + h(n)**: Total estimated cost
- **Why optimal**: Uses admissible heuristic, guarantees shortest path

### 2. **Greedy Task Allocation**
- **Strategy**: Assign each item to the agent that can complete it fastest
- **Decision criteria**: Minimize completion time for each task
- **Process**:
  1. Calculate cost for each agent to pick up each remaining item
  2. Choose agent-item pair with lowest cost
  3. Assign task and update agent state
  4. Repeat until all items assigned

### 3. **Multi-Agent Coordination**
- **Cooperative behavior**: Agents work together toward common goal
- **Task distribution**: Items divided between agents based on proximity
- **Sequential execution**: Each agent follows its assigned task sequence
- **No conflicts**: Tasks assigned such that agents don't interfere

### 4. **Manhattan Distance Heuristic**
- **Formula**: `|x1 - x2| + |y1 - y2|`
- **Purpose**: Estimate distance in grid with 4-directional movement
- **Properties**:
  - Admissible: Never overestimates actual distance
  - Consistent: Satisfies triangle inequality
  - Efficient: O(1) computation time

### 5. **Graph Search**
- **State space**: All positions in warehouse grid
- **Actions**: Move up, down, left, right
- **Goal test**: Reach target position (item or drop zone)
- **Path reconstruction**: Backtrack from goal to start using parent pointers

### 6. **Performance Metrics**
- **Ideal distance**: Theoretical minimum if each item assigned optimally
- **Actual distance**: Total distance traveled by both agents
- **Efficiency**: `(Ideal / Actual) × 100%`
- **Purpose**: Measure quality of task allocation

---

## Code Structure

### Main Class: WarehouseCooperative

#### 1. **Initialization (`__init__`)**
```python
def __init__(self, rows=8, cols=10, num_items=6, seed=None)
```
- **Purpose**: Set up warehouse environment
- **Creates**:
  - Grid dimensions (rows × cols)
  - Drop zone position (top center)
  - Agent starting positions (bottom corners)
  - Random item positions
- **Parameters**:
  - `rows`, `cols`: Warehouse dimensions
  - `num_items`: Number of items to collect
  - `seed`: Random seed for reproducibility

#### 2. **Grid Utilities**

**in_bounds(pos)**
```python
def in_bounds(self, pos: Coord) -> bool
```
- Checks if position is within warehouse boundaries
- Returns True if valid, False otherwise

**neighbors(pos)**
```python
def neighbors(self, pos: Coord) -> List[Coord]
```
- Returns list of adjacent positions (up, down, left, right)
- Only includes positions within bounds
- Used by pathfinding algorithm

**manhattan(a, b)**
```python
def manhattan(self, a: Coord, b: Coord) -> int
```
- Calculates Manhattan distance between two positions
- Used as heuristic for A* algorithm

#### 3. **A* Pathfinding (`astar`)**
```python
def astar(self, start: Coord, goal: Coord) -> List[Coord]
```
- **Purpose**: Find shortest path from start to goal
- **Algorithm**:
  1. Initialize open heap with start position
  2. Pop position with lowest f-score
  3. If goal reached, reconstruct path
  4. Otherwise, explore neighbors
  5. Update costs and add to heap
  6. Repeat until goal found
- **Returns**: List of positions from start to goal
- **Data structures**:
  - Priority queue (heap) for efficient node selection
  - Dictionary for tracking costs (g_score)
  - Dictionary for path reconstruction (came_from)
  - Set for visited nodes

#### 4. **Agent Plan Class**
```python
class AgentPlan:
    def __init__(self, start: Coord):
        self.pos: Coord = start      # Current position
        self.time: int = 0           # Current time step
        self.path: List[Coord] = []  # Complete path
        self.distance: int = 0       # Total distance traveled
```
- **Purpose**: Track agent state during planning
- **Attributes**:
  - `pos`: Where agent currently is
  - `time`: How long agent has been working
  - `path`: Sequence of positions agent will visit
  - `distance`: Total steps taken

#### 5. **Cooperative Planning (`plan_cooperative_paths`)**
```python
def plan_cooperative_paths(self)
```
- **Purpose**: Assign items to agents and plan complete paths
- **Algorithm**:

**Step 1: Calculate Ideal Distance**
```python
for item in items_remaining:
    best = min(distance from each agent to item + item to drop)
    ideal_distance += best
```
- Theoretical minimum if perfect assignment

**Step 2: Greedy Task Assignment**
```python
while items_remaining:
    for each agent:
        for each item:
            calculate: time to reach item + time to drop
    assign item with minimum completion time
    update agent position and time
```
- Iteratively assign closest item to fastest agent

**Step 3: Path Construction**
```python
for each assigned task:
    path_to_item = astar(agent.pos, item)
    path_to_drop = astar(item, drop)
    agent.path += path_to_item + path_to_drop
```
- Build complete path for each agent

**Step 4: Synchronization**
```python
L = max(len(pathA), len(pathB))
while len(pathA) < L: pathA.append(pathA[-1])
while len(pathB) < L: pathB.append(pathB[-1])
```
- Pad shorter path so agents move in lockstep

**Returns**:
- `pathA`, `pathB`: Complete paths for both agents
- `agentA`, `agentB`: Agent plan objects with statistics
- `ideal_distance`: Theoretical minimum
- `total_distance`: Actual distance traveled
- `efficiency`: Performance percentage

#### 6. **Visualization (`render_warehouse_terminal`)**
```python
def render_warehouse_terminal(self, posA, posB, remaining_items, step)
```
- **Purpose**: Create ASCII art representation of warehouse
- **Elements**:
  - Grid with walls: `+---+` and `|   |`
  - Agent A: Blue 'A'
  - Agent B: Red 'B'
  - Both agents at same position: Yellow '@'
  - Drop zone: Green 'D'
  - Items: Yellow '*'
  - Empty space: ' '
- **Header**: Shows step number, agent positions, items remaining
- **Colors**: ANSI escape codes for terminal colors

#### 7. **Simulation (`simulate_terminal`)**
```python
def simulate_terminal(self, delay=0.3)
```
- **Purpose**: Animate warehouse operations step-by-step
- **Process**:
  1. Plan cooperative paths
  2. For each time step:
     - Clear screen
     - Update item collection (if agent on item)
     - Render current state
     - Wait for delay
  3. Display final statistics
- **Statistics shown**:
  - Path lengths for each agent
  - Ideal vs actual distance
  - Efficiency percentage

---

## How It Works

### Complete Workflow

**1. Environment Setup**
```
Warehouse: 8 rows × 10 columns
Drop zone: (1, 5) - top center
Agent A starts: (8, 1) - bottom left
Agent B starts: (8, 10) - bottom right
Items: 6 randomly placed
```

**2. Task Planning Phase**

Calculate ideal distance:
```
For each item:
    distA = distance from A to item + item to drop
    distB = distance from B to item + item to drop
    ideal += min(distA, distB)
```

Greedy assignment loop:
```
While items remain:
    For each (agent, item) pair:
        cost = agent.time + distance(agent.pos, item) + distance(item, drop)
    
    Select pair with minimum cost
    Assign item to agent
    Update agent.pos = drop
    Update agent.time += travel_time
    Remove item from remaining
```

**3. Path Execution**

For each assigned task:
```
1. Plan path from current position to item (A*)
2. Plan path from item to drop zone (A*)
3. Append both paths to agent's complete path
4. Update agent statistics
```

**4. Simulation**

For each time step:
```
1. Get agent positions from paths
2. Check if agents are on items → collect them
3. Render warehouse state
4. Display on terminal
5. Wait for animation delay
```

**5. Results**
```
Display:
- Total steps for each agent
- Ideal distance (theoretical best)
- Actual distance (what happened)
- Efficiency = (ideal / actual) × 100%
```

---

## Key AI Techniques Explained

### Greedy Task Allocation

**Why Greedy?**
- Simple and fast
- Good approximation of optimal
- Works well for small number of agents

**How it works**:
```python
best_cost = None
for agent in agents:
    for item in items:
        cost = agent.time + travel_distance
        if cost < best_cost:
            best_choice = (agent, item)
```

**Limitation**: May not be globally optimal, but efficient

### A* Search Details

**Open List (Priority Queue)**:
```python
heappush(open_heap, (f_score, g_score, position))
```
- Always explores most promising node first
- f_score = g_score + heuristic
- Ensures optimal path

**Closed List (Visited Set)**:
```python
if position in visited:
    continue
visited.add(position)
```
- Prevents reprocessing nodes
- Improves efficiency

**Path Reconstruction**:
```python
path = [goal]
current = goal
while current in came_from:
    current = came_from[current]
    path.append(current)
return reversed(path)
```
- Backtrack from goal to start
- Uses parent pointers (came_from)

### Efficiency Calculation

**Ideal Distance**:
- Sum of best possible assignments
- Lower bound on performance
- Assumes perfect coordination

**Actual Distance**:
- Sum of all steps taken by both agents
- Real performance measure

**Efficiency**:
```python
efficiency = (ideal_distance / actual_distance) × 100%
```
- 100% = optimal performance
- Lower = more room for improvement

---

## Running the Program

### Requirements
```bash
# No external dependencies needed
# Uses only Python standard library
```

### Execution
```bash
python Warehouse.py
```

### Expected Output
```
============================================================
WAREHOUSE PICKUP TEAM - TERMINAL MODE
============================================================

Two agents (A & B) will collect '*' items and deliver them to 'D'.
Starting simulation in 2 seconds...

[Animated warehouse grid showing agents moving]

Simulation Complete!
Agent A path steps (moves): 42
Agent B path steps (moves): 42
Ideal total distance : 71
Actual total distance: 75
Efficiency           : 94.67%
```

---

## Customization Options

### Warehouse Size
```python
sim = WarehouseCooperative(rows=10, cols=15, num_items=8, seed=5)
```

### Number of Items
```python
num_items=10  # More items = more complex coordination
```

### Animation Speed
```python
sim.simulate_terminal(delay=0.5)  # Slower animation
sim.simulate_terminal(delay=0.1)  # Faster animation
```

### Random Seed
```python
seed=42  # Reproducible results
seed=None  # Different layout each time
```

---

## Advantages of This Approach

1. **Simple and Efficient**: Greedy allocation is fast and effective
2. **Scalable**: Can handle more items easily
3. **Visual**: Clear terminal animation shows behavior
4. **Measurable**: Efficiency metric quantifies performance
5. **Flexible**: Easy to modify warehouse layout

---

## Limitations

1. **Greedy Not Optimal**: May not find best overall assignment
2. **No Collision Avoidance**: Agents don't avoid each other (paths independent)
3. **Static Planning**: All decisions made upfront, no replanning
4. **Two Agents Only**: Current implementation limited to 2 agents
5. **No Obstacles**: Open warehouse, no internal walls

---

## Learning Outcomes

By studying this code, you will understand:
- A* pathfinding algorithm implementation
- Greedy task allocation strategies
- Multi-agent coordination basics
- Heuristic search methods
- Performance metric calculation
- Terminal-based visualization
- Object-oriented design for agent systems

---

## Possible Improvements

### 1. **Better Task Allocation**
- Use Hungarian algorithm for optimal assignment
- Consider future tasks when assigning current task
- Balance workload between agents

### 2. **Collision Avoidance**
- Implement Space-Time A* (like Cooperative_Path_Planners.py)
- Add reservation system for cells
- Prevent agents from blocking each other

### 3. **Dynamic Replanning**
- Replan when new items appear
- Handle agent failures
- Adapt to changing conditions

### 4. **More Agents**
- Extend to 3+ agents
- Implement better coordination strategies
- Handle more complex scenarios

### 5. **Obstacles**
- Add walls and barriers
- Use more complex maze layouts
- Integrate with pymaze library

### 6. **Priority Items**
- Some items more urgent than others
- Weighted task allocation
- Time-sensitive deliveries

---

## Comparison with Cooperative_Path_Planners.py

| Feature | Warehouse.py | Cooperative_Path_Planners.py |
|---------|--------------|------------------------------|
| **Environment** | Open grid | Maze with walls |
| **Task** | Collect items | Reach goal |
| **Collision Avoidance** | No | Yes (Space-Time A*) |
| **Planning** | Greedy allocation | Sequential reservation |
| **Complexity** | Simpler | More sophisticated |
| **Use Case** | Task assignment | Path coordination |

---

## Real-World Applications

1. **Warehouse Robotics**: Amazon fulfillment centers
2. **Delivery Drones**: Package delivery coordination
3. **Manufacturing**: Assembly line robots
4. **Agriculture**: Harvesting robots
5. **Cleaning Robots**: Office/home cleaning coordination

---

## References

- A* Algorithm: Hart, Nilsson, Raphael (1968)
- Task Allocation: Gerkey & Matarić (2004) - Multi-Robot Task Allocation
- Greedy Algorithms: Cormen et al. - Introduction to Algorithms
- Multi-Agent Systems: Wooldridge (2009)
