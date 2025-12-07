#!/usr/bin/python3

import os
import platform

if platform.system() == "Linux" or platform.system() == "Darwin":
    os.environ["KIVY_VIDEO"] = "ffpyplayer"

from pysimbotlib.core import PySimbotApp, Robot


class GoStraightRobot(Robot):
    def update(self):
        self.move(5)


class TurnAroundRobot(Robot):
    def update(self):
        self.turn(5)


def create_robots():
    robot1 = GoStraightRobot()
    robot2 = TurnAroundRobot()
    return [robot1, robot2]


if __name__ == "__main__":
    # customfn_create_robots will override the default create_robots function which is implemented by [robot_cls() for _ in range(num_robots)]
    app = PySimbotApp(customfn_create_robots=create_robots)
    app.run()
