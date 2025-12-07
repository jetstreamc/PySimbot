#!/usr/bin/python3

import os
import platform

if platform.system() == "Linux" or platform.system() == "Darwin":
    os.environ["KIVY_VIDEO"] = "ffpyplayer"

from kivy.config import Config

from pysimbotlib.core import PySimbotApp

# One of ['trace', 'debug', 'info', 'warning', 'error', 'critical']
# Force the program to show user's log only for "debug" level or more.
Config.set("kivy", "log_level", "debug")

if __name__ == "__main__":
    app = PySimbotApp(enable_wasd_control=True)
    app.run()
