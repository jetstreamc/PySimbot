from collections import defaultdict
from typing import Generic, TypeVar

T = TypeVar("T")


class SpatialHash(Generic[T]):
    def __init__(self, cell_size: int):
        self.cell_size = cell_size
        self.grid = defaultdict(set)
        self._objects = {}  # Map object -> set of cell keys

    def _get_cell_key(self, x: float, y: float) -> tuple[int, int]:
        return int(x / self.cell_size), int(y / self.cell_size)

    def _get_cell_keys_for_bbox(self, x: float, y: float, w: float, h: float):
        start_x, start_y = self._get_cell_key(x, y)
        end_x, end_y = self._get_cell_key(x + w, y + h)

        keys = set()
        for i in range(start_x, end_x + 1):
            for j in range(start_y, end_y + 1):
                keys.add((i, j))
        return keys

    def insert(self, obj: T, x: float, y: float, w: float, h: float):
        keys = self._get_cell_keys_for_bbox(x, y, w, h)
        self._objects[obj] = keys
        for key in keys:
            self.grid[key].add(obj)

    def remove(self, obj: T):
        if obj in self._objects:
            keys = self._objects[obj]
            for key in keys:
                self.grid[key].discard(obj)
                if not self.grid[key]:
                    del self.grid[key]
            del self._objects[obj]

    def update(self, obj: T, x: float, y: float, w: float, h: float):
        # Only update if the cell keys have changed?
        # For simplicity, remove and insert.
        # Optimization: check if keys are same.
        new_keys = self._get_cell_keys_for_bbox(x, y, w, h)
        old_keys = self._objects.get(obj)

        if old_keys == new_keys:
            return

        self.remove(obj)
        self._objects[obj] = new_keys
        for key in new_keys:
            self.grid[key].add(obj)

    def get_nearby(self, x: float, y: float, w: float, h: float) -> set[T]:
        keys = self._get_cell_keys_for_bbox(x, y, w, h)
        nearby = set()
        for key in keys:
            nearby.update(self.grid.get(key, []))
        return nearby
