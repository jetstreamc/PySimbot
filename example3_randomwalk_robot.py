#!/usr/bin/python3

import os
import platform

if platform.system() == "Linux" or platform.system() == "Darwin":
    os.environ["KIVY_VIDEO"] = "ffpyplayer"

from kivy.config import Config

from pysimbotlib.core import PySimbotApp, Robot

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set("kivy", "log_level", "info")

import random


class RandomWalkRobot(Robot):
    def update(self):
        r = random.randint(0, 3)
        self.move(5)
        if r == 1:
            self.turn(15)
        elif r == 2:
            self.turn(-15)


if __name__ == "__main__":
    app = PySimbotApp(robot_cls=RandomWalkRobot, num_robots=2)
    app.run()
