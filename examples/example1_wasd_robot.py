#!/usr/bin/python3

"""
Example 1: WASD Robot Control
=============================

This example demonstrates how to control a robot using the WASD keys.
- 'w': Move forward
- 's': Move backward
- 'a': Turn left
- 'd': Turn right
- 'q': Turn left and move forward
- 'e': Turn right and move forward
"""

from kivy.config import Config

from pysimbotlib.core import PySimbotApp

# One of ['trace', 'debug', 'info', 'warning', 'error', 'critical']
# Force the program to show user's log only for "debug" level or more.
Config.set("kivy", "log_level", "debug")

if __name__ == "__main__":
    app = PySimbotApp(enable_wasd_control=True)
    app.run()
