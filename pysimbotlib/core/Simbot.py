#!/usr/bin/python3

import csv
import random

from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from .Global import SIMBOTMAP_SIZE
from .Objective import Objective, ObjectiveWrapper
from .Obstacle import ObstacleWrapper
from .Robot import RobotWrapper


class Simbot(BoxLayout):
    _robots = ObjectProperty(None)
    _obstacles = ObjectProperty(None)
    _objectives = ObjectProperty(None)

    iteration = NumericProperty(0)
    max_tick = NumericProperty(0)
    simulation_count = NumericProperty(0)

    # stats
    eat_count = NumericProperty(0)
    food_move_count = NumericProperty(0)
    score = NumericProperty(0)
    scoreStr = StringProperty("")

    def __init__(
        self,
        robot_cls,
        num_robots,
        num_objectives,
        robot_default_start_pos,
        obj_default_start_pos,
        customfn_create_robots=None,
        customfn_before_simulation=None,
        customfn_after_simulation=None,
        simulation_forever=False,
        food_move_after_eat=True,
        save_wasd_history=False,
        robot_see_each_other=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # initialize obstacles, objectives, and robot wrapper
        self._obstacles = ObstacleWrapper()
        self._objectives = ObjectiveWrapper()
        self._robots = RobotWrapper()
        self._objective_list = []
        self._robot_list = []

        # initialize robot creator function/params
        if customfn_create_robots:
            self.customfn_create_robots = customfn_create_robots
        else:
            self.robot_cls = robot_cls
            self.num_robots = num_robots
        self.robot_default_start_pos = robot_default_start_pos

        # initialize food creator params
        self.num_objectives = num_objectives
        self.obj_default_start_pos = obj_default_start_pos

        # intialize simulation parameters
        self._before_simulation = customfn_before_simulation if customfn_before_simulation else lambda simbot: None
        self._after_simulation = customfn_after_simulation if customfn_after_simulation else lambda simbot: None
        self.simulation_forever = simulation_forever
        self.food_move_after_eat = food_move_after_eat
        self.save_wasd_history = save_wasd_history
        self.robot_see_each_other = robot_see_each_other

    @property
    def robots(self):
        return self._robot_list

    @property
    def obstacles(self):
        return self._obstacles.get_obstacles()

    @property
    def objectives(self):
        return self._objectives.get_objectives()

    def _create_robots(self):
        self._robot_list = (
            self.customfn_create_robots()
            if hasattr(self, "customfn_create_robots")
            else [self.robot_cls() for _ in range(self.num_robots)]
        )
        for r in self._robot_list:
            r.pos = self.robot_default_start_pos
            trial_count = 0
            while not self.is_robot_pos_valid(r):
                r.pos = (
                    random.randrange(SIMBOTMAP_SIZE[0] - r.size[0]),
                    random.randrange(SIMBOTMAP_SIZE[1] - r.size[1]),
                )
                r._direction = random.randrange(360)
                trial_count += 1
                if trial_count == 500:
                    raise Exception("Can't find the place for spawning robots")
            r._sm = self
            self._robots.add_widget(r)

    def _create_objectives(self):
        self._objective_list = [Objective() for _ in range(self.num_objectives)]
        for obj in self._objective_list:
            obj.pos = self.obj_default_start_pos
            trial_count = 0
            while not self.is_objective_pos_valid(obj):
                obj.pos = (
                    random.randrange(SIMBOTMAP_SIZE[0] - obj.size[0]),
                    random.randrange(SIMBOTMAP_SIZE[1] - obj.size[1]),
                )
                trial_count += 1
                if trial_count == 500:
                    raise Exception("Can't find the place for spawning objective")
            self._objectives.add_widget(obj)

    def _remove_all_robots_from_map(self):
        self._robots.clear_widgets()
        self._robot_list.clear()

    def _remove_all_objectives_from_map(self):
        self._objectives.clear_widgets()
        self._objective_list.clear()

    def _reset_stats(self):
        self.eat_count = 0
        self.food_move_count = 0
        self.score = 0
        if self.food_move_after_eat:
            self.scoreStr = str(self.score) + " %"
        else:
            self.scoreStr = str(self.score)

    def add_history(self, robot, turn, move):
        distance = robot.distance()
        angle = robot.smell()
        if not self.history:
            self.history.append(("ir0", "ir1", "ir2", "ir3", "ir4", "ir5", "ir6", "ir7", "angle", "turn", "move"))
        self.history.append(list(distance) + [angle, turn, move])

    def process(self, dt):
        if self.iteration == 0:
            self._reset_stats()
            self._create_objectives()
            self._create_robots()
            self._before_simulation(self)
            self.history = []
            self.simulation_count += 1
            Logger.debug("Map: Start Simulation")
            self.iteration += 1

        elif self.iteration < self.max_tick:
            self.iteration += 1
            Logger.debug("Map: Start Iteration")
            for robot in self._robots.get_robots():
                robot.update()
            Logger.debug(f"Map: End Iteration: {self.iteration}")

            if self.iteration == self.max_tick:
                self._after_simulation(self)
                if self.save_wasd_history:
                    Logger.debug("History: Saving History")
                    with open(f"history{self.simulation_count}.csv", "w", newline="") as out_file:
                        csv_writer = csv.writer(out_file)
                        csv_writer.writerows(self.history if self.history else [["No history"]])

                Logger.debug(f"Map: End Simulation: {self.simulation_count}")
                if self.simulation_forever:
                    self._remove_all_robots_from_map()
                    self._remove_all_objectives_from_map()
                    self.iteration = 0

    def on_robot_eat(self, robot, obj):
        self.eat_count += 1
        if self.food_move_after_eat:
            self.food_move_count += 1
            self.change_objective_pos(obj)
            self.score = int(self.eat_count * 100 / self.food_move_count)
            self.scoreStr = str(self.score) + " %"
        else:
            self.score += 5
            self.scoreStr = str(self.score)

    def change_objective_pos(self, obj, pos=None):
        if pos:
            obj.pos = pos
        else:
            obj.pos = (
                random.randrange(SIMBOTMAP_SIZE[0] - obj.size[0]),
                random.randrange(SIMBOTMAP_SIZE[1] - obj.size[1]),
            )
            trial_count = 0
            while not self.is_objective_pos_valid(obj):
                obj.pos = (
                    random.randrange(SIMBOTMAP_SIZE[0] - obj.size[0]),
                    random.randrange(SIMBOTMAP_SIZE[1] - obj.size[1]),
                )
                trial_count += 1
                if trial_count == 500:
                    raise Exception("Can't find the place for spawning food")

    def is_objective_pos_valid(self, obj):
        pos = obj.pos
        # check wall
        if pos[0] <= 0 or pos[0] >= SIMBOTMAP_SIZE[0] - obj.size[0]:
            return False
        if pos[1] <= 0 or pos[1] >= SIMBOTMAP_SIZE[1] - obj.size[1]:
            return False

        # check obstacles
        for obs in self.obstacles:
            if (
                obs.pos[0] <= pos[0] <= obs.pos[0] + obs.size[0]
                or obs.pos[0] <= pos[0] + obj.size[0] <= obs.pos[0] + obs.size[0]
            ) and (
                obs.pos[1] <= pos[1] <= obs.pos[1] + obs.size[1]
                or obs.pos[1] <= pos[1] + obj.size[1] <= obs.pos[1] + obs.size[1]
            ):
                return False

        # check robots
        for r in self._robot_list:
            if (
                r.pos[0] <= pos[0] <= r.pos[0] + r.size[0] or r.pos[0] <= pos[0] + obj.size[0] <= r.pos[0] + r.size[0]
            ) and (
                r.pos[1] <= pos[1] <= r.pos[1] + r.size[1] or r.pos[1] <= pos[1] + obj.size[1] <= r.pos[1] + r.size[1]
            ):
                return False

        # check other objectives
        for o in self._objective_list:
            if obj == o:
                continue
            if (
                o.pos[0] <= pos[0] <= o.pos[0] + o.size[0] or o.pos[0] <= pos[0] + obj.size[0] <= o.pos[0] + o.size[0]
            ) and (
                o.pos[1] <= pos[1] <= o.pos[1] + o.size[1] or o.pos[1] <= pos[1] + obj.size[1] <= o.pos[1] + o.size[1]
            ):
                return False

        return True

    def is_robot_pos_valid(self, robot):
        pos = robot.pos
        if pos[0] <= 0 or pos[0] >= SIMBOTMAP_SIZE[0] - robot.size[0]:
            return False
        if pos[1] <= 0 or pos[1] >= SIMBOTMAP_SIZE[1] - robot.size[1]:
            return False

        # check obstacles
        for obs in self.obstacles:
            if (
                obs.pos[0] <= pos[0] <= obs.pos[0] + obs.size[0]
                or obs.pos[0] <= pos[0] + robot.size[0] <= obs.pos[0] + obs.size[0]
            ) and (
                obs.pos[1] <= pos[1] <= obs.pos[1] + obs.size[1]
                or obs.pos[1] <= pos[1] + robot.size[1] <= obs.pos[1] + obs.size[1]
            ):
                return False

        # check other robots
        if self.robot_see_each_other:
            for r in self._robot_list:
                if robot == r:
                    continue
                if (
                    r.pos[0] <= pos[0] <= r.pos[0] + r.size[0]
                    or r.pos[0] <= pos[0] + robot.size[0] <= r.pos[0] + r.size[0]
                ) and (
                    r.pos[1] <= pos[1] <= r.pos[1] + r.size[1]
                    or r.pos[1] <= pos[1] + robot.size[1] <= r.pos[1] + r.size[1]
                ):
                    return False

        return True


class PySimbotMap(Widget):
    def __init__(self, simbot, enable_wasd_control=False, save_wasd_history=False, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.enable_wasd_control = enable_wasd_control
        self.save_wasd_history = save_wasd_history

        self.add_widget(simbot._obstacles)
        self.add_widget(simbot._objectives)
        self.add_widget(simbot._robots)

        self.simbot = simbot
        self.size = SIMBOTMAP_SIZE

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if not self.simbot.robots:
            return
        if self.simbot.iteration >= self.simbot.max_tick:
            return
        if keycode[1] == "n":
            for obj in self.simbot.objectives:
                self.simbot.change_objective_pos(obj)
                self.simbot.food_move_count += 1
                self.simbot.score = int(self.simbot.eat_count * 100 / self.simbot.food_move_count)
        elif keycode[1] == "w" and self.enable_wasd_control:
            r = self.simbot.robots[0]
            self.simbot.add_history(r, 0, 5)
            r.move(5)
        elif keycode[1] == "a" and self.enable_wasd_control:
            r = self.simbot.robots[0]
            self.simbot.add_history(r, -5, 0)
            r.turn(-5)
        elif keycode[1] == "d" and self.enable_wasd_control:
            r = self.simbot.robots[0]
            self.simbot.add_history(r, 5, 0)
            r.turn(5)
        elif keycode[1] == "s" and self.enable_wasd_control:
            r = self.simbot.robots[0]
            self.simbot.add_history(r, 0, -5)
            r.move(-5)
        elif keycode[1] == "q" and self.enable_wasd_control:
            r = self.simbot.robots[0]
            self.simbot.add_history(r, -5, 5)
            r.turn(-5)
            r.move(5)
        elif keycode[1] == "e" and self.enable_wasd_control:
            r = self.simbot.robots[0]
            self.simbot.add_history(r, 5, 5)
            r.turn(5)
            r.move(5)
