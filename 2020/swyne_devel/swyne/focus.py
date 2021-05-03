from functools import wraps, partial
from .node import *


@listener
def route_focus_events(window, enabled=lambda : True):
    while True:
        event_name, *args = yield
        if not enabled(): continue
        for child in window.node.children_with_attr("focus"):
            if child.focus and hasattr(child, event_name):
                getattr(child, event_name)(*args)

@listener
def mouse_focus_via_pos_dims(window, enabled=lambda : True):
    while True:
        _,x,y,button,modifiers = yield "on_mouse_press"
        if not enabled(): continue
        any_clicked = False
        for child in window.node.children_with_attr("focus"):
            if not hasattr(child,"pos"): continue
            if not hasattr(child,"dims"): continue
            pos,dims = child.pos,child.dims
            if (x > pos.x and x <= pos.x + dims.x\
                    and y > pos.y and y <= pos.y + dims.y):

                child.focus = True
                if hasattr(child, "on_mouse_press"):
                    child.on_mouse_press(x,y,button,modifiers)

                any_clicked = True
                break

        if not any_clicked: blur_all(window)



def blur_all(window):
    for child in window.node.children_with_attr("focus"):
        child.focus = False



###############################

def focusable_node(cls):

    class Wrapped(cls):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self._has_focus = False
            self._focus_event_overrides = {}

        @property
        def focus(self):
            return self._has_focus

        @focus.setter
        def focus(self,value):
            if (self._has_focus == value): return
            self._has_focus = value

            # blur everything else
            if value:
                for child in self.window.node.children_with_attr("focus"):
                    if child != self:
                        child.focus = False

            if value and hasattr(self,"on_focus"):
                self.on_focus()

            if not value and hasattr(self,"on_blur"):
                self.on_blur()

        def override_focus_event(self, func):
            if func.__name__ not in self._focus_event_overrides:
                self._focus_event_overrides[func.__name__] = []
            self._focus_event_overrides[func.__name__].append(func)

    Wrapped.__name__ = cls.__name__
    cls.__name__ += "_unwrapped"

    return Wrapped



# decorator for focus events
def focus_event(func):

    name = func.__name__

    @wraps(func)
    def wrapped(self, *args, **kwargs):
        if name not in self._focus_event_overrides:
            return func(self,*args,**kwargs)

        overrides = self._focus_event_overrides[name]

        if len(overrides) == 0:
            return func(self,*args, **kwargs)
        else:
            def default(i, *next_args, **next_kwargs):
                if i < 0:
                    return func(self,*next_args,**next_kwargs)
                else:
                    return overrides[i](partial(default, i-1), *args)

            overrides[-1](partial(default, len(overrides)-2), *args)

    return wrapped


"""
##################### DEMO

@focusable_node
class FocusTestNode(AbstractNode):
    def __init__(self):
        super().__init__()
        self.color = [255,255,255,100]
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)

    def draw(self):
        glColor4f( self.color[0]/255, self.color[1]/255, self.color[2]/255, self.color[3]/255)
        glRectf(self.pos.x,self.pos.y,self.pos.x+self.dims.x,self.pos.y+self.dims.y)

        default_draw(self)

    def set_layout(self,pos,dims):
        default_set_layout(self,pos,dims)
        self.pos = pos
        self.dims = dims

    def layout_hints(self):
        return Vector2(100,100), Vector2(100,100)

    @focus_event
    def on_focus(self):
        self.color[3] = 255
        self.window.redraw()

    @focus_event
    def on_blur(self):
        self.color[3] = 100
        self.window.redraw()

    @focus_event
    def on_text(self, text):
        import random
        self.color[0] = random.randint(200,255)
        self.color[1] = random.randint(200,255)
        self.color[2] = random.randint(200,255)
        self.window.redraw()

import traceback

class FocusTestWindow(NodeWindow):

    def __init__(self):
        super().__init__(resizable=True)

        self.node, keys = deserialize_node('''
        BackgroundNode [255,0,0,255]
        -RowsLayoutNode
        --PaddingLayoutNode 5
        ---BackgroundNode [0,255,0,100]
        --PaddingLayoutNode 5
        ---FocusTestNode
        --PaddingLayoutNode 5
        ---special FocusTestNode
        ''')

        route_focus_events(self)
        mouse_focus_via_pos_dims(self)

        special = keys["special"]

        @special.override_focus_event
        def on_text(default,text):
            default(text)

"""
