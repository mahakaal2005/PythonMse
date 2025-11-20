# Resource Collection Team - Multi-Agent Cooperative System

## 📋 Project Overview

This project demonstrates **cooperative multi-agent resource collection** where 4 autonomous agents work together to collect resources scattered across a maze. The agents use a **shared task queue** and **distributed decision logic** to efficiently divide work and avoid conflicts.

---

## 🎯 Problem Statement (Question 8)

**Objective**: Collect resources scattered in a map cooperatively.

**Key Requirements**:
- Multiple agents working together
- Shared task queue for coordination
- Distributed decision-making logic
- Visual output showing resource collection by each agent

---

## 🧠 How It Works

### 1. **System Architecture**

```
┌─────────────────────────────────────────┐
│         Resource Collection Team        │
├─────────────────────────────────────────┤
│  • 4 Agents (①②③④)                     │
│  • Shared Task Queue                    │
│  • Claimed Resources Tracker            │
│  • Simple Grid Maze (20x20)             │
└─────────────────────────────────────────┘
```

### 2. **Key Components**

#### **A. Agents**
- **Number**: 4 agents
- **Starting Positions**: 
  - Agent 1: Top-left corner (1,1)
  - Agent 2: Bottom-right corner
  - Agent 3: Top-right corner
  - Agent 4: Bottom-left corner
- **Symbols**: ①②③④ (colored circles)

#### **B. Shared Task Queue**
- Contains all resource positions
- All agents can see the queue
- Resources are claimed when an agent targets them
- Prevents multiple agents from going to the same resource

#### **C. Distributed Decision Logic**
Each agent independently:
1. Looks at available (unclaimed) resources
2. Calculates distance to each resource
3. Selects the **nearest** resource
4. Claims it (marks as "mine")
5. Moves towards it using BFS pathfinding

---

## 🔄 Algorithm Flow

```
START
  ↓
Generate Maze with Walls
  ↓
Place 15 Resources Randomly
  ↓
Place 4 Agents at Corners
  ↓
┌─────────────────────────────┐
│   MAIN LOOP (Each Move)     │
├─────────────────────────────┤
│ For each agent:             │
│   1. Need new target?       │
│      ↓ YES                  │
│   2. Find nearest unclaimed │
│      resource               │
│   3. Claim it               │
│   4. Calculate path (BFS)   │
│   5. Move one step          │
│   6. Reached resource?      │
│      ↓ YES                  │
│   7. Collect it!            │
│   8. Update statistics      │
└─────────────────────────────┘
  ↓
All resources collected?
  ↓ YES
Generate Statistics & Heatmap
  ↓
END
```

---

## 🛠️ Technical Implementation

### **1. Maze Generation**
```python
def generate_maze(self):
    # Create border walls
    # Add random internal walls (10% of grid)
    # Ensures maze is navigable
```

### **2. BFS Pathfinding**
```python
def get_path_bfs(self, start, goal):
    # Breadth-First Search
    # Finds shortest path avoiding walls
    # Returns list of positions to follow
```

### **3. Task Assignment (Distributed Logic)**
```python
def assign_task(self, agent_id):
    # Get current position
    # Find all unclaimed resources
    # Calculate Manhattan distance to each
    # Select nearest one
    # Claim it (add to claimed_resources)
    # Return target position
```

### **4. Resource Collection**
```python
def collect_resource(self, agent_id, resource_pos):
    # Remove from resource_positions
    # Add to agent's collected count
    # Record timestamp for statistics
    # Remove from claimed list
```

---

## 📊 Output & Visualization

### **1. Terminal Visualization**
- **Colored maze display** with:
  - `██` = Walls (dark gray)
  - `①②③④` = Agents (colored backgrounds)
  - `··` = Agent paths (cyan)
  - `◆` = Resources (yellow background)

### **2. Statistics Plot** (`resource_collection_stats.png`)
Two charts:
- **Bar Chart**: Resources collected by each agent
- **Timeline**: Cumulative collection over time

### **3. Summary Report**
```
Agent 1: 3 resources (20%)
Agent 2: 3 resources (20%)
Agent 3: 5 resources (33.3%)
Agent 4: 4 resources (26.7%)
Total: 15/15 (100%)
```

---

## 🎨 Color Coding

| Element | Color | Meaning |
|---------|-------|---------|
| ①① | Blue background | Agent 1 |
| ②② | Red background | Agent 2 |
| ③③ | Green background | Agent 3 |
| ④④ | Magenta background | Agent 4 |
| ·· | Cyan | Agent paths |
| ◆◆ | Yellow background | Resources |
| ██ | Dark gray | Walls |

---

## 🚀 How to Run

### **Prerequisites**
```bash
pip install matplotlib
```

### **Run the Program**
```bash
python resource_collection.py
```

### **Expected Output**
1. Terminal shows maze with agents collecting resources
2. Summary statistics printed
3. PNG file saved: `resource_collection_stats.png`

---

## 💡 Key Concepts Explained

### **1. Shared Task Queue**
Think of it like a **to-do list** that everyone can see:
- All resources start in the queue
- When an agent picks a task, it's marked as "claimed"
- Other agents skip claimed tasks
- When collected, it's removed from the queue

### **2. Distributed Decision Logic**
Each agent is **independent**:
- No central controller telling them what to do
- Each agent makes its own decisions
- Uses simple rule: "Go to nearest available resource"
- This is called **distributed** because decision-making is spread across agents

### **3. Cooperation Without Communication**
Agents cooperate by:
- **Sharing information** (claimed resources)
- **Avoiding conflicts** (don't target same resource)
- **Working in parallel** (all move simultaneously)

### **4. BFS (Breadth-First Search)**
Pathfinding algorithm:
- Explores all neighbors level by level
- Guarantees **shortest path**
- Avoids walls and obstacles

---

## 📈 Performance Metrics

### **Efficiency Calculation**
```
Efficiency = Total Moves / Resources Collected
Lower is better!

Example: 22 moves / 15 resources = 1.47 moves per resource
```

### **Coverage**
```
Coverage = Resources Collected / Total Resources × 100%
Goal: 100%
```

### **Load Balance**
How evenly work is distributed:
```
Ideal: Each agent collects ~25% of resources
Actual: Varies based on starting positions and maze layout
```

---

## 🔍 Code Structure

```
resource_collection.py
│
├── ResourceCollectionTeam (Main Class)
│   ├── __init__()           # Initialize variables
│   ├── generate_maze()      # Create maze with walls
│   ├── initialize_agents()  # Place agents at corners
│   ├── place_resources()    # Scatter resources (reachable)
│   ├── get_path_bfs()       # Find shortest path
│   ├── assign_task()        # Distributed decision logic
│   ├── move_agent()         # Move one step towards target
│   ├── collect_resource()   # Pick up resource
│   ├── run_simulation()     # Main loop
│   ├── visualize_maze_terminal()  # Display in terminal
│   ├── plot_statistics()    # Generate charts
│   └── print_summary()      # Show results
│
└── main()                   # Entry point
```

---

## 🎓 Explaining to Your Teacher

### **Key Points to Mention**

1. **Problem**: Multiple agents need to collect resources efficiently without conflicts

2. **Solution**: 
   - Shared task queue (everyone sees what needs to be done)
   - Distributed logic (each agent decides independently)
   - Resource claiming (prevents conflicts)

3. **Algorithms Used**:
   - BFS for pathfinding (shortest path)
   - Greedy nearest-neighbor for task selection
   - Manhattan distance for proximity calculation

4. **Cooperation Strategy**:
   - Agents share information about claimed resources
   - No central controller (distributed system)
   - Parallel execution (all agents move simultaneously)

5. **Results**:
   - 100% resource collection
   - Efficient coordination (minimal wasted moves)
   - Visual proof of cooperation

---

## 🧪 Example Scenario

```
Initial State:
┌─────────────────┐
│ ①  ◆    ◆    ③ │
│    ◆  ◆  ◆     │
│ ◆     ◆     ◆  │
│    ◆  ◆  ◆  ◆  │
│ ④  ◆    ◆    ② │
└─────────────────┘

Agent 1 thinks: "Nearest resource is at (1,2), I'll claim it!"
Agent 2 thinks: "Nearest resource is at (4,3), I'll claim it!"
Agent 3 thinks: "Nearest resource is at (1,3), I'll claim it!"
Agent 4 thinks: "Nearest resource is at (4,1), I'll claim it!"

After 22 moves:
┌─────────────────┐
│ ··  ··    ··  ·③│
│ ·  ··  ··  ··  ·│
│··    ··    ··  ·│
│ ·  ··  ··  ··  ·│
│④·  ··    ··   ②·│
└─────────────────┘

All resources collected! ✓
```

---

## 🔧 Customization Options

You can modify:
```python
# In main() function:
team = ResourceCollectionTeam(
    maze_size=20,      # Change maze size
    num_agents=4,      # Change number of agents
    num_resources=15   # Change number of resources
)
```

---

## 📚 Learning Outcomes

After understanding this code, you'll know:
- ✅ Multi-agent coordination
- ✅ Distributed decision-making
- ✅ Shared resource management
- ✅ Pathfinding algorithms (BFS)
- ✅ Conflict avoidance strategies
- ✅ Data visualization with matplotlib

---

## ❓ Common Questions & Answers

**Q: Why use a shared task queue?**  
A: It prevents multiple agents from targeting the same resource, avoiding wasted effort.

**Q: What if two agents claim the same resource?**  
A: The claiming happens sequentially in the code, so only one agent can claim at a time.

**Q: Why BFS instead of other pathfinding?**  
A: BFS guarantees the shortest path in an unweighted grid, which is perfect for our maze.

**Q: How do agents avoid collisions?**  
A: In this simulation, agents can occupy the same cell. In real-world scenarios, you'd add collision detection.

**Q: What makes this "distributed"?**  
A: Each agent makes its own decisions based on shared information, without a central controller.

---

## 📝 Summary

This project demonstrates **cooperative multi-agent systems** where autonomous agents work together efficiently by:
1. Sharing information (task queue)
2. Making independent decisions (distributed logic)
3. Avoiding conflicts (resource claiming)
4. Using efficient pathfinding (BFS)

The result is a system that collects all resources with minimal coordination overhead and maximum efficiency!

---

**Author**: Multi-Agent Systems Project  
**Date**: 2024  
**Purpose**: Educational demonstration of cooperative agent behavior
