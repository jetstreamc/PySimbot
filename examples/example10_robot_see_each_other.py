#!/usr/bin/python3


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
    app = PySimbotApp(
        robot_cls=MyRobot,
        num_robots=2,
        robot_see_each_other=True,
        interval=REFRESH_INTERVAL,
        map="no_wall",
        enable_wasd_control=True,
        simulation_forever=True,
    )
    app.run()
