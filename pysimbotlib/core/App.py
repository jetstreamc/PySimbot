from kivy.config import Config
Config.set('graphics', 'resizable', '0') #0 being off 1 being on as in true/false
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

import os
import platform
from kivy.app import App
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.metrics import Metrics

from .Simbot import Simbot, PySimbotMap
from .Scaler import Scaler
from .Robot import Robot

from .Global import ROBOT_DEFAULT_START_POS, OBJECTIVE_DEFAULT_START_POS

class PySimbotApp(App):

    title = 'PySimbot'

    def __init__(self,
                robot_cls = Robot,
                num_robots = 1,
                num_objectives = 1,
                robot_default_start_pos = ROBOT_DEFAULT_START_POS,
                obj_default_start_pos = OBJECTIVE_DEFAULT_START_POS,
                interval = 1.0/60.0,
                max_tick = 4000,
                map = 'default',
                theme = 'default',
                customfn_create_robots = None,
                customfn_before_simulation = None,
                customfn_after_simulation = None,
                enable_wasd_control = False,
                simulation_forever = False,
                food_move_after_eat = True,
                save_wasd_history = False,
                robot_see_each_other = False,
                **kwargs):

        super(PySimbotApp, self).__init__(**kwargs)
        self.interval = interval
        Window.size = (900, 600)

        map_file_name = "pysimbotlib/maps/%s.kv" % map
        theme_file_name = "pysimbotlib/themes/%s.kv" % theme
        if not os.path.exists(map_file_name):
            raise FileNotFoundError("File [%s] is not found." % map_file_name)
        if not os.path.exists(theme_file_name):
            raise FileNotFoundError("File [%s] is not found." % theme_file_name)
        
        Builder.load_file(map_file_name)
        Builder.load_file(theme_file_name)

        self.simbot = Simbot(max_tick=max_tick,
                            robot_cls = robot_cls,
                            num_robots = num_robots,
                            num_objectives = num_objectives,
                            robot_default_start_pos = robot_default_start_pos,
                            obj_default_start_pos = obj_default_start_pos,
                            customfn_create_robots = customfn_create_robots,
                            customfn_before_simulation = customfn_before_simulation,
                            customfn_after_simulation = customfn_after_simulation,
                            simulation_forever = simulation_forever,
                            food_move_after_eat = food_move_after_eat,
                            save_wasd_history = save_wasd_history,
                            robot_see_each_other = robot_see_each_other)

        self.simbotMap = PySimbotMap(self.simbot,
                            enable_wasd_control = enable_wasd_control,
                            save_wasd_history = save_wasd_history)

        self.simbot.add_widget(self.simbotMap, index=1)

    def build(self):
        if platform.system() == 'Darwin':
            self._scaler = Scaler(size=Window.size, scale=2)
            Window.add_widget(self._scaler)
            parent = self._scaler or Window
            parent.add_widget(self.simbot)
        else:
            Window.add_widget(self.simbot)
        Clock.schedule_interval(self.simbot.process, self.interval)