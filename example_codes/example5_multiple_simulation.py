#!/usr/bin/python3

import os
import platform

if platform.system() == "Linux" or platform.system() == "Darwin":
    os.environ["KIVY_VIDEO"] = "ffpyplayer"

from pysimbotlib.core import PySimbotApp, Robot


class MyRobot(Robot):
    def update(self):
        self.move(10)
        self.turn(-2)


if __name__ == "__main__":
    # The new robots instances will be created every simulation.
    app = PySimbotApp(robot_cls=MyRobot, max_tick=200, simulation_forever=True)
    app.run()
