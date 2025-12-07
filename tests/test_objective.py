from pysimbotlib.core.Objective import Objective


def test_objective_initialization():
    # Test default initialization
    o = Objective()
    assert o.size == [20, 20]
    assert o.size_hint == [None, None]


def test_objective_custom_initialization():
    # Test custom initialization
    o = Objective(size=(30, 30), pos=(10, 10))
    assert o.size == [30, 30]
    assert o.pos == [10, 10]
