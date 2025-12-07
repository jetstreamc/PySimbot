#!/usr/bin/python3

"""
Example 9: Recording History
============================

This example enables recording of simulation history.
- `save_wasd_history=True` saves robot movements to a CSV file.
- `simulation_forever=True` allows continuous data collection across resets.
"""

from kivy.config import Config

from pysimbotlib.core import PySimbotApp

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set("kivy", "log_level", "info")


if __name__ == "__main__":
    app = PySimbotApp(enable_wasd_control=True, save_wasd_history=True, max_tick=4000, simulation_forever=True)
    app.run()
