# PySimbot

## 1. Project Overview
PySimbot is a lightweight, 2D robot simulation framework built on top of the [Kivy](https://kivy.org/) library. It provides an environment where one or more robots roam a 2D map, interacting with obstacles and objectives (food). The framework is designed for educational purposes, allowing users to implement robot control logic, test navigation algorithms, or simply control a robot manually.

## 2. Architecture
The project follows a component-based architecture leveraging Kivy's widget system.

### 2.1 Directory Structure
-   **`pysimbotlib/core/`**: contains the core logic classes.
    -   `App.py`: The main Kivy Application class.
    -   `Simbot.py`: The simulation controller and environment.
    -   `Robot.py`: The robot agent definition.
    -   `Geom.py`: Geometry utility functions.
    -   `Obstacle.py`: Obstacle entity definition.
    -   `Objective.py`: Objective (food) entity definition.
    -   `Global.py`: Global constants.
-   **`pysimbotlib/maps/`**: Kivy language (`.kv`) files defining map layouts.
-   **`pysimbotlib/themes/`**: Kivy language (`.kv`) files defining visual themes.
-   **`examples/`**: (in root) various example scripts demonstrating usage.

### 2.2 Core Classes

#### `PySimbotApp` (`App.py`)
-   **Role**: Application Entry Point.
-   **Responsibilities**:
    -   Initializes the Kivy window and configuration.
    -   Loads map and theme `.kv` files.
    -   Instantiates the `Simbot` simulation instance.
    -   Schedules the simulation loop (`Simbot.process`) using `kivy.clock.Clock`.

#### `Simbot` (`Simbot.py`)
-   **Role**: Simulation Supervisor / Environment.
-   **Responsibilities**:
    -   **State Management**: Tracks iteration count, score, and simulation status.
    -   **Entity Management**: Maintains lists of `Robot`, `Obstacle`, and `Objective` instances.
    -   **Simulation Loop**: The `process(dt)` method is the heartbeat, calling `Robot.update()` for all robots and handling start/end conditions.
    -   **Rules Enforcer**: Handles logic like spawning entities, resetting the simulation, and processing "eat" events.

#### `Robot` (`Robot.py`)
-   **Role**: The Agent.
-   **Responsibilities**:
    -   **Movement**: `move(step)` and `turn(degree)`. Handles collision detection with walls and obstacles during movement to prevent invalid states.
    -   **Sensing**:
        -   `distance(index)`: Returns distance to the nearest collider in a specific direction.
        -   `smell(index)`: Returns the angle to a specific objective.
    -   **Logic**: Users are expected to override the `update()` method to implement autonomous behavior.
    -   **State**: Tracks position, direction, color, and internal flags (stuck, just_eat).

#### `Geom` (`Geom.py`)
-   **Role**: Math Helper.
-   **Responsibilities**:
    -   Static methods for 2D geometry checks:
        -   Line segment intersections (for raycasting/sensors).
        -   Bounding box overlaps (AABB).
        -   Circle-Rectangle intersections (for accurate collision detection).

## 3. Key Concepts

### 3.1 Coordinate System
-   Standard Cartesian 2D grid.
-   Robot `pos` is `(x, y)`.
-   Robot `direction` is in degrees (0 = East, increasing counter-clockwise, typically).

### 3.2 Simulation Loop
1.  **Initialization**: `Simbot` sets up the map, spawns entities.
2.  **Tick**: `process()` is called every frame (defined by `interval`).
3.  **Update**: Each robot's `update()` method is called.
4.  **Action**: Robots perform `move` or `turn`, which immediately check for collisions.
5.  **Validation**: If a move results in a collision, the robot is blocked (or slides, depending on implementation details in `move`).
6.  **Termination**: Simulation runs until `max_tick` is reached or runs forever if configured.

### 3.3 Sensors & Actuators
-   **Actuators**:
    -   `move(step)`: Move forward/backward.
    -   `turn(degree)`: Rotate.
-   **Sensors**:
    -   **Raycasting**: Robots have "eyes" (distance sensors) at fixed angles defined in `Global.py`. They cast rays to detect distances to walls or obstacles.
    -   **Smell**: A virtual sensor providing the angle to food sources.

## 4. Usage
Users typically create a script that:
1.  Defines a custom `Robot` subclass implementing the `update()` method.
2.  Instantiates `PySimbotApp`, passing the custom robot class.
3.  Calls `app.run()`.

Example:
```python
from pysimbotlib import *

class MyRobot(Robot):
    def update(self):
        self.move(2)
        if self.distance(0) < 40:
             self.turn(10)

app = PySimbotApp(robot_cls=MyRobot, num_robots=1)
app.run()
```