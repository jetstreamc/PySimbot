import os

# Set Kivy to use ffpyplayer video provider for better cross-platform compatibility
os.environ["KIVY_VIDEO"] = "ffpyplayer"

from . import core as core
