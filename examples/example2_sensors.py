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
        smell_value = self.smell()
        Logger.info(f"Smell Angle: {smell_value:.2f}")
        distances = self.distance()
        formatted = ", ".join(f"{d:5.1f}" for d in distances)
        Logger.info(f"Distance: ({formatted})")


if __name__ == "__main__":
    app = PySimbotApp(
        robot_cls=MyRobot,
        num_robots=1,
        interval=REFRESH_INTERVAL,
        enable_wasd_control=True,
        draw_rays=True,
    )
    app.run()
