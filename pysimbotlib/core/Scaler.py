#!python
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.base import EventLoop
from kivy.lang import Builder

class Scaler(Widget):
    scale = NumericProperty(2)
    container = ObjectProperty(None)

    def __init__(self, **kwargs):
        from kivy.base import EventLoop
        from kivy.lang import Builder
        Builder.load_string('''
<Scaler>:
    container: container
    canvas.before:
        PushMatrix
        Scale:
            x: root.scale
            y: root.scale
            z: 1

    canvas.after:
        PopMatrix

    FloatLayout:
        id: container
        size: root.width / root.scale, root.height / root.scale
''')

        super(Scaler, self).__init__(**kwargs)
        EventLoop.add_postproc_module(self)

    def get_parent_window(self):
        return self.container

    def add_widget(self, widget):
        if self.container is not None:
            return self.container.add_widget(widget)
        return super(Scaler, self).add_widget(widget)

    def remove_widget(self, widget):
        if self.container is not None:
            return self.container.remove_widget(widget)
        return super(Scaler, self).remove_widget(widget)

    def process_to_local(self, x, y, relative=False):
        if x is None:
            return None, None
        s = float(self.scale)
        return x / s, y / s

    def process(self, events):
        transform = self.process_to_local
        transformed = []
        for etype, event in events:

            # you might have a move and up event in the same process
            # then avoid the double-transformation
            if event in transformed:
                continue
            transformed.append(event)

            event.sx, event.sy = transform(event.sx, event.sy)
            if etype == 'begin':
                event.osx, event.osy = transform(event.osx, event.osy)
            else:
                # update the delta
                event.dsx = event.sx - event.psx
                event.dsy = event.sy - event.psy

        return events


