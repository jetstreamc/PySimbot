#!/usr/bin/python3
from collections.abc import Sequence

from kivy.uix.widget import Widget


class Objective(Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault("size", (20, 20))
        kwargs.setdefault("size_hint", (None, None))
        super().__init__(**kwargs)


class ObjectiveWrapper(Widget):
    def get_objectives(self) -> Sequence[Objective]:
        return [obj for obj in self.children if isinstance(obj, Objective)]
