from pysimbotlib.core.model.simulation_model import SimulationModel


def test_model_initialization():
    sm = SimulationModel()
    assert sm.robots == []
    assert sm.obstacles == []
    assert sm.objectives == []
    assert sm.score == 0
    assert sm.iteration == 0


def test_model_add_entities():
    sm = SimulationModel()

    # Mock entities
    r = "Robot"
    o = "Obstacle"
    obj = "Objective"

    sm.add_robot(r)
    assert len(sm.robots) == 1
    assert sm.robots[0] == r

    sm.add_obstacle(o)
    assert len(sm.obstacles) == 1

    sm.add_objective(obj)
    assert len(sm.objectives) == 1


def test_model_iteration():
    sm = SimulationModel()
    sm.increment_iteration()
    assert sm.iteration == 1

    sm.reset_iteration()
    assert sm.iteration == 0
