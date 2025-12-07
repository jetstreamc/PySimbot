#!/usr/bin/python3

import os
import platform

if platform.system() == "Linux" or platform.system() == "Darwin":
    os.environ["KIVY_VIDEO"] = "ffpyplayer"

from kivy.config import Config
from kivy.logger import Logger

from pysimbotlib.core import PySimbotApp, Robot

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set("kivy", "log_level", "info")

# update robot every 0.5 seconds (2 frames per sec)
REFRESH_INTERVAL = 1 / 2


class MyRobot(Robot):
    def update(self):
        Logger.info(f"Smell Angle: {self.smell()}")
        Logger.info(f"Distance: {self.distance()}")


if __name__ == "__main__":
    app = PySimbotApp(robot_cls=MyRobot, num_robots=1, interval=REFRESH_INTERVAL, enable_wasd_control=True)
    app.run()
