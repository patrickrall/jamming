

from .node import *
from pyglet.window import key
from .text import bordered_text_box
from .layout import *
import os

# call these from an @listener function
# using yield from

# Alert dialog
# Confirm dialog
# Prompt dialog
# Filepicker dialog


def alert_dialog(window, text):

    node, keys = deserialize_node("""
    BackgroundNode [0,0,0,100]
    -PaddingLayoutNode "*"
    --PaddingLayoutNode 10
    ---BackgroundNode [255,255,255,255]
    ----PaddingLayoutNode 1
    -----BackgroundNode [0,0,0,255]
    ------RowsLayoutNode
    -------PaddingLayoutNode 5
    --------label LabelNode "{color (255,255,255,255)} placeholder"
    -------PaddingLayoutNode [0,"*",5,"*"]
    --------okbutton BackgroundNode [255,255,255,255]
    ---------LabelNode "Ok"
    """)

    keys["label"].document.text = text
    window._basenode.add_child(node)
    window.redraw()

    ok = keys["okbutton"]

    while True:
        event, *args = yield ['on_mouse_press', 'on_key_press']

        if event == "on_mouse_press":
            x,y,buttons,modifiers = args

            if (x > ok.pos.x and x <= ok.pos.x + ok.dims.x\
                    and y > ok.pos.y and y <= ok.pos.y + ok.dims.y):
                window._basenode.splice(len(window._basenode.children)-1,1)
                window.redraw()
                return

        if event == "on_key_press":
            symbol, modifiers = args
            if symbol == key.ENTER or symbol == key.ESCAPE:
                # eat the '\n' text
                if symbol == key.ENTER: yield "on_text"

                window._basenode.splice(len(window._basenode.children)-1,1)
                window.redraw()
                return


def confirm_dialog(window, text):

    node, keys = deserialize_node("""
    BackgroundNode [0,0,0,100]
    -PaddingLayoutNode "*"
    --PaddingLayoutNode 10
    ---BackgroundNode [255,255,255,255]
    ----PaddingLayoutNode 1
    -----BackgroundNode [0,0,0,255]
    ------ForceMinLayoutNode "X"
    -------RowsLayoutNode
    --------PaddingLayoutNode [5,"*",5,"*"]
    ---------PaddingLayoutNode [0,5,0,5]
    ----------label LabelNode "{color (255,255,255,255)} placeholder"
    --------PaddingLayoutNode [0,"*",5,"*"]
    ---------ColsLayoutNode
    ----------HintedLayoutNode [5,0]
    ----------yesbutton BackgroundNode [255,255,255,255]
    -----------LabelNode "Yes"
    ----------HintedLayoutNode [10,0]
    ----------nobutton BackgroundNode [255,255,255,255]
    -----------LabelNode "No"
    ----------HintedLayoutNode [5,0]
    """)

    keys["label"].document.text = text
    yes = keys["yesbutton"]
    no = keys["nobutton"]
    window._basenode.add_child(node)
    window.redraw()

    def close(out):
        window._basenode.splice(len(window._basenode.children)-1,1)
        window.redraw()
        return out

    while True:
        event, *args = yield ['on_mouse_press', 'on_key_press']

        if event == "on_mouse_press":
            x,y,buttons,modifiers = args

            if (x > yes.pos.x and x <= yes.pos.x + yes.dims.x\
                and y > yes.pos.y and y <= yes.pos.y + yes.dims.y):
                    return close(True)

            if (x > no.pos.x and x <= no.pos.x + no.dims.x\
                and y > no.pos.y and y <= no.pos.y + no.dims.y):
                    return close(False)

        if event == "on_key_press":
            symbol, modifiers = args
            if symbol == key.ENTER:
                # eat the '\n' text
                if symbol == key.ENTER: yield "on_text"

                return close(True)
            if symbol == key.ESCAPE: return close(False)


# has focus by default, events are routed by dialog function
class PromptTextBoxNode(AbstractNode):
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
        self.caret.visible = True

    def set_layout(self,pos,dims):
        self.pos, self.dims = pos,dims
        default_set_layout(self,pos,dims)
        self.layout.begin_update()
        self.layout.x = pos.x
        self.layout.y = pos.y
        self.layout.width = dims.x
        self.layout.end_update()

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


def prompt_dialog(window, label_text, prompt_text):

    node, keys = deserialize_node("""
    BackgroundNode [0,0,0,100]
    -PaddingLayoutNode "*"
    --PaddingLayoutNode 10
    ---BackgroundNode [255,255,255,255]
    ----PaddingLayoutNode 1
    -----BackgroundNode [0,0,0,255]
    ------ForceMinLayoutNode "X"
    -------RowsLayoutNode
    --------PaddingLayoutNode [5,"*",0,"*"]
    ---------PaddingLayoutNode [0,5,0,5]
    ----------label LabelNode "{color (255,255,255,255)} placeholder"
    --------PaddingLayoutNode [0,"*",0,"*"]
    ---------PaddingLayoutNode {"top": 10, "left": 10, "bottom": 10, "right": 10}
    ----------BackgroundNode [255, 255, 255, 255]
    -----------PaddingLayoutNode {"top": 1, "left": 1, "bottom": 1, "right": 1}
    ------------BackgroundNode [0, 0, 0, 255]
    -------------PaddingLayoutNode {"top": 3, "left": 3, "bottom": 3, "right": 3}
    --------------box PromptTextBoxNode
    """)

    keys["label"].document.text = label_text

    box = keys["box"]
    box.document.text = prompt_text
    box.caret.position = len(box.document.text)

    window._basenode.add_child(node)
    box.layout.view_x = 0
    window.redraw()

    def hit(args):
        x,y = args[0], args[1]
        pos,dims = box.pos,box.dims
        return (x > pos.x and x <= pos.x + dims.x\
                and y > pos.y and y <= pos.y + dims.y)

    while True:
        event, *args = yield
        if event == "on_mouse_motion": continue

        if event == "on_text_motion": box.caret.on_text_motion(*args)
        if event == "on_text_motion_select": box.caret.on_text_motion_select(*args)

        if event == "on_mouse_scroll" and hit(args): box.caret.on_mouse_scroll(*args)
        if event == "on_mouse_press" and hit(args): box.caret.on_mouse_press(*args)
        if event == "on_mouse_drag" and hit(args): box.caret.on_mouse_drag(*args)

        if event == "on_activate": box.caret.on_activate(*args)
        if event == "on_deactivate": box.caret.on_deactivate(*args)

        if event == "on_text":
            text = args[0]
            if text == "\r":
                window._basenode.splice(len(window._basenode.children)-1,1)
                window.redraw()
                return box.document.text
            else:
                box.caret.on_text(*args)

        if event == "on_key_press":
            symbol, modifiers = args
            if symbol == key.ESCAPE:
                window._basenode.splice(len(window._basenode.children)-1,1)
                window.redraw()
                return None

        window.redraw()


def file_dialog(window, label_text, initial_path=os.getcwd()):

    node, keys = deserialize_node("""
    BackgroundNode [0,0,0,100]
    -PaddingLayoutNode "*"
    --PaddingLayoutNode 10
    ---BackgroundNode [255,255,255,255]
    ----PaddingLayoutNode 1
    -----BackgroundNode [0,0,0,255]
    ------ForceMinLayoutNode "X"
    -------RowsLayoutNode
    --------PaddingLayoutNode [5,"*",0,"*"]
    ---------PaddingLayoutNode [0,5,0,5]
    ----------label LabelNode "{color (255,255,255,255)} placeholder"
    --------PaddingLayoutNode [0,"*",0,"*"]
    ---------PaddingLayoutNode {"top": 10, "left": 10, "bottom": 10, "right": 10}
    ----------BackgroundNode [255, 255, 255, 255]
    -----------PaddingLayoutNode {"top": 1, "left": 1, "bottom": 1, "right": 1}
    ------------BackgroundNode [0, 0, 0, 255]
    -------------PaddingLayoutNode {"top": 3, "left": 3, "bottom": 3, "right": 3}
    --------------box PromptTextBoxNode
    --------HintedLayoutNode [500,500,"*",100]
    ---------suggestions BlocksLayoutNode
    """)

    keys["label"].document.text = label_text

    box = keys["box"]
    box.document.text = initial_path
    box.caret.position = len(box.document.text)

    suggnode = keys["suggestions"]
    sugglist = None # list of full paths of suggestions (node only displays basenames)
    suggsource = None # the text that yielded the current list of suggestions

    window._basenode.add_child(node)
    box.layout.view_x = 0
    window.redraw()

    def hit(args,targ):
        x,y = args[0], args[1]
        pos,dims = targ.pos,targ.dims
        return (x > pos.x and x <= pos.x + dims.x\
                and y > pos.y and y <= pos.y + dims.y)

    while True:
        event, *args = yield
        if event == "on_mouse_motion": continue

        if event == "on_text_motion": box.caret.on_text_motion(*args)
        if event == "on_text_motion_select": box.caret.on_text_motion_select(*args)

        if event == "on_mouse_drag" and hit(args,box): box.caret.on_mouse_drag(*args)
        if event == "on_mouse_press":
            if hit(args,box): box.caret.on_mouse_press(*args)
            if hit(args,suggnode):
                x,y = args[0], args[1]

                t = suggnode.translate.y
                found_child = None

                for child in suggnode.children:
                    if (x > child.pos.x and x <= child.pos.x + child.dims.x\
                            and y > child.pos.y+t and y <= child.pos.y+t + child.dims.y):
                        text = child.children[0].children[0].document.text
                        subs = [x for x in sugglist if x.endswith(text)][0]
                        box.document.text = subs

                        found_child = child

                        child.color = [100,100,100,255]

                        if child.pos.y + suggnode.translate.y < suggnode.pos.y:
                            suggnode.translate.y = suggnode.pos.y - child.pos.y

                        if child.pos.y + child.dims.y + suggnode.translate.y\
                                - (suggnode.pos.y + suggnode.dims.y) > 0:
                            suggnode.translate.y = (suggnode.pos.y + suggnode.dims.y)\
                                    - (child.pos.y + child.dims.y)

                if found_child is not None:
                    for child in suggnode.children:
                        if child == found_child: continue
                        child.color = [0,0,0,255]

        if event == "on_mouse_scroll":
            if hit(args,box): box.caret.on_mouse_scroll(*args)
            if hit(args,suggnode):
                scroll_y = args[3]
                suggestions.translate.y -= scroll_y*3

                if suggestions.translate.y < 0: suggestions.translate.y = 0
                if suggestions.translate.y > suggestions.max_translate.y:
                    suggestions.translate.y = suggestions.max_translate.y

        if event == "on_activate": box.caret.on_activate(*args)
        if event == "on_deactivate": box.caret.on_deactivate(*args)

        if event == "on_text":
            text = args[0]
            if text == "\r":
                window._basenode.splice(len(window._basenode.children)-1,1)
                window.redraw()
                return box.document.text
            else:
                box.caret.on_text(*args)

        if event == "on_key_press":
            symbol, modifiers = args
            if symbol == key.ESCAPE:
                window._basenode.splice(len(window._basenode.children)-1,1)
                window.redraw()
                return None

            if symbol == key.TAB:
                text = box.document.text

                def file_node(t):
                    node, keys = deserialize_node("""
                    BackgroundNode [0,0,0,10]
                    -PaddingLayoutNode 5
                    --label LabelNode "{color (255,255,255,255)}{font_size 10} placeholder"
                    """)
                    keys["label"].document.text = t
                    return node,keys

                # clear suggestions if user has typed something
                if sugglist is not None:
                    if text != suggsource and \
                            text not in sugglist:
                        sugglist = None

                if sugglist is None:

                    # populate sugglist
                    if os.path.isdir(text) and text[-1] != ".":
                        sugglist = [os.path.join(text,f) for f in os.listdir(text) if \
                                    f[0] != "."]
                    else:
                        dirname = os.path.dirname(text)
                        if os.path.exists(dirname):
                            sugglist = [os.path.join(dirname,f) for f in os.listdir(dirname) if \
                                        text in os.path.join(dirname,f)]
                        else:
                            sugglist = []

                    # update suggs node
                    suggnode.splice(0,len(suggnode.children))
                    for x in sugglist:
                        node, keys = file_node(os.path.basename(x))
                        suggnode.add_child(node)

                    # display error message
                    if len(sugglist) == 0:
                        if os.path.isdir(text):
                            node, _ = file_node("Directory empty (except hidden files?).")
                        else:
                            node, _ = file_node("No matches found.")
                        suggnode.add_child(node)

                    suggsource = text
                    rebuild_layout(window)

                else:

                    if text == suggsource:
                        # just generated this list, so complete textbox with first element
                        box.document.text = sugglist[0]
                        box.caret.position = len(box.document.text)

                    else:
                        # complete next item in sugglist
                        idx = sugglist.index(text)
                        if idx == len(sugglist) - 1: idx = 0
                        else: idx += 1
                        box.document.text = sugglist[idx]
                        box.caret.position = len(box.document.text)

                    for child in suggnode.children:
                        if child.children[0].children[0].document.text\
                                == os.path.basename(box.document.text):
                            child.color = [100,100,100,255]

                            if child.pos.y + suggnode.translate.y < suggnode.pos.y:
                                suggnode.translate.y = suggnode.pos.y - child.pos.y

                            if child.pos.y + child.dims.y + suggnode.translate.y\
                                    - (suggnode.pos.y + suggnode.dims.y) > 0:
                                suggnode.translate.y = (suggnode.pos.y + suggnode.dims.y)\
                                        - (child.pos.y + child.dims.y)
                        else:
                            child.color = [0,0,0,255]

        window.redraw()

