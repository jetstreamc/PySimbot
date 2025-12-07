# Kivy needs a window to apply KV rules sometimes, or at least the Builder needs to be loaded.
# Simbot loads 'pysimbotlib/core/pysimbot.kv' usually via App or locally?
# The KV files are in 'themes/'. Simbot.py doesn't seem to load them explicitly, App does.
# We will simulate App loading default.kv
from kivy.lang import Builder

from pysimbotlib.core.Objective import Objective

try:
    Builder.load_file("pysimbotlib/themes/default.kv")
except:
    pass  # Might fail if file not found relative to here

o = Objective()
print(f"Objective Size: {o.size}")
if o.width == 20:
    print("SUCCESS: Width is 20")
else:
    print(f"FAILURE: Width is {o.width} (Expected 20)")
