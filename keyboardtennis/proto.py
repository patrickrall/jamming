
import json
from swyne.node import NodeWindow,Vector2,deserialize_node
from swyne.layout import HintedLayoutNode
import pyglet
from pyglet.gl import *

def main():

    global keys
    keys = ["`", "1", "2","3","4","5","6","7","8","9", "0", "-", "=", "del",
            "tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\",
            "caps", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "enter",
            "lshift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "rshift"]

    # make window

    global keys_pressed
    keys_pressed = {key:False for key in keys}


    with open("keyboard.json") as f:
        data = json.loads(f.read())

    global key_rects
    key_rects = {keys[i]:data["frames"][str(i)]["frame"] for i in range(len(keys))}

    global balls
    balls = [{"pos":Vector2(0,0), "vel": Vector2(0,0), "caught": "none", "dia":5}]

    global level
    level = {
        "default": ["none","wall"],
        "`": ["wall", "none"],
        "y": ["none", "goal"],
        "k": ["goal"],
        "c": ["hazard"],
        "lshift": ["hazard"],
    }

    w = NodeWindow()
    w.fps = 30

    w.node, _ = deserialize_node("""
    HintedLayoutNode [960,230]
    """)

    # Stella's numbers are: [960,230]

    w.launch_listener(draw)
    pyglet.app.run()



def draw():

    colors = {
        "none": [1.,1.,1.,1.],
        "wall": [0.,0.,0.,1.],
        "hazard": [1.,0.,0.,1.],
        "goal": [1.,1.,0.,1.],
    }

    while True:
        yield "on_draw"

        # draw balls

        for key in keys:
            idx = 1 if keys_pressed[key] else 0

            if key in level: value = level[key][idx]
            else: value = level["default"][idx]

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
