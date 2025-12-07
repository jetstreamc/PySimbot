#!/usr/bin/python3


from kivy.config import Config

from pysimbotlib.core import PySimbotApp

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set("kivy", "log_level", "info")


if __name__ == "__main__":
    # possible theme value: ["default", "light", "dark"]
    app = PySimbotApp(theme="light", enable_wasd_control=True)
    app.run()
