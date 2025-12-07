import math
from unittest.mock import MagicMock

import pytest
from kivy.tests.common import GraphicUnitTest

from pysimbotlib.core.app import PySimbotApp
from pysimbotlib.core.model.obstacle import Obstacle
from pysimbotlib.core.model.robot import Robot
from pysimbotlib.core.utils.geom import Geom
from pysimbotlib.core.utils.spatial_hash import SpatialHash


class MockSimbot:
    def __init__(self):
        self.obstacles = []
        self.objectives = []
        self._robot_list = []
        self.robot_see_each_other = False
        self.pos = (0, 0)  # Map origin at (0,0). Size (700, 600).
        self.spatial_hash = SpatialHash(100)  # Cell size 100

    def on_robot_eat(self, robot, obj):
        pass


def create_robot_with_spatial_hash():
    robot = Robot()
    sm = MockSimbot()
    robot._sm = sm
    return robot


class TestGeomExtended:
    def test_angle_normalization(self):
        # Robot handles turning by adding degrees. Normalization happens implicitly via trig functions?
        # Let's verify behavior.
        r = create_robot_with_spatial_hash()
        r.turn(370)
        # Expected: direction 370 or 10.
        # Robot normalizes to % 360.
        assert r._direction == 10

        # Test movement works correctly with > 360
        r.pos = (100, 100)
        r.move(10)
        # 370 degrees is 10 degrees.
        # angle 10 degrees (counter-clockwise?).
        # Robot turn logic: self._direction += angle.
        # If default direction is 0 (East).
        # Move logic: rad_angle = math.radians(-self._direction).
        # -370 = -10.
        # dx = cos(-10) = cos(10). dy = sin(-10) = -sin(10).
        # So moves slightly down-right.

        expected_x = 100 + 10 * math.cos(math.radians(-370))
        expected_y = 100 + 10 * math.sin(math.radians(-370))

        assert abs(r.x - expected_x) < 0.001
        assert abs(r.y - expected_y) < 0.001

    def test_circle_rect_intersect_strict(self):
        # Precise corner overlap
        # Rect (10,10) w=10, h=10. Range x[5,15], y[5,15]
        rect_center = (10, 10)
        rect_w = 10
        rect_h = 10

        # Circle at (16, 10). Radius 0.9. No overlap (dist to edge x=15 is 1.0 > 0.9)
        assert not Geom.is_circle_rect_intersect((16, 10), 0.9, rect_center, rect_w, rect_h)
        # Radius 1.1. Overlap.
        assert Geom.is_circle_rect_intersect((16, 10), 1.1, rect_center, rect_w, rect_h)


class TestRobotLogicExtended:
    def test_sensor_distance_no_obstacles(self):
        r = create_robot_with_spatial_hash()
        r.pos = (350, 300)  # Robot center roughly (360,310) - safe from walls
        r.size = (20, 20)  # Explicit size
        # Default max distance is 100.
        dists = r.distance()
        # Should be all 100
        assert all(d == 100 for d in dists)

    def test_sensor_distance_with_obstacle_ahead(self):
        r = create_robot_with_spatial_hash()
        # Robot center at (0,0) approx for logic if we set pos correctly
        r.size = (20, 20)
        r.pos = (100, 100)  # Inside map (100,100)

        # Obstacle ahead at +30 x.
        # Robot pos (100, 100). Robot's bounding box x range [100, 120].
        # Obstacle pos (130, 100). Obstacle's bounding box x range [130, 150].
        obs = Obstacle()
        obs.pos = (130, 100)
        obs.size = (20, 20)

        r._sm.obstacles.append(obs)
        r._sm.spatial_hash.insert(obs, 130, 100, 20, 20)

        # Robot facing 0 (East).
        # Let's check logic:
        # It calculates intersection of ray with rect.

        dists = r.distance()
        # Front sensor is index 0 (angle 0).
        # dist should be around 20 - 10 (radius) = 10?
        # Or if sensor is from center: 20.
        # Let's verify Model/Robot.py implementation detail:
        # It uses Geom.line_segment_rect_intersect with start=center, end=center+max_dist.
        # So it returns distance from CENTER.
        # If log shows "Distance: (100...)", and users sees "32" in example, implies subtract radius?
        # Wait, previous verification log showed (100, 32, ...).
        # In example2: Robot at (100, 300) approx?
        # Let's just assert it is detected (< 100) and roughly correct.

        front_dist = dists[0]
        assert front_dist < 100
        # If center (0,0) and obs x starts at 20. Dist from center to 20 is 20.
        # Sensor starts at edge (x=10).
        # Expected distance = 20 - 10 = 10.
        assert 9 <= front_dist <= 11

    def test_robot_map_boundary(self):
        r = create_robot_with_spatial_hash()
        r.size = (20, 20)

        # Place robot near right edge. Map width 700.
        # Robot width 20. Valid x range [0, 680].
        r.pos = (675, 300)

        # Move 10 units East (0 deg).
        # Should stop at x=680.
        r.move(10)

        assert abs(r.x - 680) < 0.001
        # It shouldn't be "stuck" completely (moved 5), but hit loop limit.
        # best_dist logic: will find max valid.

        # Try moving further when at boundary
        r.move(10)
        assert abs(r.x - 680) < 0.001
        assert r.stuck is True

    def test_spatial_hash_update_on_robot_move(self):
        r = create_robot_with_spatial_hash()
        r.size = (20, 20)
        r.pos = (100, 100)
        # on_pos should have inserted it into hash

        # Check hash
        nearby = r._sm.spatial_hash.get_nearby(100, 100, 20, 20)
        assert r in nearby

        # Move robot
        r.move(10)
        # New pos roughly (110, 100)

        # Check old pos hash - might still be there if buckets overlap,
        # but let's check new pos
        nearby_new = r._sm.spatial_hash.get_nearby(r.x, r.y, 20, 20)
        assert r in nearby_new

        # Move far away
        r.pos = (500, 500)
        nearby_old = r._sm.spatial_hash.get_nearby(100, 100, 20, 20)
        # Should NOT be in old spot
        assert r not in nearby_old
        nearby_far = r._sm.spatial_hash.get_nearby(500, 500, 20, 20)
        assert r in nearby_far


class TestSimbotManagement(GraphicUnitTest):
    def test_add_remove_robots(self):
        # Create App with real Simbot
        app = PySimbotApp(num_robots=0, num_objectives=0)
        simbot = app.simbot

        assert len(simbot.robots) == 0

        # Create robots
        simbot.num_robots = 2
        simbot._create_robots()

        assert len(simbot.robots) == 2
        assert len(simbot._robots.children) == 2

        # Verify robot valid position checker
        # The logic is internal to _create_robots loop.

        # Remove robots
        simbot._remove_all_robots_from_map()
        assert len(simbot._robots.children) == 0

    def test_robot_on_size_update_hash(self):
        r = create_robot_with_spatial_hash()
        # Force size change to trigger on_size
        r.size = (21, 21)
        # Check if hash has it
        assert len(r._sm.spatial_hash.get_nearby(0, 0, 1000, 1000)) > 0

        # Change size
        r.size = (40, 40)
        # Should update hash (remove old, add new).
        # We can mock update method to verify call.
        r._sm.spatial_hash.update = MagicMock()
        r.size = (50, 50)
        r._sm.spatial_hash.update.assert_called()

    def test_distance_invalid_index(self):
        r = Robot()
        with pytest.raises(ValueError):
            r.distance(index=100)

    def test_distance_valid_index(self):
        r = create_robot_with_spatial_hash()
        dist = r.distance(index=0)
        assert isinstance(dist, (float, int))
