from OpenGL.GL import *
import numpy as np
import ctypes
import glfw

from patpygl import listen
from patpygl.vector import *
from patpygl.projection import *
from patpygl.quadarray import *
from patpygl.textbox import *

import globs

def render_init(w,h):
    globs.cam = {
        "pos":Vec(0,0),         # of bottom left corner of screen, in units
        "pixel_scale": 3,       # each asset pixel occupies this many screen pixels
        "pixels_per_unit": 16,  # this is asset pixels, not screen pixels
        "w": w, "h": h,         # width in screen pixels, height in screen pixels
        "projection": None,     # viewport_loop populates this with a matrix
        "projection-inv": None, # and its inverse here.
        "w_asset" : w/16/3,     # width in asset pixels is width / pixels_per_unit / pixel_scale
        "h_asset" : h/16/3,     # height in asset pixels is height / pixels_per_unit / pixel_scale
        "smoothing" : False,    # is the camera's motion smoothed (True), or does it snap to the player (False)
        "smoothing_factor" : 5  # how smooth is the motion (higher numbers are slower, smoother motion
    }
    globs.hud_elements = [
        {
            "function": "test",
            "sprite": "assets/hud.png",
            "location": {"x": 12,"y": 12 },# world units (1 block = 1x1 world units)
            "size" : {"x": 128, "y" : 16} # pixel_width/20, pixel_height/20
        },
        {
            "function": "inventory",
            "sprite": "assets/hud.png",
            "location": {"x": 12 ,"y": 3 },
            "size" : {"x": 128, "y" : 16}# pixel_width/20, pixel_height/20
        },
    ]
    listen.launch(viewport_loop())
    listen.launch(render_loop())


def viewport_loop():
    while True:
        # set the viewport
        glViewport(0,0,globs.cam["w"], globs.cam["h"])

        # build orthographic projection
        proj = np.eye(4)
        s = globs.cam["pixels_per_unit"]*globs.cam["pixel_scale"]
        proj = scale(s,s,-1) @ proj
        proj = scale(2/globs.cam["w"],2/globs.cam["h"],1) @ proj
        proj = translate(-1,-1,0) @ proj
        globs.cam["projection"] = proj
        globs.cam["projection-inv"] = np.linalg.inv(proj)

        # wait until framebuffer gets resized
        yield from listen.on_framebuffer_size(globs.window)
        globs.cam["w"], globs.cam["h"] = glfw.get_framebuffer_size(globs.window)

# given x,y in pixels on screen, output point in game coordinates
def mouse_coords(x,y):
    x = 2*x/globs.cam["w"] - 1
    y = -(2*y/globs.cam["h"] - 1)
    s = Vec(x, y, 1, 1)

    m = globs.cam["projection-inv"]
    s @= m
    s = s.xy/s.w

    s -= globs.cam["pos"]
    return s

#######################################

def render_loop():

    # Need depth testing for z order
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    # Need blending for text rendering
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    while True:
        yield from listen.event("on_render")

        # blue background
        glClearColor(0.16,0.67,1.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Load the quadshader. Load the projection uniform with the camera position.
        glUseProgram(QuadArray.quadshader)
        proj = globs.cam["projection"] @ translate(globs.cam["pos"].xy0) # translation based on world position of camera
        set_uniform_matrix(QuadArray.quadshader, "projection", proj)
        # draw world
        for quadarray in globs.quadarrays:
            quadarray.draw()

        # HUD setup for drawing
        HUDproj = globs.cam["projection"]
        set_uniform_matrix(QuadArray.quadshader, "projection", HUDproj)
        # draw HUD
        for quadarray in globs.hud_quadarrays:
            quadarray.draw()


        # Load the textbox shader. Text is in pixels, not units,
        # so need to scale appropriately. Ignore camera position.
        glUseProgram(TextBox.textshader)
        s = globs.cam["pixels_per_unit"]*globs.cam["pixel_scale"]
        tproj =  globs.cam["projection"] @ scale(1/s,1/s,1)
        set_uniform_matrix(TextBox.textshader, "projection", tproj)

        for textbox in globs.textboxes:
            textbox.draw()

        glfw.swap_buffers(globs.window)


