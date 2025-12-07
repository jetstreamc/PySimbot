from pysimbotlib.core.Global import ROBOT_MAX_SENSOR_DISTANCE
from pysimbotlib.core.Model.Robot import Robot


def test_distance_to_line_generators():
    sensor_coor = (0, 0)
    sensor_coverage_coor = (10, 0)

    # Line perpendicular to sensor ray at x=5
    line1 = ((5, -5), (5, 5))
    bounding_lines = [line1]

    gen = Robot.distance_to_line_generators(sensor_coor, sensor_coverage_coor, bounding_lines)
    distances = list(gen)
    assert len(distances) == 1
    assert distances[0] == 5.0

    # Line behind sensor
    line2 = ((-5, -5), (-5, 5))
    gen = Robot.distance_to_line_generators(sensor_coor, sensor_coverage_coor, [line2])
    distances = list(gen)
    assert distances[0] == ROBOT_MAX_SENSOR_DISTANCE


def test_distance_to_robot_generators():
    sensor_coor = (0, 0)
    sensor_coverage_coor = (10, 0)

    # Robot at (5, 0) with width 2 (radius 1)
    class MockRobot:
        center = (5, 0)
        width = 2

    gen = Robot.distance_to_robot_generators(sensor_coor, sensor_coverage_coor, [MockRobot()])
    distances = list(gen)
    # distance should be center distance (5) - radius (1) = 4 ??
    # Logic in Robot.py:
    # intersection = Geom.line_segment_circle_intersect(..., center, 0.5 * width)
    # near_intersection = intersection[0]
    # distance = Geom.distance(sensor_coor, near_intersection)

    # Intersections of line y=0 and circle (5,0, r=1) are (4,0) and (6,0).
    # Near is (4,0). Distance is 4.

    assert len(distances) == 2  # yields for each robot + ROBOT_MAX_SENSOR_DISTANCE at end
    assert distances[0] == 4.0
    assert distances[1] == ROBOT_MAX_SENSOR_DISTANCE


def test_min_distance_to_wall_or_obstacle():
    sensor_coor = (100, 100)
    sensor_coverage_coor = (110, 100)

    # Obstacle range x[105, 107], y[99, 101].
    # Ray (100,100)->(110,100) intersects left side at (105,100).
    obstacle_bboxes = ((105, 99, 2, 2),)

    dist = Robot._min_distance_to_wall_or_obstacle(obstacle_bboxes, sensor_coor, sensor_coverage_coor)
    assert dist == 5.0
