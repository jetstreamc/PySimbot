#!/usr/bin/python3
from collections.abc import Generator

from kivy.uix.widget import Widget


class Obstacle(Widget):
    pass


class ObstacleWrapper(Widget):
    def get_obstacles(self) -> Generator[Obstacle, None, None]:
        return (obstacle for obstacle in self.children if isinstance(obstacle, Obstacle))
