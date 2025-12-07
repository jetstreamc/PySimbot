#!/usr/bin/python3

"""
Example 6: Advanced Multiple Simulation
=======================================

This example demonstrates advanced hooks for simulation life-cycle.
- `customfn_before_simulation`: Called before each run (used to randomize positions).
- `customfn_after_simulation`: Called after each run (used to log stats).
- Manages strict timing and high robot count (`num_robots=30`).
- Demonstrates access to simulation statistics key like `eat_count` and `score`.
"""

import random
import time

from kivy.config import Config
from kivy.logger import Logger

from pysimbotlib.core import PySimbotApp, Robot, Simbot

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set("kivy", "log_level", "info")
Config.set("graphics", "maxfps", 10)


class RandomWalkRobot(Robot):
    def update(self):
        self.distance()
        r = random.randint(0, 3)
        self.move(5)
        if r == 1:
            self.turn(15)
        elif r == 2:
            self.turn(-15)


start_time = time.time()


def before_sim(simbot_map: Simbot):
    global start_time
    start_time = time.time()
    Logger.info("Simulation: Before simulation.")
    Logger.info("Simulation: You can now do something with map objects or robots")
    for r in simbot_map.robots:
        while True:
            # Try a new random position
            r.pos = (random.randint(0, 800 - r.width), random.randint(0, 600 - r.height))
            # Check validity (walls, obstacles, other robots in hash)
            if simbot_map.is_robot_pos_valid(r):
                break

        r.set_color(random.random(), random.random(), random.random())


def after_sim(simbot_map: Simbot):
    # There are some simbot and robot calcalated statistics and property during simulation
    # - simbot.score
    # - simbot.simulation_count
    # - simbot.eat_count
    # - simbot.food_move_count
    # - simbot.score
    # - simbot.scoreStr

    # - simbot.robot[i].eat_count
    # - simbot.robot[i].collision_count
    # - simbot.robot[i].color

    for r in simbot_map.robots:
        Logger.info(f"Simulation: robot pos = {r.pos}")
        Logger.info(f"Simulation: robot eat_count = {r.eat_count}")
        Logger.info(f"Simulation: robot collision_count = {r.collision_count}")

    Logger.info(f"Simulation: End simulation. Robot[0] is at {simbot_map.robots[0].pos}")
    Logger.info(f"Simulation: Score = {simbot_map.score}")
    Logger.info(f"Time: {time.time() - start_time}")


if __name__ == "__main__":
    app = PySimbotApp(
        robot_cls=RandomWalkRobot,
        num_robots=30,
        max_tick=500,
        interval=1 / 1000.0,
        simulation_forever=True,
        robot_see_each_other=True,
        customfn_before_simulation=before_sim,
        customfn_after_simulation=after_sim,
        food_move_after_eat=False,
    )
    app.run()
