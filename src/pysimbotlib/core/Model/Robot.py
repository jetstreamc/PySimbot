#!/usr/bin/python3

import math
from collections.abc import Generator, Iterable, Sequence
from functools import cache
from itertools import chain

from kivy.logger import Logger
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.uix.widget import Widget

from ..Utils.Geom import Geom
from ..Utils.Global import ROBOT_DISTANCE_ANGLES, ROBOT_MAX_SENSOR_DISTANCE, SIMBOTMAP_BOUNDING_LINES, SIMBOTMAP_SIZE
from .Entity import Entity
from .Objective import Objective
from .Obstacle import Obstacle


class Robot(Entity):
    # Facing 0 degree direction
    _sm = None
    _direction = NumericProperty(0)

    # Defaults from original KV
    # We set these in __init__ to ensure they override the Entity defaults properly
    def __init__(self, **kwargs):
        kwargs.setdefault("width", 20)
        kwargs.setdefault("height", 20)
        super().__init__(**kwargs)

    _color_r = NumericProperty(0.7)
    _color_g = NumericProperty(0)
    _color_b = NumericProperty(0)
    _color_a = NumericProperty(1)

    color = ReferenceListProperty(_color_r, _color_g, _color_b, _color_a)

    eat_count: int = 0
    collision_count: int = 0
    just_eat: bool = False
    stuck: bool = False

    def get_obstacles_bboxes(self) -> Generator[Geom.BBox, None, None]:
        if not hasattr(self, "_cached_bboxes"):
            self._cached_bboxes = tuple((obs.x, obs.y, obs.width, obs.height) for obs in self._sm.obstacles)
        return self._cached_bboxes

    @staticmethod
    def distance_to_line_generators(
        sensor_coor: Geom.Point2D, sensor_coverage_coor: Geom.Point2D, bounding_lines
    ) -> Generator[float, None, None]:
        for line in bounding_lines:
            intersection = Geom.line_segment_intersect(sensor_coor, sensor_coverage_coor, line[0], line[1])
            yield (Geom.distance(sensor_coor, intersection) if intersection else ROBOT_MAX_SENSOR_DISTANCE)

    @staticmethod
    def distance_to_robot_generators(
        sensor_coor: Geom.Point2D, sensor_coverage_coor: Geom.Point2D, robots
    ) -> Generator[float, None, None]:
        for r in robots:
            intersection = Geom.line_segment_circle_intersect(
                sensor_coor, sensor_coverage_coor, r.center, 0.5 * r.width
            )
            near_intersection = intersection[0]
            yield (Geom.distance(sensor_coor, near_intersection) if near_intersection else ROBOT_MAX_SENSOR_DISTANCE)
        yield ROBOT_MAX_SENSOR_DISTANCE

    @staticmethod
    @cache
    def _min_distance_to_wall_or_obstacle(
        obstacle_bboxes: Iterable[Geom.BBox], sensor_coor: Geom.Point2D, sensor_coverage_coor: Geom.Point2D
    ) -> float:
        obstacle_bounding_lines: Generator[Geom.Line] = (
            line for line in Geom.all_bounding_lines_generator(obstacle_bboxes)
        )
        min_distance_to_wall_or_obs = min(
            Robot.distance_to_line_generators(
                sensor_coor, sensor_coverage_coor, chain(SIMBOTMAP_BOUNDING_LINES, obstacle_bounding_lines)
            )
        )
        return min_distance_to_wall_or_obs

    def _distance(self, angle: float) -> float:
        rad_angle = math.radians(-(self._direction + angle))
        unit_x = math.cos(rad_angle)
        unit_y = math.sin(rad_angle)

        # Point2D that represents sensor coordinate. It must be located at the robot edge.
        sensor_coor = (
            self.center_x + 0.5 * self.width * unit_x,
            self.center_y + 0.5 * self.height * unit_y,
        )

        # Point2D that represents coordinates that sensor can be reached. It is outside the robot.
        sensor_coverage_coor = (
            sensor_coor[0] + unit_x * ROBOT_MAX_SENSOR_DISTANCE,
            sensor_coor[1] + unit_y * ROBOT_MAX_SENSOR_DISTANCE,
        )

        obstacle_bboxes = self.get_obstacles_bboxes()
        min_distance_to_wall_and_obs = Robot._min_distance_to_wall_or_obstacle(
            obstacle_bboxes, sensor_coor, sensor_coverage_coor
        )

        if self._sm.robot_see_each_other:
            x = min(sensor_coor[0], sensor_coverage_coor[0])
            y = min(sensor_coor[1], sensor_coverage_coor[1])
            w = abs(sensor_coor[0] - sensor_coverage_coor[0])
            h = abs(sensor_coor[1] - sensor_coverage_coor[1])
            ROI = (x, y, w, h)
            other_robots_in_ROI = (
                r
                for r in self._sm._robot_list
                if r != self and Geom.is_bbox_overlap(ROI, (r.x, r.y, r.width, r.height))
            )
            min_distance_to_other_robot = min(
                Robot.distance_to_robot_generators(sensor_coor, sensor_coverage_coor, other_robots_in_ROI)
            )
            return min(min_distance_to_wall_and_obs, min_distance_to_other_robot)
        else:
            return min_distance_to_wall_and_obs

    def _is_robot_inside_map(self, p: Geom.Point2D = None) -> bool:
        if p is None:
            p = self.pos

        robot_radius = 0.5 * self.width
        robot_center = (p[0] + robot_radius, p[1] + robot_radius)

        map_pos = self._sm.pos
        map_half_width = 0.5 * SIMBOTMAP_SIZE[0]
        map_half_height = 0.5 * SIMBOTMAP_SIZE[1]
        map_center = (map_pos[0] + map_half_width, map_pos[1] + map_half_height)

        dx = abs(robot_center[0] - map_center[0])
        dy = abs(robot_center[1] - map_center[1])

        if dx > (map_half_width - robot_radius) or dy > (map_half_height - robot_radius):
            return False
        return True

    def _is_robot_collide_obstacles(self, p: Geom.Point2D, obstacles_included: Iterable[Obstacle] = None) -> bool:
        if obstacles_included is None:
            obstacles_included = self._sm.obstacles

        if p is None:
            p = self.pos

        robot_radius = 0.5 * self.width
        robot_center = (p[0] + robot_radius, p[1] + robot_radius)

        # Check obstacles
        for obs in obstacles_included:
            obs_pos = obs.pos
            obs_width, obs_height = obs.size
            obs_center = (obs_pos[0] + 0.5 * obs_width, obs_pos[1] + 0.5 * obs_height)

            if Geom.is_circle_rect_intersect(robot_center, robot_radius, obs_center, obs_width, obs_height):
                return True

        return False

    def _is_robot_collide_others(self, p: Geom.Point2D) -> bool:
        if p is None:
            p = self.pos

        robot_radius = 0.5 * self.width
        robot_center = (p[0] + robot_radius, p[1] + robot_radius)

        for r in self._sm._robot_list:
            if r != self and Geom.distance(r.center, robot_center) <= 2 * robot_radius:
                return True

        return False

    def _is_valid_position(self, next_position: Geom.Point2D) -> bool:
        if not self._is_robot_inside_map(next_position):
            return False

        if self._is_robot_collide_obstacles(next_position):
            return False

        if self._sm.robot_see_each_other and self._is_robot_collide_others(next_position):
            return False

        return True

    def _get_overlap_objective(self) -> Objective | None:
        robot_center = self.center
        robot_radius = 0.5 * self.size[0]
        for obj in self._sm.objectives:
            obj_width, obj_height = obj.size
            obj_center = (obj.pos[0] + 0.5 * obj_width, obj.pos[1] + 0.5 * obj_height)
            if Geom.is_circle_rect_intersect(robot_center, robot_radius, obj_center, obj_width, obj_height):
                return obj
        return None

    def set_color(self, r: float, g: float, b: float, a: float = 1) -> None:
        self._color_r = r
        self._color_g = g
        self._color_b = b
        self._color_a = a

    def distance(self, index: int | None = None) -> Sequence[float] | float:
        if index is None:
            return tuple(self._distance(angle) for angle in ROBOT_DISTANCE_ANGLES)
        if isinstance(index, int):
            if index < 0 or index >= len(ROBOT_DISTANCE_ANGLES):
                raise ValueError(
                    f"Invalid distance sensor index: {index}. "
                    f"The valid values are between 0 and {len(ROBOT_DISTANCE_ANGLES) - 1}"
                )
            else:
                return self._distance(ROBOT_DISTANCE_ANGLES[index])

    def calc_angle_to_objective(self, obj: Widget) -> float:
        dx = obj.center_x - self.center_x
        dy = obj.center_y - self.center_y
        rad = math.atan2(dy, dx)
        deg = -(math.degrees(rad) + self._direction) % 360
        return deg if deg <= 180 else deg - 360

    def smell(self, index: int = 0) -> float:
        if index < 0 or index >= len(self._sm.objectives):
            raise ValueError(
                f"Cannot smell the objective indexed at {index}. "
                f"The valid values are between 0 and {len(self._sm.objectives) - 1}"
            )
        return self.calc_angle_to_objective(self._sm.objectives[index])

    def smell_nearest(self) -> float:
        nearest_food = min(self._sm.objectives, key=lambda food: Geom.distance(self.pos, food.pos))
        return self.calc_angle_to_objective(nearest_food)

    def turn(self, degree: float = 1.0) -> None:
        self._direction = (self._direction + degree) % 360
        self.stuck = False

    def move(self, step: int = 1) -> None:
        if step >= 0:
            rad_angle = math.radians(-self._direction)
            step = int(step)
        else:
            rad_angle = math.radians(180 - self._direction)
            step = int(-step)
        dx = math.cos(rad_angle)
        dy = math.sin(rad_angle)

        self.stuck = False
        next_position = (self.pos[0] + step * dx, self.pos[1] + step * dy)
        # check if the robot cannot go by longest distance.
        if not self._is_valid_position(next_position):
            # Binary search for the furthest valid position
            low = 0
            high = step
            best_dist = 0

            while low <= high:
                mid = (low + high) // 2
                check_pos = (self.pos[0] + mid * dx, self.pos[1] + mid * dy)
                if self._is_valid_position(check_pos):
                    best_dist = mid
                    low = mid + 1
                else:
                    high = mid - 1

            # The robot is stuck if the best distance it can move is 0
            if best_dist == 0:
                self.stuck = True

            # Update collision count if we couldn't complete the full step
            if best_dist < step:
                self.collision_count += 1

            next_position = (self.pos[0] + best_dist * dx, self.pos[1] + best_dist * dy)

        self.pos = next_position

        obj = self._get_overlap_objective()
        if not obj:
            self.just_eat = False
        elif obj and not self.just_eat:
            Logger.debug(f"Robot: Eat Objective at [{obj.pos[0]}, {obj.pos[1]}]")
            self._sm.on_robot_eat(self, obj)
            self.eat_count += 1
            self.just_eat = True

    def update(self) -> None:
        pass


class RobotWrapper(Widget):
    def get_robots(self) -> Generator[Robot, None, None]:
        # This wrapper now holds RobotViews, but Simbot might expect Robots.
        # This needs careful handling.
        # If Simbot uses this to iterate generic children, it gets Views.
        # But Simbot logic expects Robot Models.

        # We should NOT use this wrapper to access models anymore.
        # Models should be in self.simbot.robots list.
        # But for backward compat of this specific helper method:
        return (view.model for view in self.children if hasattr(view, "model") and isinstance(view.model, Robot))
