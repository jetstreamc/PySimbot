from kivy.event import EventDispatcher
from kivy.properties import ListProperty, NumericProperty, StringProperty

# RobotEntity import will be added later or we use generic Entity for now to avoid circular deps if Robot is in separate file


class SimulationModel(EventDispatcher):
    # State Properties
    robots = ListProperty([])
    obstacles = ListProperty([])
    objectives = ListProperty([])

    score = NumericProperty(0)
    scoreStr = StringProperty("")
    iteration = NumericProperty(0)
    simulation_count = NumericProperty(1)

    map_size = ListProperty([900, 600])  # Default, can be updated

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_robot(self, robot):
        self.robots.append(robot)

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def add_objective(self, objective):
        self.objectives.append(objective)

    def reset_iteration(self):
        self.iteration = 0

    def increment_iteration(self):
        self.iteration += 1
