from kivy.clock import Clock
from kivy.logger import Logger

from ..Model.SimulationModel import SimulationModel
from ..Utils.Geom import Geom


class SimulationController:
    def __init__(self, model: SimulationModel):
        self.model = model
        self.max_tick = 0
        self.simulation_forever = False
        self.save_wasd_history = False
        self.food_move_after_eat = True
        self.history = []

        # User defined hooks
        self._before_simulation = lambda sim: None
        self._after_simulation = lambda sim: None

    def start(self, interval=1.0 / 60.0):
        Clock.schedule_interval(self.process, interval)

    def stop(self):
        Clock.unschedule(self.process)

    def process(self, dt):
        model = self.model

        if model.iteration == 0:
            self._reset_stats()
            # Entity creation should ideally happen via factory/builder,
            # but for now we assume they might be pre-populated or we call a setup method.
            # IN TRANSITION: We rely on the App/Simbot to populate the model initially,
            # or we move creation logic here.

            self._before_simulation(self)
            self.history = []
            model.simulation_count += 1
            Logger.debug("Controller: Start Simulation")
            model.increment_iteration()

        elif model.iteration < self.max_tick:
            model.increment_iteration()
            Logger.debug("Controller: Start Iteration")

            # Update all robots
            for robot in model.robots:
                if hasattr(robot, "update"):
                    robot.update()

            Logger.debug(f"Controller: End Iteration: {model.iteration}")

            if model.iteration == self.max_tick:
                self._after_simulation(self)
                if self.save_wasd_history:
                    self._save_history()

                Logger.debug(f"Controller: End Simulation: {model.simulation_count}")
                if self.simulation_forever:
                    self._reset_round()

    def _reset_stats(self):
        self.model.score = 0
        if self.food_move_after_eat:
            self.model.scoreStr = str(self.model.score) + " %"
        else:
            self.model.scoreStr = str(self.model.score)

    def is_valid_position(self, pos, size, exclude_obj=None):
        # Generic check for any entity placement
        # Used for initial spawning
        map_w, map_h = self.model.map_size
        w, h = size

        # Check walls
        if pos[0] <= 0 or pos[0] >= map_w - w:
            return False
        if pos[1] <= 0 or pos[1] >= map_h - h:
            return False

        # Check obstacles
        for obs in self.model.obstacles:
            if exclude_obj and obs == exclude_obj:
                continue
            if Geom.is_bbox_overlap((pos[0], pos[1], w, h), (obs.x, obs.y, obs.width, obs.height)):
                return False

        # Check robots
        for r in self.model.robots:
            if exclude_obj and r == exclude_obj:
                continue
            if Geom.is_bbox_overlap((pos[0], pos[1], w, h), (r.x, r.y, r.width, r.height)):
                return False

        return True

    def _reset_round(self):
        # Logic to clear entities and restart
        self.model.robots.clear()
        self.model.objectives.clear()
        self.model.reset_iteration()

    def _save_history(self):
        Logger.debug("History: Saving History")
        import csv

        with open(f"history{self.model.simulation_count}.csv", "w", newline="") as out_file:
            csv_writer = csv.writer(out_file)
            csv_writer.writerows(self.history if self.history else [["No history"]])
