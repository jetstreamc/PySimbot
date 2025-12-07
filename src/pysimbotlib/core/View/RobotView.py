import math

from kivy.clock import Clock
from kivy.graphics import Color, InstructionGroup, Line
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty, ReferenceListProperty
from kivy.uix.widget import Widget


class RobotView(Widget):
    model = ObjectProperty(None)
    direction = NumericProperty(0)
    draw_rays = BooleanProperty(False)

    def __init__(self, model, draw_rays=False, **kwargs):
        self.model = model
        self.draw_rays = draw_rays
        super().__init__(**kwargs)
        self.ray_instructions = InstructionGroup()

        # Bind view properties to model properties
        if self.model:
            self.model.bind(pos=self.on_model_pos)
            self.model.bind(size=self.on_model_size)
            self.model.bind(color=self.on_model_color)
            self.model.bind(_direction=self.on_model_direction)

            # Intial sync
            self.pos = self.model.pos
            self.size = self.model.size
            self.direction = self.model._direction

        self.bind(draw_rays=self.on_draw_rays)
        if self.draw_rays:
            Clock.schedule_interval(self.update_rays, 1.0 / 60.0)
            self.canvas.add(self.ray_instructions)

        # Color handling might need specific property in view or direct canvas access
        # But for KV compatibility, we usually expose a 'color' property on the View

    # Proxy properties for KV
    # KV accesses 'self.color' (rgba)
    _color_r = NumericProperty(0)
    _color_g = NumericProperty(0)
    _color_b = NumericProperty(0)
    _color_a = NumericProperty(0)
    color = ReferenceListProperty(_color_r, _color_g, _color_b, _color_a)

    def on_model_pos(self, instance, value):
        self.pos = value

    def on_model_size(self, instance, value):
        self.size = value

    def on_model_direction(self, instance, value):
        self.direction = value

    def on_model_color(self, instance, value):
        self.color = value

    def on_draw_rays(self, instance, value):
        if value:
            Clock.schedule_interval(self.update_rays, 1.0 / 60.0)
            self.canvas.add(self.ray_instructions)
        else:
            Clock.unschedule(self.update_rays)
            self.canvas.remove(self.ray_instructions)
            self.ray_instructions.clear()

    def update_rays(self, dt):
        if not self.model or not self.draw_rays:
            return

        self.ray_instructions.clear()

        # Get sensor data
        distances = self.model.distance()  # Tuple of distances

        # Assume angles are known constant from Global
        from ..Utils.Global import ROBOT_DISTANCE_ANGLES

        self.ray_instructions.add(Color(0, 0, 1, 1))  # Blue for high contrast

        center_x, center_y = self.center

        for i, angle_offset in enumerate(ROBOT_DISTANCE_ANGLES):
            dist = distances[i]

            # Calculate ray end point
            # Robot direction is in degrees, counter-clockwise?
            # Model uses: rad_angle = math.radians(-(self._direction + angle))

            # Use same logic as model to match
            # direction is property here

            # Canvas is already rotated by self.direction (in canvas.before)
            # So we only need to account for the sensor offset angle.
            # Model uses '-(direction + offset)'
            # Here we use '-(offset)' because direction rotation is handled by context.

            rad_angle = math.radians(-angle_offset)
            unit_x = math.cos(rad_angle)
            unit_y = math.sin(rad_angle)

            # Start from the robot's edge (border)
            # The sensor is located at the edge of the robot (width/2)
            radius = self.width / 2.0

            start_x = center_x + radius * unit_x
            start_y = center_y + radius * unit_y

            # The distance returned is from the sensor (edge) to the obstacle
            end_x = start_x + dist * unit_x
            end_y = start_y + dist * unit_y

            # Draw
            # If dist is max, maybe draw different color or transparency?
            # For now just draw the line

            self.ray_instructions.add(Line(points=[start_x, start_y, end_x, end_y], width=1))
