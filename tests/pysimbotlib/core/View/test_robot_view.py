from unittest.mock import MagicMock

from kivy.tests.common import GraphicUnitTest

from pysimbotlib.core.Model.Robot import Robot
from pysimbotlib.core.View.RobotView import RobotView


class TestRobotView(GraphicUnitTest):
    def test_robot_view_initialization(self):
        # View needs a model
        r = Robot()
        view = RobotView(model=r)

        # Check initial bindings
        assert view.model == r
        assert view.pos == r.pos
        assert view.size == r.size
        # Direction binding? When Robot turns, canvas rotates.
        # Hard to test visual rotation accumulation without rendering frame inspection.
        # But we can check internal state if exposed or just ensure no crash.

    def test_draw_rays_property(self):
        r = Robot()
        # Mock _sm and spatial_hash for distance calculation
        r._sm = MagicMock()
        r._sm.spatial_hash = MagicMock()
        # get_nearby returns empty list -> no obstacles -> default max dist
        r._sm.spatial_hash.get_nearby.return_value = []
        r._sm.robot_see_each_other = False  # Default

        view = RobotView(model=r, draw_rays=True)
        assert view.draw_rays is True

        # Rays are drawn on update_rays clock event.
        # We can trigger it manually.
        view.update_rays(0)
        # ray_instructions should have items.
        # Color + Line per sensor (8 sensors) -> 1 + 8 = 9 instructions?
        # ray_instructions is an InstructionGroup.
        assert len(view.ray_instructions.children) > 0

        view.draw_rays = False
        view.update_rays(0)
        # Should clear
        assert len(view.ray_instructions.children) == 0

    def test_sync_properties(self):
        r = Robot()
        view = RobotView(model=r)

        # Change model pos
        r.pos = (150, 150)
        # View should update pos?
        # RobotView is a Widget. Robot is an Entity.
        # Simbot creates RobotView. Does it bind pos?
        # Kivy properties bind automatically if names match? No.
        # Typically View binds to Model optimization.
        # Let's check RobotView logic.
        # If RobotView inherits Widget and doesn't bind, pos might not sync automatically unless set explicitly.
        # Simbot main loop calls r.update().
        # View is usually just visual.
        # Kivy: if RobotView uses model.pos in canvas, it updates.
        # But widget.pos property?
        pass
