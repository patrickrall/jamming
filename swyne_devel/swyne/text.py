
from .node import *
import pyglet
from .layout import *
from .focus import *

class LabelNode(AbstractNode):
    def __init__(self):
        super().__init__()
        self.document = pyglet.text.decode_attributed("Hello world!")
        self.document.set_style(0, len(self.document.text), {'color': (255,255,255,255) })
        self.layout = pyglet.text.layout.TextLayout(self.document, multiline=True, wrap_lines=False)

    def draw(self):
        self.layout.draw()
        default_draw(self)

    def serialize(self):
        data = {"text": self.document.text, "styles": {}}
        for key in self.document._style_runs:
            data["styles"][key] = list(self.document._style_runs[key])
        return data

    def deserialize(self,data):
        if isinstance(data,str):
            self.document = pyglet.text.decode_attributed(data)
            self.layout.document = self.document
        else:
            print(data)
            self.document.text = data["text"]
            self.document._style_runs = {}
            for attr,runs in data["styles"].items():
                for start,stop,value in runs:
                    if isinstance(value,list): value = tuple(value)
                    self.document._set_style(start,stop,{attr: value})

    def set_layout(self,pos,dims):
        default_set_layout(self,pos,dims)
        self.layout.begin_update()
        self.layout.x = pos.x
        self.layout.y = pos.y
        self.layout.end_update()

    def layout_hints(self):
       return default_layout_hints(self,
                Vector2(self.layout.content_width,self.layout.content_height),
                Vector2(self.layout.content_width,self.layout.content_height))

@focusable_node
class TextBoxNode(AbstractNode):

    def __init__(self):
        super().__init__()

        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)

        white = (255,255,255,255)
        black = (0,0,0,255)
        blue = (100,100,160,255)
        min_width = 150

        self.document = pyglet.text.document.UnformattedDocument()
        self.document.text = "Label"

        font = self.document.get_font(0)
        h = font.ascent-font.descent
        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document,
                min_width, h, multiline=False)

        self.document.set_style(0, len(self.document.text), {"color": white})
        self.document.set_style(0, len(self.document.text), {"background_color": black})
        self.caret = pyglet.text.caret.Caret(self.layout, color=(255,255,255))

        self.layout.selection_background_color = blue

        self.caret.visible = False

    def serialize(self):
        return self.document.text

    def deserialize(self,data):
        self.document.text = data

    def set_layout(self,pos,dims):
        self.pos, self.dims = pos,dims

        default_set_layout(self,pos,dims)

        self.layout.begin_update()
        self.layout.x = pos.x
        self.layout.y = pos.y
        self.layout.width = dims.x
        self.layout.end_update()

        if not self.caret.visible:
            self.layout.set_selection(0,0)

    def layout_hints(self):
        min_width = 150
        font = self.document.get_font(0)
        h = font.ascent-font.descent

        return default_layout_hints(self,
                Vector2(min_width,h),
                Vector2(float('inf'),h))

    def draw(self):
        self.layout.draw()
        default_draw(self)

    ########################################################

    @focus_event
    def on_focus(self):
        self.caret.visible = True
        gray = (100,100,100,255)
        self.document.set_style(0, len(self.document.text), {"background_color": gray})
        self.layout.set_selection(0,0)
        self.window.redraw()

    @focus_event
    def on_blur(self):
        self.caret.visible = False
        black = (0,0,0,255)
        self.document.set_style(0, len(self.document.text), {"background_color": black})
        self.layout.set_selection(0,0)
        self.window.redraw()

    @focus_event
    def on_text(self,text):
        self.caret.on_text(text)
        self.window.redraw()

    @focus_event
    def on_text_motion(self,motion,select=False):
        self.caret.on_text_motion(motion,select=select)
        self.window.redraw()

    @focus_event
    def on_text_motion_select(self, motion):
        self.caret.on_text_motion_select(motion)
        self.window.redraw()

    @focus_event
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pos,dims = self.pos,self.dims
        if (x > pos.x and x <= pos.x + dims.x\
                and y > pos.y and y <= pos.y + dims.y):
            self.caret.on_text_motion_select(x, y, scroll_x, scroll_y)
            self.window.redraw()

    @focus_event
    def on_mouse_press(self, x, y, button, modifiers):
        pos,dims = self.pos,self.dims
        if (x > pos.x and x <= pos.x + dims.x\
                and y > pos.y and y <= pos.y + dims.y):
            self.caret.on_mouse_press(x, y, button, modifiers)
            self.window.redraw()

    @focus_event
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pos,dims = self.pos,self.dims
        if (x > pos.x and x <= pos.x + dims.x\
                and y > pos.y and y <= pos.y + dims.y):
            self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
            self.window.redraw()

    @focus_event
    def on_activate(self):
        self.caret.on_activate()
        self.window.redraw()

    @focus_event
    def on_deactivate(self):
        self.caret.on_deactivate()
        self.window.redraw()

def bordered_text_box(text="Label"):
    nodes = """
    PaddingLayoutNode {"top": 10, "left": 10, "bottom": 10, "right": 10}
    -BackgroundNode [255, 255, 255, 255]
    --PaddingLayoutNode {"top": 1, "left": 1, "bottom": 1, "right": 1}
    ---BackgroundNode [0, 0, 0, 255]
    ----PaddingLayoutNode {"top": 3, "left": 3, "bottom": 3, "right": 3}
    -----box TextBoxNode
    """
    node, keys = deserialize_node(nodes)
    keys["box"].document.text = text
    return node, keys["box"]
