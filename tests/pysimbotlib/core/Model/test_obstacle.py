from pysimbotlib.core.model.obstacle import Obstacle


def test_obstacle_initialization():
    obs = Obstacle()
    # Kivy widgets default to (100, 100) if not specified,
    # but let's just check it instantiates correctly
    assert isinstance(obs, Obstacle)


def test_obstacle_properties():
    obs = Obstacle(pos=(50, 50), size=(100, 20))
    assert obs.pos == [50, 50]
    assert obs.size == [100, 20]
