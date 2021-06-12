from OpenGL.GL import *
import numpy as np
import ctypes
import glfw

from patpygl import listen
from patpygl.vector import *
from patpygl.projection import *

from polygon import *

import globs

def render_init(w,h):
    globs.cam = {
        "w": w, "h": h,
        "projection": None,
    }

    globs.hud_elements = [
        {
            "function": "switchColors",
            "sprite": "assets/hud_switchColors.png",
            "location": {"x": 2,"y": 12 },# world units (1 block = 1x1 world units)
            "size" : {"x": 16, "y" : 16} # pixel_width/20, pixel_height/20
        },
        {
            "function": "inventory",
            "sprite": "assets/hud.png",
            "location": {"x": 5 ,"y": 12 },
            "size" : {"x": 128, "y" : 16}# pixel_width/20, pixel_height/20
        },
    ]

    listen.launch(viewport_loop())
    listen.launch(render_loop())


def viewport_loop():
    while True:
        # set the viewport
        glViewport(0,0,globs.cam["w"], globs.cam["h"])

        # origin = bottom left corner
        # x,y = position in window in pixels
        proj = np.eye(4)
        proj = scale(2/globs.cam["w"],2/globs.cam["h"],1) @ proj
        proj = translate(-1,-1,0) @ proj
        globs.cam["projection"] = proj
        globs.cam["projection-inv"] = np.linalg.inv(proj)

        # wait until framebuffer gets resized
        yield from listen.on_framebuffer_size(globs.window)
        globs.cam["w"], globs.cam["h"] = glfw.get_framebuffer_size(globs.window)

# given x,y in pixels on screen, output point in game coordinates
def mouse_coords(x, y):
    x = 2 * x / globs.cam["w"] - 1
    y = -(2 * y / globs.cam["h"] - 1)
    s = Vec(x, y, 1, 1)

    m = globs.cam["projection-inv"]
    s @= m
    s = s.xy / s.w

    s -= globs.cam["pos"]
    return s

#######################################

def render_loop():

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    while True:
        yield from listen.event("on_render")

        # black background
        glClearColor(0,0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(Polygon.polygon_shader)
        set_uniform_matrix(Polygon.polygon_shader, "projection", globs.cam["projection"])

        for polygon in globs.polygons:
            polygon.draw()

        glfw.swap_buffers(globs.window)


