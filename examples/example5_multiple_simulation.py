#!/usr/bin/python3

"""
Example 5: Multiple Simulations
===============================

This example shows how to run continuous simulations.
- `simulation_forever=True` restarts the simulation automatically.
- `max_tick=200` limits each simulation to 200 iterations.
- Automatically resets robot positions and state between runs.
"""

from pysimbotlib.core import PySimbotApp, Robot


class MyRobot(Robot):
    def update(self):
        self.move(10)
        self.turn(-2)


if __name__ == "__main__":
    # The new robots instances will be created every simulation.
    app = PySimbotApp(robot_cls=MyRobot, max_tick=200, simulation_forever=True)
    app.run()
