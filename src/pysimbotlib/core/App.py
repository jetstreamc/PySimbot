import platform
from pathlib import Path

from kivy.config import Config

Config.set("graphics", "resizable", "0")  # 0 being off 1 being on as in true/false
Config.set("input", "mouse", "mouse,multitouch_on_demand")

# ruff: noqa: E402
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder

from .model.robot import Robot
from .utils.globals import OBJECTIVE_DEFAULT_START_POS, ROBOT_DEFAULT_START_POS
from .utils.scaler import Scaler
from .view.simbot import PySimbotMap, Simbot


class PySimbotApp(App):
    title = "PySimbot"

    def __init__(
        self,
        robot_cls=Robot,
        num_robots=1,
        num_objectives=1,
        robot_default_start_pos=ROBOT_DEFAULT_START_POS,
        obj_default_start_pos=OBJECTIVE_DEFAULT_START_POS,
        interval=1.0 / 60.0,
        max_tick=4000,
        map="default",
        theme="default",
        customfn_create_robots=None,
        customfn_before_simulation=None,
        customfn_after_simulation=None,
        enable_wasd_control=False,
        simulation_forever=False,
        food_move_after_eat=True,
        save_wasd_history=False,
        robot_see_each_other=False,
        draw_rays=False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.interval = interval
        Window.size = (900, 600)

        # pysimbotlib/core/App.py -> pysimbotlib/
        package_root = Path(__file__).parent.parent
        map_file = package_root / "maps" / f"{map}.kv"
        theme_file = package_root / "themes" / f"{theme}.kv"
        if not map_file.exists():
            raise FileNotFoundError(f"File [{map_file}] is not found.")
        if not theme_file.exists():
            raise FileNotFoundError(f"File [{theme_file}] is not found.")

        Builder.load_file(str(map_file))
        Builder.load_file(str(theme_file))

        self.simbot = Simbot(
            max_tick=max_tick,
            robot_cls=robot_cls,
            num_robots=num_robots,
            num_objectives=num_objectives,
            robot_default_start_pos=robot_default_start_pos,
            obj_default_start_pos=obj_default_start_pos,
            customfn_create_robots=customfn_create_robots,
            customfn_before_simulation=customfn_before_simulation,
            customfn_after_simulation=customfn_after_simulation,
            simulation_forever=simulation_forever,
            food_move_after_eat=food_move_after_eat,
            save_wasd_history=save_wasd_history,
            robot_see_each_other=robot_see_each_other,
            draw_rays=draw_rays,
        )

        self.simbotMap = PySimbotMap(
            self.simbot, enable_wasd_control=enable_wasd_control, save_wasd_history=save_wasd_history
        )

        self.simbot.add_widget(self.simbotMap, index=1)

    def build(self):
        root_widget = self.simbot
        if platform.system() == "Darwin":
            self._scaler = Scaler(size=Window.size, scale=2)
            self._scaler.add_widget(self.simbot)
            root_widget = self._scaler

        Window.add_widget(root_widget)
        Clock.schedule_interval(self.simbot.process, self.interval)
