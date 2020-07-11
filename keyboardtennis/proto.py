
import json
from swyne.node import NodeWindow,Vector2,deserialize_node
from swyne.layout import HintedLayoutNode
import pyglet
from pyglet.gl import *

def main():

    global keys
    keys = ["GRAVE", "_1", "_2","_3","_4","_5","_6","_7","_8","_9", "_0", "MINUS", "EQUAL", "DELETE",
            "TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "BRACKETLEFT", "BRACKETRIGHT", "BACKSLASH",
            "CAPSLOCK", "A", "S", "D", "F", "G", "H", "J", "K", "L", "SEMICOLON", "APOSTROPHE", "ENTER",
            "LSHIFT", "Z", "X", "C", "V", "B", "N", "M", "COMMA", "PERIOD", "SLASH", "RSHIFT"]


    with open("keyboard.json") as f:
        data = json.loads(f.read())

    global key_rects
    key_rects = {keys[i]:data["frames"][str(i)]["frame"] for i in range(len(keys))}
    for key in keys:
        key_rects[key]["y"] = 244 - key_rects[key]["y"] - key_rects[key]["h"]

    global balls
    balls = [{"pos":Vector2(0,0), "vel": Vector2(0,0), "caught": "none", "dia":5}]

    global level
    level = {
        "default": ["none","wall"],
        "GRAVE": ["wall", "none"],
        "TAB": ["none", "goal"],
        "K": ["goal"],
        "C": ["hazard"],
        "LSHIFT": ["hazard"],
    }

    w = NodeWindow()
    w.fps = 30

    w.node, _ = deserialize_node("""
    HintedLayoutNode [724,244]
    """)

    # Stella's numbers are: [960,230]

    w.launch_listener(draw)
    w.launch_listener(find_keys_pressed)
    pyglet.app.run()




def find_keys_pressed():

    # TODO: make capslock work

    global keys

    global keys_pressed
    keys_pressed = {key: False for key in keys}

    while True:
        event, symbol, modifiers = yield ["on_key_press", "on_key_release"]

        for key in keys:
            if getattr(pyglet.window.key, key) == symbol:
                if event == "on_key_press": keys_pressed[key] = True
                if event == "on_key_release": keys_pressed[key] = False

        # filter down to 2 keys
        n = 0
        for key in keys:
            if n >= 2:
                keys_pressed[key] = False
                continue
            if keys_pressed[key]:
                n += 1



def draw():

    colors = {
        "none": [1.,1.,1.,1.],
        "wall": [0.,0.,0.,1.],
        "hazard": [1.,0.,0.,1.],
        "goal": [1.,1.,0.,1.],
    }

    global keys_pressed
    global level
    global keys
    global balls

    while True:
        yield "on_draw"

        # draw balls

        for key in keys:

            if key in level: value = level[key]
            else: value = level["default"]

            if keys_pressed[key] and len(value) > 1: value = value[1]
            else: value = value[0]

            color = colors[value]

            # draw key as rectangle
            glColor4f(color[0],color[1],color[2],color[3])
            rect = key_rects[key]
            glRectf(rect["x"],rect["y"],rect["x"]+rect["w"],rect["y"]+rect["h"])


# types of things a key can be
#  - wall
#  - goal
#  - hazard
#  - bouncer
#  - prism?
#  - mud
#  - gravity?


if __name__ == "__main__":
    main()
