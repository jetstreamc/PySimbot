#!/usr/bin/python3

import os
import platform

if platform.system() == "Linux" or platform.system() == "Darwin":
    os.environ["KIVY_VIDEO"] = "ffpyplayer"

from kivy.config import Config

from pysimbotlib.core import PySimbotApp

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set("kivy", "log_level", "info")


if __name__ == "__main__":
    # possible map value: ["default", "no_wall"]
    app = PySimbotApp(map="no_wall", enable_wasd_control=True)
    app.run()
