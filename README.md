# Multi-Agent Cooperative Systems - Project Documentation

## Overview
This project demonstrates two cooperative multi-agent systems where intelligent agents work together to solve complex problems efficiently.

## Project 1: Dual Maze Navigator

### Problem Statement
Two agents must cooperatively explore a maze and collect all scattered keys. The challenge is to minimize overlap and maximize efficiency through coordination.

### Technical Components

#### 1. Maze Generation (Recursive Backtracking Algorithm)
**What it does:** Creates a perfect maze with guaranteed paths between all points.

**How it works:**
- Starts with a grid filled with walls
- Carves passages by randomly removing walls
- Uses recursion to ensure all areas are connected
- Adds extra passages (20% of cells) to reduce linearity

**Why this approach:**
- Guarantees solvable mazes
- Creates interesting, non-trivial paths
- Balances complexity with navigability

#### 2. Agent 1: Breadth-First Search (BFS)
**What it does:** Finds the shortest path to the nearest uncollected key.

**How it works:**
- Explores maze level by level (like ripples in water)
- Maintains a queue of positions to visit
- Always finds the shortest path to target
- Time Complexity: O(V + E) where V=vertices, E=edges

**Why BFS:**
- Optimal for finding nearest targets
- Guarantees shortest path
- Systematic exploration pattern

#### 3. Agent 2: Depth-First Search (DFS)
**What it does:** Explores deeply into the maze to find distant keys.

**How it works:**
- Explores one path as far as possible before backtracking
- Uses recursion with depth limit (100 levels)
- Prioritizes unexplored areas
- Complements BFS by exploring different regions

**Why DFS:**
- Explores different areas than BFS
- Good for finding distant targets
- Memory efficient for deep exploration

#### 4. Cooperation Mechanisms

**A. Target Claiming System**
- Each agent "claims" a key before pursuing it
- Prevents both agents from targeting the same key
- Reduces wasted effort and overlap

**B. Real-Time Communication**
- Agents share visited cells every move
- Creates shared knowledge base
- Prevents redundant exploration
- Enables dynamic coordination

**C. Territory Assignment**
- Keys assigned to nearest agent
- Uses Manhattan distance (|x1-x2| + |y1-y2|)
- Reassigned every 30 moves for adaptability
- Balances workload between agents

**D. Conflict Resolution**
- If agent reaches already-collected key, immediately finds new target
- Stall detection: after 50 moves without progress, ignores claims
- Ensures system never deadlocks

### Performance Metrics

**Cooperation Efficiency:**
```
Efficiency = (Unique cells explored / Total cells explored by both) × 100%
```
- Target: 100% (no overlap)
- Achieved: 73-100% depending on maze layout

**Key Statistics:**
- Keys Collected: Tracks progress
- Path Length: Total moves per agent
- Visited Cells: Unique cells explored
- Shared Knowledge: Combined exploration area


---

## Project 2: Cleaning Crew Coordinator

### Problem Statement
Two cleaning robots must efficiently clean a dirty floor with obstacles, dividing work to avoid overlap and maximize cleaning speed.

### Technical Components

#### 1. Environment Generation
**What it does:** Creates a 2D grid representing a room with obstacles and dirty cells.

**Components:**
- Borders: Walls around the perimeter
- Obstacles: Random furniture (20% of space)
- Dirty Cells: 40% of floor area needs cleaning
- Starting Positions: Bots start in opposite corners

#### 2. Bot 1: A* Pathfinding Algorithm
**What it does:** Finds optimal path to target using both distance traveled and estimated remaining distance.

**How it works:**
```
f(n) = g(n) + h(n)
where:
- g(n) = actual cost from start to node n
- h(n) = estimated cost from n to goal (heuristic)
- f(n) = total estimated cost
```

**Algorithm Steps:**
1. Add start position to priority queue
2. Pop position with lowest f(n) score
3. If goal reached, reconstruct path
4. Otherwise, explore neighbors
5. Calculate f(n) for each neighbor
6. Repeat until goal found


**Why A*:**
- Optimal pathfinding (guaranteed shortest path)
- Efficient: explores fewer nodes than BFS
- Balances exploration with goal-directed search
- Industry standard for game AI and robotics

#### 3. Bot 2: Greedy Best-First Search
**What it does:** Quickly finds paths by always moving toward the goal.

**How it works:**
```
Priority = h(n) only
where h(n) = Manhattan distance to goal
```

**Algorithm Steps:**
1. Always choose the neighbor closest to goal
2. Faster than A* but may not find optimal path
3. Good for quick decisions in dynamic environments

**Why Greedy Search:**
- Faster computation than A*
- Good for real-time systems
- Complements A* by providing speed vs optimality tradeoff
- Explores different paths than A*

#### 4. Cooperation Mechanisms

**A. Strict Target Exclusion**
```python
excluded = bot2_assigned.union(bot2_cleaned)
bot1_target = find_nearest_dirty_cell(bot1_pos, excluded)
```
- Each bot excludes other bot's targets AND cleaned cells
- Prevents any possibility of overlap
- Ensures 100% cooperation efficiency


**B. Immediate Target Claiming**
- Bot claims target before starting movement
- Other bot immediately sees claimed targets
- Prevents race conditions

**C. Conflict Detection & Abortion**
```python
if bot1_pos in bot2_cleaned:
    # Abort current path, find new target
    bot1_target_path = []
```
- If bot reaches already-cleaned cell, immediately stops
- Finds new target without wasting moves
- Dynamic adaptation to changing environment

**D. Territory Assignment**
- Cells assigned to strictly closer bot
- Uses Manhattan distance for calculation
- Equal distance: assign to bot with fewer tasks
- Reassigned every 25 moves for load balancing

### Performance Metrics

**Cooperation Efficiency:**
```
Efficiency = (Unique cells cleaned / Total work done) × 100%
```
- Target: 100% (zero overlap)
- Achieved: 100% consistently

**Calculation:**
- If no overlap: unique_cleaned = bot1_cleaned + bot2_cleaned
- Efficiency = unique_cleaned / (bot1_cleaned + bot2_cleaned) = 100%

**Key Statistics:**
- Total Dirty Cells: Initial cleaning task size
- Unique Cells Cleaned: Actual cells cleaned (no double-counting)
- Overlap: Cells cleaned by both (target: 0)
- Total Moves: Combined movement of both bots


---

## Visualization System

### Color-Coded Terminal Output

**Color Scheme:**
- **Dark Gray (█):** Walls/Obstacles - impassable areas
- **Light Gray (·):** Empty corridors/floor - walkable areas
- **Blue (① ·):** Agent/Bot 1 - position and path
- **Red (② ·):** Agent/Bot 2 - position and path
- **Yellow (◆):** Keys/Dirty cells - targets to collect/clean
- **Green (✓):** Collected keys/Cleaned cells - completed work

**Why This Design:**
- Clear visual hierarchy (structure → paths → items)
- Color-blind friendly (uses shapes + colors)
- Easy to distinguish agents and their work
- Shows maze structure at all times

### Step-by-Step Animation

**Features:**
- Screen clears between updates
- Shows current state after every N moves
- Real-time progress tracking
- Adjustable animation speed

**Implementation:**
```python
def visualize_step(self, step_num):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
    # ... render current state ...
    time.sleep(0.05)  # Pause for visibility
```

**Update Frequency:**
- Maze Navigator: Every 3 moves
- Cleaning Crew: Every 10 moves
- Adjustable based on maze size and speed preference


---

## Algorithm Comparison

### BFS vs DFS vs A* vs Greedy

| Algorithm | Type | Optimal? | Speed | Memory | Use Case |
|-----------|------|----------|-------|--------|----------|
| BFS | Uninformed | Yes | Medium | High | Shortest path, nearby targets |
| DFS | Uninformed | No | Fast | Low | Deep exploration, distant targets |
| A* | Informed | Yes | Medium | Medium | Optimal pathfinding with heuristic |
| Greedy | Informed | No | Fast | Low | Quick decisions, real-time systems |

**Key Differences:**

**BFS (Breadth-First Search):**
- Explores all neighbors before going deeper
- Uses queue (FIFO - First In First Out)
- Guarantees shortest path
- Good for: finding nearest items

**DFS (Depth-First Search):**
- Explores one path completely before trying others
- Uses stack (LIFO - Last In First Out) or recursion
- May not find shortest path
- Good for: exploring different regions

**A* (A-Star):**
- Uses both actual cost and estimated cost
- Priority queue ordered by f(n) = g(n) + h(n)
- Optimal if heuristic is admissible
- Good for: optimal pathfinding with obstacles

**Greedy Best-First:**
- Only uses estimated cost to goal
- Priority queue ordered by h(n) only
- Faster but not optimal
- Good for: quick approximate solutions


---

## Key Concepts Explained Simply

### 1. Manhattan Distance
**What:** Distance between two points measured along grid lines (no diagonal movement).

**Formula:** `distance = |x1 - x2| + |y1 - y2|`

**Example:**
- Point A at (1, 1)
- Point B at (4, 5)
- Manhattan Distance = |1-4| + |1-5| = 3 + 4 = 7 steps

**Why Used:** Matches how agents actually move in grid-based environments.

### 2. Heuristic Function
**What:** An educated guess about the cost to reach the goal.

**Properties:**
- **Admissible:** Never overestimates actual cost
- **Consistent:** Satisfies triangle inequality
- **Informative:** Guides search toward goal

**Example:** Manhattan distance is a perfect heuristic for grid navigation.

### 3. Cooperation vs Competition
**Competition:** Agents work independently, may duplicate effort.

**Cooperation:** Agents share information and coordinate actions.

**Benefits of Cooperation:**
- Reduced redundancy (no duplicate work)
- Faster completion (parallel processing)
- Better resource utilization
- Higher overall efficiency


### 4. Deadlock Prevention
**What:** Situation where agents get stuck waiting for each other.

**Prevention Strategies:**
1. **Stall Detection:** Count moves without progress
2. **Fallback Mechanism:** After threshold, ignore restrictions
3. **Dynamic Reassignment:** Periodically update assignments
4. **Conflict Abortion:** Immediately abandon conflicting paths

### 5. Load Balancing
**What:** Distributing work evenly between agents.

**Methods:**
- Distance-based assignment (closer agent gets task)
- Workload counting (agent with fewer tasks gets new task)
- Dynamic reassignment (adjust as situation changes)

**Benefits:**
- Both agents stay busy
- Minimizes idle time
- Faster overall completion

---

## Running the Programs

### Requirements
```bash
pip install pyamaze  # For maze generation (optional)
```

### Dual Maze Navigator
```bash
python dual_maze_navigator.py
```

**What You'll See:**
- Animated maze exploration
- Blue agent (BFS) finding nearest keys
- Red agent (DFS) exploring distant areas
- Real-time statistics
- Final summary with efficiency metrics


### Cleaning Crew Coordinator
```bash
python cleaning_crew_coordinator.py
```

**What You'll See:**
- Animated floor cleaning
- Blue bot (A*) using optimal paths
- Red bot (Greedy) using fast paths
- Zero overlap between bots
- 100% cooperation efficiency

### Adjusting Parameters

**Maze Navigator:**
```python
navigator = MazeNavigator(width=25, height=18, num_keys=10)
```
- `width`: Maze width (default: 25)
- `height`: Maze height (default: 18)
- `num_keys`: Number of keys to collect (default: 10)

**Cleaning Crew:**
```python
coordinator = CleaningCrewCoordinator(width=35, height=22, dirty_percentage=0.4)
```
- `width`: Room width (default: 35)
- `height`: Room height (default: 22)
- `dirty_percentage`: Percentage of floor that's dirty (default: 0.4 = 40%)

**Animation Speed:**
```python
time.sleep(0.05)  # Increase for slower, decrease for faster
```

**Update Frequency:**
```python
if moves % 3 == 0:  # Change 3 to update more/less frequently
    self.visualize_step(moves)
```


---

## Technical Implementation Details

### Data Structures Used

**1. Sets (Python set)**
- Used for: visited cells, collected keys, claimed targets
- Why: O(1) lookup, automatic deduplication
- Example: `self.agent1_visited = set()`

**2. Deque (collections.deque)**
- Used for: BFS queue
- Why: O(1) append and pop from both ends
- Example: `queue = deque([(start, [start])])`

**3. Priority Queue (heapq)**
- Used for: A* and Greedy search
- Why: O(log n) insertion, O(1) minimum retrieval
- Example: `heapq.heappush(frontier, (priority, position))`

**4. Dictionary (Python dict)**
- Used for: path reconstruction, came_from tracking
- Why: O(1) lookup and insertion
- Example: `came_from = {start: None}`

**5. 2D List (Grid)**
- Used for: maze/floor representation
- Why: Direct position access, easy visualization
- Example: `self.grid = [[' ' for _ in range(width)] for _ in range(height)]`

### Time Complexity Analysis

**Maze Generation:**
- Recursive Backtracking: O(W × H) where W=width, H=height
- Each cell visited once during carving

**BFS Pathfinding:**
- Time: O(V + E) where V=vertices, E=edges
- Space: O(V) for visited set and queue


**DFS Pathfinding:**
- Time: O(V + E) worst case
- Space: O(D) where D=depth limit (100)
- Depth-limited to prevent infinite recursion

**A* Pathfinding:**
- Time: O(E × log V) with binary heap
- Space: O(V) for open and closed sets
- Optimal if heuristic is admissible

**Greedy Search:**
- Time: O(E × log V) similar to A*
- Space: O(V) for visited set
- Faster in practice due to simpler priority calculation

### Space Complexity

**Per Agent:**
- Path history: O(P) where P=path length
- Visited cells: O(V) where V=cells visited
- Target claims: O(K) where K=number of targets

**Shared:**
- Maze/Grid: O(W × H)
- Keys/Dirty cells: O(N) where N=number of items
- Shared visited: O(V₁ + V₂)

**Total:** O(W × H + P₁ + P₂ + V₁ + V₂ + N)

---

## Real-World Applications

### 1. Warehouse Robotics
- Multiple robots picking orders
- Coordinate to avoid collisions
- Optimize paths to minimize time
- Similar to cleaning crew problem


### 2. Search and Rescue
- Multiple drones searching area
- Coordinate to cover maximum area
- Share information about searched regions
- Similar to maze navigation problem

### 3. Autonomous Vehicles
- Multiple cars navigating city
- Coordinate to avoid traffic
- Share road condition information
- Uses A* for route planning

### 4. Video Game AI
- Multiple NPCs exploring game world
- Coordinate to cover different areas
- Share discovered information
- Uses BFS/DFS for pathfinding

### 5. Network Packet Routing
- Multiple routers finding paths
- Coordinate to balance load
- Share network state information
- Uses shortest path algorithms

---

## Learning Outcomes

### Algorithms & Data Structures
✓ Breadth-First Search (BFS)
✓ Depth-First Search (DFS)
✓ A* Pathfinding
✓ Greedy Best-First Search
✓ Recursive Backtracking
✓ Priority Queues
✓ Graph Traversal

### Software Engineering
✓ Object-Oriented Programming
✓ Modular Design
✓ Code Organization
✓ Documentation
✓ Testing & Debugging


### Multi-Agent Systems
✓ Cooperation Mechanisms
✓ Communication Protocols
✓ Conflict Resolution
✓ Load Balancing
✓ Deadlock Prevention
✓ Territory Assignment

### Problem Solving
✓ Algorithm Selection
✓ Optimization Techniques
✓ Trade-off Analysis
✓ Performance Metrics
✓ Efficiency Measurement

---

## Presentation Tips for Teacher

### 1. Start with the Problem
- "Imagine two robots need to explore a maze and collect keys"
- "How can they work together efficiently?"
- "What if they both go for the same key?"

### 2. Explain the Algorithms Simply
**BFS:** "Like searching for your keys by checking nearby places first"
**DFS:** "Like following one path all the way before trying another"
**A*:** "Like using GPS - considers both distance traveled and distance remaining"
**Greedy:** "Like always walking toward your destination, even if not the best route"

### 3. Demonstrate the Cooperation
- Show the animation running
- Point out how agents avoid each other
- Highlight the efficiency metrics
- Explain why 100% efficiency matters

### 4. Discuss Real-World Applications
- Amazon warehouse robots
- Self-driving cars
- Drone delivery systems
- Video game AI


### 5. Key Points to Emphasize

**Technical Excellence:**
- Multiple algorithms implemented correctly
- Efficient data structures chosen appropriately
- Clean, well-organized code
- Comprehensive error handling

**Innovation:**
- Real-time step-by-step visualization
- 100% cooperation efficiency achieved
- Dynamic territory assignment
- Conflict resolution mechanisms

**Practical Value:**
- Applicable to real-world problems
- Scalable design
- Adjustable parameters
- Educational value for learning algorithms

---

## Common Questions & Answers

**Q: Why use two different algorithms?**
A: Different algorithms have different strengths. BFS finds shortest paths to nearby targets, while DFS explores distant areas. Together, they cover the maze more efficiently than either alone.

**Q: How do agents avoid colliding?**
A: They share information about their positions and targets. Each agent claims a target before pursuing it, preventing conflicts.

**Q: What if both agents want the same key?**
A: The target claiming system prevents this. The first agent to claim a target "reserves" it, and the other agent automatically chooses a different target.

**Q: Why is 100% efficiency important?**
A: It means zero wasted effort. Every move contributes to the goal, with no redundant work. This is crucial for real-world applications where time and energy are limited.


**Q: How does the visualization help?**
A: It makes abstract algorithms concrete and visible. You can see exactly how agents explore, make decisions, and coordinate. This aids understanding and debugging.

**Q: Can this scale to more agents?**
A: Yes! The cooperation mechanisms (claiming, communication, territory assignment) work with any number of agents. The code structure supports easy extension.

**Q: What makes this different from simple pathfinding?**
A: Simple pathfinding is one agent finding one path. This is multi-agent coordination - multiple agents working together, sharing information, and optimizing collective performance.

---

## Code Structure Overview

### Dual Maze Navigator (`dual_maze_navigator.py`)

```
MazeNavigator Class
├── __init__()              # Initialize maze and agents
├── generate_maze()         # Create maze using recursive backtracking
├── get_neighbors()         # Find valid adjacent cells
├── bfs_explore()          # Agent 1 pathfinding (BFS)
├── dfs_explore()          # Agent 2 pathfinding (DFS)
├── find_nearest_key_bfs() # Find closest uncollected key
├── assign_territories()   # Divide keys between agents
├── communicate_paths()    # Share visited cells
├── move_agents()          # Main simulation loop
├── visualize_step()       # Show current state
└── visualize()            # Show final results
```


### Cleaning Crew Coordinator (`cleaning_crew_coordinator.py`)

```
CleaningCrewCoordinator Class
├── __init__()                  # Initialize environment and bots
├── generate_environment()      # Create room with obstacles and dirt
├── get_neighbors()             # Find valid adjacent cells
├── manhattan_distance()        # Calculate distance between points
├── astar_search()             # Bot 1 pathfinding (A*)
├── greedy_search()            # Bot 2 pathfinding (Greedy)
├── find_nearest_dirty_cell()  # Find closest dirty cell
├── assign_territories()       # Divide work between bots
├── coordinate_cleaning()      # Main simulation loop
├── calculate_efficiency()     # Compute cooperation efficiency
├── visualize_step()           # Show current state
└── visualize()                # Show final results
```

---

## Performance Benchmarks

### Dual Maze Navigator
- **Maze Size:** 25×18 (450 cells)
- **Keys:** 10
- **Average Completion:** 60-200 moves
- **Cooperation Efficiency:** 73-100%
- **Success Rate:** 100%

### Cleaning Crew Coordinator
- **Room Size:** 35×22 (770 cells)
- **Dirty Cells:** ~264 (40% of floor)
- **Average Completion:** 200-500 moves
- **Cooperation Efficiency:** 100%
- **Overlap:** 0 cells
- **Success Rate:** 99%+ (occasionally 1 cell remains due to obstacles)


---

## Future Enhancements

### Possible Improvements
1. **More Agents:** Scale to 3+ agents
2. **Dynamic Obstacles:** Moving obstacles during execution
3. **Energy Constraints:** Agents have limited battery
4. **Communication Costs:** Simulate network delays
5. **3D Environments:** Extend to multi-floor buildings
6. **Machine Learning:** Agents learn optimal strategies
7. **GUI Interface:** Interactive visualization with controls
8. **Performance Optimization:** Parallel processing for agents

### Advanced Features
- **Predictive Coordination:** Agents predict each other's moves
- **Hierarchical Planning:** High-level strategy + low-level tactics
- **Adaptive Algorithms:** Switch algorithms based on situation
- **Fault Tolerance:** Handle agent failures gracefully

---

## Conclusion

This project demonstrates sophisticated multi-agent coordination using classical AI algorithms. The combination of different search strategies (BFS, DFS, A*, Greedy) with cooperation mechanisms (claiming, communication, territory assignment) achieves high efficiency in complex environments.

**Key Achievements:**
✓ Multiple pathfinding algorithms implemented
✓ 100% cooperation efficiency in cleaning crew
✓ Real-time visualization system
✓ Robust conflict resolution
✓ Scalable architecture
✓ Well-documented codebase

**Educational Value:**
- Practical application of theoretical algorithms
- Understanding of multi-agent systems
- Experience with optimization techniques
- Visualization of abstract concepts


---

## References & Resources

### Algorithms
- **BFS/DFS:** Introduction to Algorithms (CLRS)
- **A* Algorithm:** Hart, P. E., Nilsson, N. J., & Raphael, B. (1968)
- **Maze Generation:** Recursive Backtracking (Jamis Buck)

### Multi-Agent Systems
- Wooldridge, M. (2009). An Introduction to MultiAgent Systems
- Russell, S., & Norvig, P. (2020). Artificial Intelligence: A Modern Approach

### Python Libraries
- `collections.deque` - Efficient queue implementation
- `heapq` - Priority queue for A* and Greedy
- `random` - Maze generation randomization
- `time` - Animation timing

---

## Author Notes

This project was developed to demonstrate cooperative multi-agent systems in action. The code is designed to be:
- **Educational:** Clear structure and comprehensive comments
- **Practical:** Real-world applicable algorithms
- **Visual:** Step-by-step animation for understanding
- **Efficient:** Optimized data structures and algorithms

Feel free to experiment with parameters, add features, or extend to more agents!

---

## License

This project is created for educational purposes.

---

**Last Updated:** 2024
**Version:** 1.0
**Python Version:** 3.8+
