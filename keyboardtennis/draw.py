
from pyglet.gl import *
import globs

def init_draw(w):

    # TODO grab images

    w.launch_listener(draw)


def draw():

    balls = globs.balls
    keys = globs.keys
    level = globs.level
    keys_pressed = globs.keys_pressed
    key_rects = globs.key_rects

    colors = {
        "none": [1.,1.,1.,1.],
        "wall": [0.,0.,0.,1.],
        "hazard": [1.,0.,0.,1.],
        "goal": [1.,1.,0.,1.],
    }



    while True:
        yield "on_draw"


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

        for ball in balls:
            glColor4f(0,0,0,1)
            x,y = ball["pos"].x, ball["pos"].y
            r = ball["dia"]/2.0
            t = 10
            glRectf(x-r, y-r, x+r,y+r)


