from pysimbotlib.core.App import PySimbotApp
from pysimbotlib.core.Model.Robot import Robot

if __name__ == "__main__":
    app = PySimbotApp(
        robot_cls=Robot,
        num_robots=1,
        num_objectives=3,
        draw_rays=True,  # Enable ray drawing
        simulation_forever=True,
    )
    app.run()
