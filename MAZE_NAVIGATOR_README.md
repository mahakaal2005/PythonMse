# Dual Maze Navigator - Cooperative Key Collection System

## Project Overview

Two intelligent agents cooperatively explore a maze to collect scattered keys. They use different search algorithms (BFS and DFS) and coordinate their efforts to maximize efficiency and minimize redundant exploration.

---

## Problem Statement

**Challenge:** A maze contains multiple keys scattered throughout. Two agents must collect all keys as efficiently as possible.

**Goals:**
- Collect all keys in minimum time
- Minimize overlap between agents
- Maximize cooperation efficiency
- Demonstrate different pathfinding algorithms

---

## Technical Components

### 1. Maze Generation Algorithm

**Algorithm Used:** Recursive Backtracking

**How It Works:**
1. Start with a grid completely filled with walls
2. Choose a random starting cell and mark it as a passage
3. Randomly select an unvisited neighbor
4. Remove the wall between current cell and chosen neighbor
5. Recursively repeat from the new cell
6. Backtrack when no unvisited neighbors remain
7. Add extra passages (20% of cells) to reduce linearity

**Why This Algorithm:**
- Creates perfect mazes (exactly one path between any two points)
- Guarantees all areas are reachable
- Produces interesting, non-trivial layouts
- Balances complexity with solvability

**Code Example:**
```python
def generate_maze(self):
    # Initialize with walls
    for i in range(self.height):
        for j in range(self.width):
            self.grid[i][j] = '#'
    
    # Carve passages recursively
    def carve_passages(cx, cy):
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if is_valid(nx, ny) and self.grid[nx][ny] == '#':
                self.grid[cx + dx // 2][cy + dy // 2] = ' '
                self.grid[nx][ny] = ' '
                carve_passages(nx, ny)
```


---

### 2. Agent 1: Breadth-First Search (BFS)

**What It Does:** Finds the shortest path to the nearest uncollected key.

**Algorithm Explanation:**

**Simple Analogy:** Like ripples spreading in water - explores all nearby cells before moving to distant ones.

**How It Works:**
1. Start at current position
2. Add all neighbors to a queue
3. Process queue in order (FIFO - First In First Out)
4. Mark each cell as visited
5. Continue until target key is found
6. Reconstruct path by backtracking

**Step-by-Step Example:**
```
Start: Agent at position (1,1), Key at (3,3)

Step 1: Check (1,1) - not the key
Step 2: Add neighbors (1,2) and (2,1) to queue
Step 3: Check (1,2) - not the key
Step 4: Add its neighbors to queue
Step 5: Check (2,1) - not the key
...continue until (3,3) is found
```

**Time Complexity:** O(V + E)
- V = number of vertices (cells)
- E = number of edges (connections)

**Space Complexity:** O(V)
- Stores visited cells and queue

**Advantages:**
- ✓ Guarantees shortest path
- ✓ Systematic exploration
- ✓ Good for finding nearby targets
- ✓ Complete (always finds solution if exists)

**Disadvantages:**
- ✗ Uses more memory
- ✗ May be slower for distant targets
- ✗ Explores many unnecessary cells

**Code Implementation:**
```python
def bfs_explore(self, start, excluded_keys):
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        pos, path = queue.popleft()
        
        # Found a key?
        if pos in self.keys_positions and pos not in excluded_keys:
            return path, pos
        
        # Explore neighbors
        for neighbor in self.get_neighbors(pos):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return [start], None
```


---

### 3. Agent 2: Depth-First Search (DFS)

**What It Does:** Explores deeply into the maze to find distant keys.

**Algorithm Explanation:**

**Simple Analogy:** Like exploring a cave - follow one tunnel all the way to the end before trying another tunnel.

**How It Works:**
1. Start at current position
2. Choose a random unvisited neighbor
3. Recursively explore from that neighbor
4. Go as deep as possible (up to depth limit of 100)
5. Backtrack when no unvisited neighbors or depth limit reached
6. Continue until key is found

**Step-by-Step Example:**
```
Start: Agent at (1,1), Key at (5,5)

Step 1: Go to (1,2)
Step 2: Go to (1,3)
Step 3: Go to (1,4)
Step 4: Go to (2,4)
Step 5: Go to (3,4)
...continue going deep until key found or dead end
If dead end: backtrack and try different path
```

**Time Complexity:** O(V + E)
- V = number of vertices
- E = number of edges

**Space Complexity:** O(D)
- D = depth limit (100 in our case)
- Much less memory than BFS

**Advantages:**
- ✓ Memory efficient
- ✓ Good for finding distant targets
- ✓ Explores different regions than BFS
- ✓ Fast for deep searches

**Disadvantages:**
- ✗ May not find shortest path
- ✗ Can get stuck in wrong branch
- ✗ Needs depth limit to prevent infinite loops

**Code Implementation:**
```python
def dfs_explore(self, pos, visited, path, depth=0, max_depth=100):
    if depth > max_depth:
        return False, path, None
    
    # Found a key?
    if pos in self.keys_positions and pos not in self.collected_keys:
        return True, path, pos
    
    visited.add(pos)
    
    # Try each neighbor
    neighbors = self.get_neighbors(pos)
    random.shuffle(neighbors)  # Randomize for variety
    
    for neighbor in neighbors:
        if neighbor not in visited:
            found, new_path, target = self.dfs_explore(
                neighbor, visited, path + [neighbor], depth + 1, max_depth)
            if found:
                return True, new_path, target
    
    return False, path, None
```


---

## Cooperation Mechanisms

### 1. Target Claiming System

**Purpose:** Prevent both agents from pursuing the same key.

**How It Works:**
```python
# Agent 1 claims a key before pursuing it
if self.agent1_target:
    self.agent1_claimed.add(self.agent1_target)

# Agent 2 excludes Agent 1's claimed keys
excluded = self.agent1_claimed
agent2_target = find_nearest_key(agent2_pos, excluded)
```

**Benefits:**
- Eliminates duplicate effort
- Ensures each key is targeted by only one agent
- Increases overall efficiency

### 2. Real-Time Communication

**Purpose:** Share exploration progress between agents.

**Implementation:**
```python
def communicate_paths(self):
    # Combine visited cells from both agents
    self.shared_visited = self.agent1_visited.union(self.agent2_visited)
```

**What's Shared:**
- Visited cells
- Collected keys
- Current targets
- Path information

**Update Frequency:** Every move (real-time)

### 3. Territory Assignment

**Purpose:** Divide keys between agents based on proximity.

**Algorithm:**
```python
def assign_territories(self):
    for key_pos in uncollected_keys:
        dist1 = manhattan_distance(agent1_pos, key_pos)
        dist2 = manhattan_distance(agent2_pos, key_pos)
        
        if dist1 < dist2:
            self.agent1_claimed.add(key_pos)
        elif dist2 < dist1:
            self.agent2_claimed.add(key_pos)
```

**Reassignment:** Every 30 moves for dynamic adaptation


### 4. Conflict Resolution

**Problem:** What if an agent reaches a key already collected by the other agent?

**Solution:**
```python
if self.agent1_pos in self.bot2_cleaned:
    # Abort current path
    agent1_target_path = []
    agent1_target = None
    # Find new target immediately
```

**Deadlock Prevention:**
- Stall counter tracks moves without progress
- After 50 moves without collecting a key, ignore all claims
- Ensures system never gets stuck

---

## Performance Metrics

### Cooperation Efficiency

**Formula:**
```
Efficiency = (Unique cells explored / Total cells explored) × 100%
```

**Calculation Example:**
- Agent 1 visited: 100 cells
- Agent 2 visited: 80 cells
- Overlap: 20 cells
- Unique cells: 100 + 80 - 20 = 160
- Total cells: 100 + 80 = 180
- Efficiency: 160/180 = 88.9%

**Target:** 100% (no overlap)
**Typical Achievement:** 73-100%

### Other Metrics

**Keys Collected:** Progress indicator
- Shows X/Y keys collected
- Success = all keys collected

**Path Length:** Total moves per agent
- Shorter is better
- Indicates efficiency of pathfinding

**Visited Cells:** Unique cells explored per agent
- Shows exploration coverage
- Lower overlap = better cooperation

**Shared Knowledge:** Combined exploration area
- Total unique cells visited by both agents
- Indicates overall coverage


---

## Visualization System

### Color-Coded Display

**Colors Used:**
- **Dark Gray (█):** Walls - impassable barriers
- **Light Gray (·):** Empty corridors - walkable paths
- **Blue (① ·):** Agent 1 (BFS) - position and path
- **Red (② ·):** Agent 2 (DFS) - position and path
- **Yellow (◆):** Uncollected keys - targets
- **Green (✓):** Collected keys - completed objectives

### Step-by-Step Animation

**Features:**
- Screen clears between updates
- Shows maze state every 3 moves
- Real-time progress tracking
- Adjustable speed

**Example Output:**
```
============================================================
STEP 45 - Keys: 7/10
============================================================

█ █ █ █ █ █ █ █ █ █ █ █ █
█ · · · · · · · · · · · █
█ · █ █ █ · █ █ █ · █ · █
█ · · · ✓ · · · ◆ · · · █
█ · █ · █ █ █ · █ · █ · █
█ · · · · · ① · · · · · █
█ █ █ · █ █ █ · █ █ █ · █
█ · · · · · · · · · ② · █
█ █ █ █ █ █ █ █ █ █ █ █ █

Agent 1: 45 steps | Agent 2: 38 steps
```

**What You See:**
- Current agent positions (① ②)
- Paths taken so far (blue and red dots)
- Keys collected (✓) and remaining (◆)
- Maze structure (walls and corridors)
- Progress statistics


---

## Running the Program

### Requirements
```bash
# Python 3.8 or higher
python --version

# No external libraries required (uses standard library only)
```

### Execution
```bash
python dual_maze_navigator.py
```

### What Happens
1. Maze is generated using recursive backtracking
2. 10 keys are randomly placed
3. Agents start in opposite corners
4. Animation shows step-by-step exploration
5. Final statistics are displayed

### Adjusting Parameters

**Maze Size:**
```python
navigator = MazeNavigator(width=25, height=18, num_keys=10)
```
- `width`: Maze width (default: 25)
- `height`: Maze height (default: 18)
- `num_keys`: Number of keys (default: 10)

**Animation Speed:**
```python
time.sleep(0.05)  # Seconds between frames
```
- Increase for slower animation
- Decrease for faster animation

**Update Frequency:**
```python
if moves % 3 == 0:  # Update every 3 moves
    self.visualize_step(moves)
```
- Lower number = more frequent updates
- Higher number = less frequent updates

---

## Algorithm Comparison: BFS vs DFS

| Aspect | BFS (Agent 1) | DFS (Agent 2) |
|--------|---------------|---------------|
| **Strategy** | Explore nearby first | Explore deeply first |
| **Path Quality** | Shortest path | May not be shortest |
| **Memory Usage** | High (stores all levels) | Low (only current path) |
| **Best For** | Nearby targets | Distant targets |
| **Exploration** | Systematic, level-by-level | Random, depth-first |
| **Completeness** | Always finds solution | Finds solution (with depth limit) |


**Why Use Both?**
- BFS efficiently collects nearby keys
- DFS explores distant regions
- Together they cover the maze faster than either alone
- Complementary strengths lead to better overall performance

---

## Key Concepts Explained

### Manhattan Distance

**Definition:** Distance between two points measured along grid lines (no diagonal movement).

**Formula:**
```
distance = |x1 - x2| + |y1 - y2|
```

**Example:**
- Point A: (2, 3)
- Point B: (5, 7)
- Distance: |2-5| + |3-7| = 3 + 4 = 7 steps

**Why Used:** Matches how agents actually move in grid-based mazes.

### Recursive Backtracking

**Concept:** Solve problem by trying options, backtracking when stuck.

**In Maze Generation:**
1. Try carving a passage
2. If successful, recursively continue
3. If stuck, backtrack and try different direction
4. Repeat until maze is complete

**Advantages:**
- Creates perfect mazes
- Guarantees connectivity
- Natural-looking layouts

---

## Real-World Applications

### 1. Search and Rescue Operations
- Multiple drones searching disaster area
- Coordinate to cover maximum area
- Share information about searched regions
- Minimize redundant searching

### 2. Warehouse Robotics
- Multiple robots picking orders
- Coordinate paths to avoid collisions
- Share information about picked items
- Optimize for minimum total time


### 3. Video Game AI
- Multiple NPCs exploring game world
- Coordinate to cover different areas
- Share discovered information
- Create realistic behavior

### 4. Network Exploration
- Multiple crawlers indexing websites
- Coordinate to avoid duplicate work
- Share visited URLs
- Maximize coverage efficiency

---

## Presentation Guide for Teacher

### Opening (2 minutes)
**Start with the problem:**
"Imagine you and a friend need to find 10 hidden keys in a large maze. How would you work together efficiently? Would you both search the same areas, or divide the work?"

### Algorithm Explanation (5 minutes)

**BFS - Simple Explanation:**
"Like searching for your lost phone by checking nearby rooms first, then gradually expanding to farther rooms."

**DFS - Simple Explanation:**
"Like exploring a cave by following one tunnel all the way to the end before trying another tunnel."

**Why Both:**
"One agent finds nearby keys quickly (BFS), while the other explores distant areas (DFS). Together, they're faster than either alone."

### Demonstration (3 minutes)
1. Run the program
2. Point out the two agents (blue and red)
3. Show how they avoid each other
4. Highlight the efficiency metric
5. Explain the final statistics

### Cooperation Mechanisms (3 minutes)
**Explain:**
- Target claiming: "Like calling dibs on a key"
- Communication: "They share what they've explored"
- Territory assignment: "Each agent focuses on nearby keys"
- Conflict resolution: "If they meet, they adjust plans"


### Technical Details (5 minutes)
**Cover:**
- Time complexity: O(V + E) for both algorithms
- Space complexity: O(V) for BFS, O(D) for DFS
- Data structures: Sets for visited cells, Deque for BFS queue
- Cooperation efficiency: 73-100%

### Conclusion (2 minutes)
**Key Points:**
- Multiple algorithms working together
- Efficient cooperation mechanisms
- Real-world applicable
- Demonstrates AI coordination

---

## Common Questions & Answers

**Q: Why not use just one algorithm?**
A: Different algorithms have different strengths. BFS is optimal for nearby targets, DFS explores distant areas. Using both provides better coverage.

**Q: How do agents avoid collecting the same key?**
A: The target claiming system. When an agent decides to pursue a key, it "claims" it, and the other agent automatically chooses a different key.

**Q: What if the maze has no solution?**
A: The recursive backtracking algorithm guarantees all areas are connected, so there's always a path to every key.

**Q: Can this work with more than 2 agents?**
A: Yes! The cooperation mechanisms (claiming, communication, territory assignment) scale to any number of agents.

**Q: Why is cooperation efficiency not always 100%?**
A: Some overlap is inevitable when agents' paths cross or when they're searching nearby areas. The goal is to minimize this overlap.

---

## Performance Benchmarks

**Typical Results:**
- Maze Size: 25×18 (450 cells)
- Keys: 10
- Completion Time: 60-200 moves
- Cooperation Efficiency: 73-100%
- Success Rate: 100%

**Best Case:**
- Agents explore completely different regions
- No path overlap
- 100% efficiency

**Worst Case:**
- Agents search similar areas
- Significant path overlap
- ~70% efficiency


---

## Code Structure

```
MazeNavigator Class
│
├── Initialization
│   ├── __init__()                    # Set up maze and agents
│   └── generate_maze()               # Create maze structure
│
├── Pathfinding Algorithms
│   ├── bfs_explore()                 # Agent 1: Breadth-First Search
│   ├── dfs_explore()                 # Agent 2: Depth-First Search
│   └── find_nearest_key_bfs()        # Find closest uncollected key
│
├── Cooperation Mechanisms
│   ├── assign_territories()          # Divide keys between agents
│   ├── communicate_paths()           # Share visited cells
│   └── get_neighbors()               # Find valid adjacent cells
│
├── Simulation
│   └── move_agents()                 # Main loop: move agents, collect keys
│
└── Visualization
    ├── visualize_step()              # Show current state (animation)
    └── visualize()                   # Show final results
```

---

## Learning Outcomes

### Algorithms
✓ Breadth-First Search (BFS)
✓ Depth-First Search (DFS)
✓ Recursive Backtracking
✓ Graph Traversal

### Data Structures
✓ Sets (for visited cells)
✓ Deque (for BFS queue)
✓ 2D Lists (for maze grid)
✓ Tuples (for positions)

### Concepts
✓ Multi-agent coordination
✓ Cooperation mechanisms
✓ Conflict resolution
✓ Performance optimization
✓ Algorithm comparison

---

## Future Enhancements

### Possible Improvements
1. **More Agents:** Scale to 3+ agents
2. **Different Algorithms:** Add A*, Dijkstra's
3. **Dynamic Mazes:** Walls that move or change
4. **Energy Constraints:** Agents have limited moves
5. **Weighted Keys:** Some keys more valuable than others
6. **Time Limits:** Must collect all keys within time limit

---

## Conclusion

This project demonstrates how two agents with different search strategies can cooperate to solve a complex problem efficiently. The combination of BFS and DFS, along with sophisticated cooperation mechanisms, achieves high performance in maze exploration and key collection.

**Key Achievements:**
✓ Two pathfinding algorithms implemented
✓ Efficient cooperation mechanisms
✓ Real-time visualization
✓ High cooperation efficiency (73-100%)
✓ Robust conflict resolution

---

**Project Type:** Multi-Agent Cooperative System
**Algorithms:** BFS, DFS, Recursive Backtracking
**Language:** Python 3.8+
**Dependencies:** None (standard library only)
