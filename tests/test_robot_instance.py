from unittest.mock import MagicMock

from pysimbotlib.core.Robot import Robot


class MockSimbot:
    def __init__(self):
        self.obstacles = []
        self.objectives = []
        self._robot_list = []
        self.robot_see_each_other = False
        # Center the map at (0,0) assuming size 900x600
        self.pos = (-450, -300)

    def on_robot_eat(self, robot, obj):
        pass


# Helper to create a robot with a mocked Simbot
def create_robot():
    robot = Robot()
    robot._sm = MockSimbot()
    return robot


def test_robot_move_simple():
    r = create_robot()
    # Default pos (0,0). Center (10,10). Dir 0.
    # Move 10. dx=1, dy=0.
    r.move(10)
    assert r.pos == [10, 0]


def test_robot_turn():
    r = create_robot()
    # Initial direction 0
    r.turn(90)
    assert r._direction == 90

    r.move(10)
    # Dir 90. rad -90. dx=0, dy=-1.
    # Pos (0,0) -> (0, -10)
    assert abs(r.pos[0]) < 0.0001
    assert abs(r.pos[1] + 10) < 0.0001


def test_robot_smell():
    r = create_robot()
    # Align robot center to (0,0) for simpler math
    r.pos = (-10, -10)

    # Add an objective
    obj = MagicMock()
    # Objective at (10,0)
    obj.center_x = 10
    obj.center_y = 0
    obj.pos = (10, 0)
    r._sm.objectives.append(obj)

    # Robot center (0,0), facing 0. Objective at (10,0). Angle should be 0.
    angle = r.smell(0)
    assert angle == 0.0

    # Robot facing 90.
    r.turn(90)
    # Relative angle: 0 - 90 = -90.
    angle = r.smell(0)
    assert angle == -90.0


def test_robot_eat():
    r = create_robot()
    # Align robot center to (0,0)
    r.pos = (-10, -10)

    # Place objective at center (2,0)
    obj = MagicMock()
    obj.size = (2, 2)
    obj.pos = (1, -1)
    # Mock Widget properties if accessed directly

    r._sm.objectives.append(obj)

    # Move robot (internal update)
    r.move(0)
    assert r.eat_count == 1
    assert r.just_eat is True
