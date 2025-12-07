#!/usr/bin/python3

"""
Example 7: UI Theming
=====================

This example shows how to change the application theme.
- `theme="light"` sets the UI to a light theme.
- Other options include "default" and "dark".
"""

from kivy.config import Config

from pysimbotlib.core import PySimbotApp

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set("kivy", "log_level", "info")


if __name__ == "__main__":
    # possible theme value: ["default", "light", "dark"]
    app = PySimbotApp(theme="light", enable_wasd_control=True)
    app.run()
