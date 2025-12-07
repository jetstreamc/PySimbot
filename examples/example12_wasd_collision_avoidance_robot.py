#!/usr/bin/python3


import random

from kivy.config import Config

from pysimbotlib.core import PySimbotApp, Robot

# Force the program to show user's log only for "debug" level or more. The info log will be disabled.
Config.set("kivy", "log_level", "debug")


class CollisionAvoidanceRobot(Robot):
    def update(self):
        if self.stuck:
            if random.random() < 0.5:
                self.turn(5)
            else:
                self.turn(-5)


if __name__ == "__main__":
    app = PySimbotApp(robot_cls=CollisionAvoidanceRobot, enable_wasd_control=True)
    app.run()
