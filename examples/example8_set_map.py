#!/usr/bin/python3

"""
Example 8: Map Selection
========================

This example demonstrates how to select different simulation maps.
- `map="no_wall"` loads a map configuration without boundary walls.
- "default" is the standard map.
"""

from kivy.config import Config

from pysimbotlib.core import PySimbotApp

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set("kivy", "log_level", "info")


if __name__ == "__main__":
    # possible map value: ["default", "no_wall"]
    app = PySimbotApp(map="no_wall", enable_wasd_control=True)
    app.run()
