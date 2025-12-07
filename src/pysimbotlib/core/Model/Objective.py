#!/usr/bin/python3
from collections.abc import Sequence

from kivy.uix.widget import Widget


class Objective(Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault("size", (20, 20))
        kwargs.setdefault("size_hint", (None, None))
        self._sm = None
        super().__init__(**kwargs)

    def on_pos(self, instance, value):
        if self._sm and hasattr(self._sm, "spatial_hash"):
            self._sm.spatial_hash.update(self, value[0], value[1], self.width, self.height)


class ObjectiveWrapper(Widget):
    def get_objectives(self) -> Sequence[Objective]:
        return [obj for obj in self.children if isinstance(obj, Objective)]
