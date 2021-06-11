import glfw
from OpenGL.GL import *
import numpy as np

from patpygl import listen, projection
from patpygl.vector import *

import globs
from render import render_init
from polygon import *


def main():
    glfw.init()

    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)

    w,h = 800, 640

    globs.window = glfw.create_window(w, h, 'Polygon', None, None)
    x = glfw.make_context_current(globs.window)

    init_polygon_shader()

    # this stuff gets rendered by the render_loop
    globs.polygons = []

    globs.polygons.append(Polygon(Vec(1.0,0,0,1.0),\
            [Vec(150,50,0), Vec(100,150,0), Vec(50,50,0)]))

    globs.polygons.append(Polygon(Vec(1.0,0,1.0,1.0),\
            [Vec(200,200,0), Vec(200,300,0), Vec(300,300,0),Vec(300,200,0)]))

    globs.polygons.append(Polygon(Vec(0.0,1.0,1.0,1.0),\
            [Vec(410,200,0), Vec(390,290,0), Vec(450,350,0),Vec(510,290,0),Vec(490,200,0)]))


    # launch loops (order matters here)
    globs.spf = 0.015 # 60ish fps
    listen.launch(game_loop())

    render_init(w,h)

    # the main loop.
    while not glfw.window_should_close(globs.window):
        glfw.wait_events_timeout(globs.spf/10)
        listen.trigger_timers()

    glfw.terminate()


def game_loop():
    dt = 1
    while True:
        # render, and compute how much time it took
        t0 = glfw.get_time()
        listen.dispatch("on_frame",dt)
        listen.dispatch("on_render")
        dt_render = glfw.get_time() - t0

        # wait a bit to match the fps rate if needed
        _, dt_wait = yield from listen.wait(max(globs.spf - dt_render,0))
        dt = dt_wait + dt_render

if __name__ == "__main__": main()
