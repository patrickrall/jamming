import glfw
from OpenGL.GL import *
import numpy as np

from patpygl import listen, projection
from patpygl.vector import *

import globs
from render import render_init
from polygon import *
from edit_triangles import *


def main():
    glfw.init()

    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)

    w,h = 800, 800

    globs.window = glfw.create_window(w, h, 'Polygon', None, None)
    x = glfw.make_context_current(globs.window)

    init_polygon_shader()

    globs.colors = [Vec(1.0, 0.0, 1.0, 1.0), Vec(1.0, 1.0, 1.0, 1.0), Vec(0.5, 0.5, 1.0, 1.0), Vec(0.0,1.0,1.0,1.0)]
    globs.colorIndex = 0
    print(globs.colors[0])
    globs.tri = {}
    globs.tri["i_max"] = 5
    globs.tri["j_max"] = 5
    globs.tri["offsetX"] = 50
    globs.tri["offsetY"] = 50
    globs.tri["scaleX"] = 50
    globs.tri["scaleY"] = 50

    # this stuff gets rendered by the render_loop
    globs.polygons = []
    #generate arrays
    for i in range(0, globs.tri["i_max"]):
        for j in range(0, globs.tri["j_max"]):
            isStaggered = (j % 2 == 1)
            if not isStaggered:
                p1, p2, p3 = grid_index_to_position(i, j, True) # upward point
                globs.polygons.append(Polygon(Vec(i/globs.tri["i_max"], j/globs.tri["j_max"], 1.0, 1.0), [p1, p2, p3]))
                p1, p2, p3 = grid_index_to_position(i, j, False) # downward point
                globs.polygons.append(Polygon(globs.colors[1 if isStaggered else 3], [p1, p2, p3]))
            else:
                p1, p2, p3 = grid_index_to_position(i, j, False) # downward point
                globs.polygons.append(Polygon(globs.colors[1 if isStaggered else 3], [p1, p2, p3]))
                p1, p2, p3 = grid_index_to_position(i, j, True) # upward point
                globs.polygons.append(Polygon(Vec(i/globs.tri["i_max"], j/globs.tri["j_max"], 1.0, 1.0), [p1, p2, p3]))

    # launch loops (order matters here)
    globs.spf = 0.015 # 60ish fps
    listen.launch(game_loop())

    render_init(w,h)
    edit_init()

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
