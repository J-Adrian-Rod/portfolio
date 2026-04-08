## 🚀 ASTRA-9: Multi-Agent Lunar Transit Simulation  
### *Pulsing Light Protocol*

---

## Project Overview

Astra-9 is a real-time, multi-agent ride simulation that models autonomous vehicle coordination within a lunar base environment.

Set within a commercialized research colony on the Moon, the system simulates how autonomous rover-pods:
- Navigate a network of biodomes and airlocks  
- Maintain throughput under operational constraints  
- Respond dynamically to system disruptions (e.g., solar flares, gravity instability)  

This project integrates data science, simulation, and storytelling to explore how complex systems behave under constrained and dynamic conditions.

---

## Objectives

- Model vehicle coordination within a constrained network  
- Simulate real-time decision-making under uncertainty  
- Analyze throughput, congestion, and failure propagation  
- Create an immersive “living storyboard” of system behavior  

---

## System Architecture

### Core Components

- **Agents**: Autonomous rover-pods (12 passengers; 3 rows of 4)  
- **Nodes**: Discrete locations (biodomes, control room, corridors, etc.)  
- **Edges**: Airlocks and connecting pathways  
- **Controller**: S.A.G.A.N. (System & Geospatial Autonomous Navigator)  

---

## Key Constraints

- Preserve an immersive experience — vehicles should not encounter one another during the ride  
- Maintain safe spacing between vehicles at all times  
- Enforce dynamic speed limits across different zones  
- Account for variability in passenger boarding times  
- Model system-wide disruptions that affect all agents simultaneously  

---

## Simulation Logic

### Vehicle Decision Rules

- Detect occupied nodes → wait or yield  
- Airlock priority system → sequential access  
- Maintain minimum following distance  
- Adjust speed based on:
  - congestion  
  - environmental conditions  
  - system alerts  

### Dynamic Events

- **Solar flare** → global speed reduction  
- **Gravity instability** → stochastic movement disruptions  
- **Structural failure** → path constraints / rerouting  

---

## Environment: Astra-9 Base

The simulation takes place across interconnected zones:

- **Embarkation Hub** — passenger boarding  
- **Rainforest Dome** — humid, dense canopy  
- **Arctic Dome** — sub-freezing, engineered tundra  
- **Desert Dome** — extreme heat, arid conditions  
- **Agriculture Dome** — food production and pollination  
- **Control Room** — system monitoring  
- **Research Core** — future expansion  
- **Panoramic Observatory** — Earth-facing and base-facing views  
- **Power Sector** — gravity and energy systems  
- **Unfinished Sky Bridge** — high-risk traversal  
- **Bunker Elevator** — located at crater center (end of bridge)  
- **Subsurface Bunker** — protected safe zone  

---

## Living Storyboard

### Scene 1 — The Setup

Astra-9 operates as both a research facility and tourist destination, with vehicles transporting guests through four biodomes connected by airlocks.

The system must:
- Maintain target throughput (PPH)  
- Avoid congestion in narrow corridors  
- Coordinate multiple autonomous vehicles simultaneously  

---

### Scene 2 — The Ride System

![Untitled](https://github.com/user-attachments/assets/ee623f17-a3ea-4108-833d-9f5dec8f96cd)


Vehicles navigate dynamically while:
- Yielding at shared airlocks  
- Avoiding collisions  
- Maintaining flow efficiency  

> Demonstrates how local decision-making produces global coordination.

---

### Scene 3 — The Conflict (Solar Flare Event)

*(Insert GIF: warning system + slowdown)*

A solar flare triggers:
- Global speed reduction (~30%)  
- Increased congestion risk  
- System-wide constraint tightening  

> The system is pushed out of equilibrium, testing its robustness.

---

### Scene 4 — Structural Failure

*(Insert GIF: bridge / instability sequence)*

Compounding factors:
- Gravity grid instability  
- Uneven load distribution  
- Incomplete infrastructure  

Result:
- Progressive structural collapse  
- Forced path constraints  
- No rerouting options  

> A failure cascade emerges from interacting subsystems.

---

### Scene 5 — Resolution

*(Insert GIF or graph: system recovery)*

The system stabilizes as:
- Vehicles clear bottlenecks  
- Flow is restored  
- Throughput approaches target levels  

---

## Performance Metrics

The simulation tracks:
- **Throughput (PPH)**  
- **Average vehicle delay**  
- **Bottleneck frequency (airlocks)**  
- **System recovery time after disruption**  

*(Optional: insert plots or dashboards here)*

---

## Key System Insights

- Airlocks act as primary system bottlenecks  
- Small delays propagate non-linearly across vehicles  
- Throughput is highly sensitive to global speed reductions  
- Structural constraints amplify failure cascades  

> The system exhibits emergent behavior under stress — not all outcomes are predictable from local rules alone.

---

## Future Work

- Reinforcement learning for adaptive routing  
- Dynamic demand simulation (variable guest flow)  
- Predictive congestion modeling  
- Real-time optimization of throughput vs. safety  

---

## Why This Project

This project sits at the intersection of:
- Autonomous systems & mobility  
- Ride/experience system design  
- Multi-agent simulation  
- Data science & system optimization  

---

## Tech Stack

- Python (simulation logic)  
- Pygame (visualization)  
- NumPy / pandas (data handling)  
- Matplotlib (analysis & metrics)  
