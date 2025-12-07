from kivy.tests.common import GraphicUnitTest

from pysimbotlib.core.app import PySimbotApp
from pysimbotlib.core.model.objective import Objective
from pysimbotlib.core.model.obstacle import Obstacle
from pysimbotlib.core.model.robot import Robot


class TestSpatialHashIntegration(GraphicUnitTest):
    def test_objective_integration(self):
        app = PySimbotApp(num_robots=1, num_objectives=0)  # Start with 0 objectives
        simbot = app.simbot

        # Manually create an objective and add it
        obj = Objective()
        obj.pos = (100, 100)
        obj.size = (20, 20)

        # Verify it's not in spatial hash yet (since not added to simbot yet or added manually without injection)
        # Actually Simbot adds widgets, but injection happens in _create_objectives or manual additions need care?
        # In Simbot.py we modified _create_objectives.
        # But if we use simbot.objectives property it returns children.

        # Let's simulate what _create_objectives does but for a single obj
        simbot._objectives.add_widget(obj)
        obj._sm = simbot
        simbot.spatial_hash.insert(obj, obj.x, obj.y, obj.width, obj.height)

        # Verify it is in spatial hash
        nearby = simbot.spatial_hash.get_nearby(100, 100, 20, 20)
        assert obj in nearby, "Objective should be in spatial hash"

        # Move objective
        obj.pos = (200, 200)

        # Verify it moved in spatial hash
        nearby_old = simbot.spatial_hash.get_nearby(100, 100, 20, 20)
        assert obj not in nearby_old, "Objective should have moved from old position"

        nearby_new = simbot.spatial_hash.get_nearby(200, 200, 20, 20)
        assert obj in nearby_new, "Objective should be in new position"

    def test_robot_collision_queries_spatial_hash(self):
        app = PySimbotApp(num_robots=1, num_objectives=0)
        simbot = app.simbot

        # Setup robot
        robot = Robot()
        robot._sm = simbot
        robot.pos = (50, 50)

        # Setup obstacle in spatial hash
        obs = Obstacle()
        obs.pos = (60, 60)  # Overlapping
        obs.size = (20, 20)
        simbot.spatial_hash.insert(obs, obs.x, obs.y, obs.width, obs.height)

        # We need to mock _sm.obstacles to be empty to PROVE it uses spatial hash
        # If it used _sm.obstacles (iterating children), it might fail if we don't add to children.
        # But Robot.py now prefers spatial hash.

        # Ensure obstacle is NOT in simbot._obstacles children
        assert obs not in simbot.obstacles

        # Check collision
        is_collide = robot._is_robot_collide_obstacles((50, 50))
        assert is_collide, "Robot should detect collision via spatial hash even if obstacle not in main list"

    def test_robot_objective_queries_spatial_hash(self):
        app = PySimbotApp(num_robots=1, num_objectives=0)
        simbot = app.simbot

        # Setup robot
        robot = Robot()
        robot._sm = simbot
        robot.pos = (50, 50)
        robot.size = (20, 20)

        # Setup objective in spatial hash
        obj = Objective()
        obj.pos = (50, 50)
        obj.size = (20, 20)
        # Hack inject into spatial hash without adding to simbot list
        simbot.spatial_hash.insert(obj, obj.x, obj.y, obj.width, obj.height)

        # Ensure obj NOT in simbot.objectives
        assert obj not in simbot.objectives

        # Check sensing
        found_obj = robot._get_overlap_objective()
        assert found_obj == obj, "Robot should find objective via spatial hash"
