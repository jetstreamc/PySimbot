import gc
import weakref

from pysimbotlib.core.Robot import Robot


# Mock Simbot and Obstacle for Robot initialization
class MockObstacle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h


class MockSimbot:
    obstacles = [MockObstacle(0, 0, 10, 10)]


def test_leak():
    print("Testing for memory leak...")

    # Create a robot instance
    # Robot.__init__ expects kwargs, but checks _sm internally for some things?
    # Looking at Robot.py, __init__ calls super().__init__.
    # _sm is a class attribute in Robot but usually assigned to the instance or class in the app.
    # The method triggering cache is get_obstacles_bboxes which uses self._sm.

    # We need to ensure self._sm is set for the instance if we want to call the method.
    # The original class has _sm = None.

    r = Robot()
    r._sm = MockSimbot()

    # Create a weak reference to the robot
    r_ref = weakref.ref(r)

    # Call the cached method
    _ = r.get_obstacles_bboxes()

    # Delete the strong reference
    del r

    # Force garbage collection
    gc.collect()

    # Check if the object is still alive
    if r_ref() is None:
        print("PASS: Robot instance was garbage collected.")
    else:
        print("FAIL: Robot instance was NOT garbage collected (Memory Leak detected).")


if __name__ == "__main__":
    test_leak()
