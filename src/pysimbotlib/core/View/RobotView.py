from kivy.properties import NumericProperty, ObjectProperty, ReferenceListProperty
from kivy.uix.widget import Widget


class RobotView(Widget):
    model = ObjectProperty(None)
    direction = NumericProperty(0)

    def __init__(self, model, **kwargs):
        self.model = model
        super().__init__(**kwargs)
        # Bind view properties to model properties
        if self.model:
            self.model.bind(pos=self.on_model_pos)
            self.model.bind(size=self.on_model_size)
            self.model.bind(color=self.on_model_color)
            self.model.bind(_direction=self.on_model_direction)

            # Initial sync
            self.pos = self.model.pos
            self.size = self.model.size
            self.direction = self.model._direction

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
