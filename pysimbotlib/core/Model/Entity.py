from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, ReferenceListProperty


class Entity(EventDispatcher):
    x = NumericProperty(0)
    y = NumericProperty(0)
    pos = ReferenceListProperty(x, y)

    width = NumericProperty(100)
    height = NumericProperty(100)
    size = ReferenceListProperty(width, height)

    # Logic-only center property (calculated, not stored)
    @property
    def center(self):
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)

    @property
    def center_x(self):
        return self.x + self.width / 2.0

    @property
    def center_y(self):
        return self.y + self.height / 2.0
