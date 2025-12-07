from unittest.mock import MagicMock

from kivy.tests.common import GraphicUnitTest
from kivy.uix.widget import Widget

from pysimbotlib.core.Utils.Scaler import Scaler


class TestScaler(GraphicUnitTest):
    def test_scaler_init(self):
        # Initializing widget in GraphicUnitTest usually requires attaching to event loop?
        # Or explicit initialization if using Builder.
        s = Scaler()
        assert s.scale == 2
        # Container should be created by Builder rule if updated
        # GraphicUnitTest ensures kv rules are applied if loaded.
        # But Scaler uses Builder.load_string inside __init__.
        # This might fail if app is not running loop, but let's try.
        assert s.container is not None

    def test_add_remove_widget(self):
        s = Scaler()
        w = Widget()
        s.add_widget(w)
        # Should be added to s.container
        assert w in s.container.children

        s.remove_widget(w)
        assert w not in s.container.children

    def test_process_to_local(self):
        s = Scaler()
        s.scale = 2.0

        # Should divide by scale
        x, y = s.process_to_local(100, 50)
        assert x == 50.0
        assert y == 25.0

        x, y = s.process_to_local(None, None)
        assert x is None

    def test_process_events(self):
        s = Scaler()
        s.scale = 2.0

        # Mock MotionEvent
        event = MagicMock()
        event.sx = 100
        event.sy = 50
        event.osx = 100
        event.osy = 50
        event.psx = 0
        event.psy = 0

        # type, event
        events = [("begin", event)]

        # Should modify event in place
        s.process(events)

        # 100 / 2 = 50
        assert event.sx == 50.0
        assert event.sy == 25.0

        # osx/osy transformed on begin
        assert event.osx == 50.0
