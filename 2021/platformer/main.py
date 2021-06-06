# module dependencies: numpy, pillow, pyopengl, glfw, freetype-py

import glfw
from OpenGL.GL import *
import numpy as np

from patpygl import listen, projection
from patpygl.vector import Vec
from patpygl.animator import *
from patpygl.quadarray import *
from patpygl.textbox import *

import globs
from render import render_init
from edit import edit_init
from play import play_init


def main():
    glfw.init()

    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)

    w,h = 800, 640

    globs.window = glfw.create_window(w, h, 'PlatformPrototype', None, None)
    x = glfw.make_context_current(globs.window)

    # initialize libraries
    init_quadarray()
    init_textbox(w=2000,h=2000) # dimension of glyph atlas


    globs.spf = 0.015 # 60ish fps

    # this stuff gets rendered by the render_loop
    globs.hud_quadarrays = []
    globs.quadarrays = []
    globs.textboxes = []

    # launch loops (order matters here)
    listen.launch(game_loop())
    render_init(w,h)
    load_assets()
    edit_init()
    play_init()


    # the main loop.
    while not glfw.window_should_close(globs.window):
        glfw.wait_events_timeout(globs.spf/10)
        listen.trigger_timers()

    glfw.terminate()



def game_loop():
    # put the fps meter into this textbox
    fpsbox = TextBox("IBMPlexSans-Regular.ttf",
                     size=30,
                     color=Vec(0,0,0),
                     pos=Vec(5,5,0.9))
    globs.textboxes.append(fpsbox)

    dt_count, dt_sum = 0, 0 # tally up the dt's
    dt = 1 # first value of dt
    while True:
        # render, and compute how much time it took
        t0 = glfw.get_time()
        listen.dispatch("on_frame",dt)
        listen.dispatch("on_render")
        dt_render = glfw.get_time() - t0

        # wait a bit to match the fps rate if needed
        _, dt_wait = yield from listen.wait(max(globs.spf - dt_render,0))
        dt = dt_wait + dt_render

        # put the average fps into the textbox
        dt_count += 1
        dt_sum += dt
        if dt_sum >= 0.5: # every half second
            fpsbox.text = str(int(dt_count/dt_sum*10)/10) + "fps"
            dt_count, dt_sum = 0, 0


def load_assets():
    from patpygl.quadarray import QuadArray
    spritesheets = []
    spritesheets.append("assets/grassland.json")
    spritesheets.append("assets/dino.json")

    # all the assets get put in here
    globs.assets = {}

    for fname in spritesheets:
        # frames is a list of dictionaries with {"texture", "duration", "w,", "h", "texcoords"}
        # sheet is a dictionary of lists, lists containing subsets fo the frames
        frames, sheet = load_spritesheet(fname)

        # post-process the sheet a little bit, populate globs.assets
        for key in sheet:
            if key in globs.assets:
                print("Duplicate asset",key,"in",fname)
                continue

            # if the key ends in "-right", populate this list with some "-left" frames
            flipped_frames = []

            for frame in sheet[key]:
                # add the "size" key to the frame. Quadarray uses this to decide how big the texture is.
                frame["size"] = Vec(sheet[key][0]["w"]/globs.cam["pixels_per_unit"],
                                     sheet[key][0]["h"]/globs.cam["pixels_per_unit"])

                # if key ends in "-right", copy the frame with the texcoords flipped l<->r
                if key[-6:] == "-right":
                    flipped_frames.append({
                        "texture": frame["texture"],
                        "duration": frame["duration"],
                        "w": frame["w"], "h": frame["h"],
                        "texcoords": {
                            "tl": frame["texcoords"]["tr"],
                            "tr": frame["texcoords"]["tl"],
                            "bl": frame["texcoords"]["br"],
                            "br": frame["texcoords"]["bl"],
                        },
                        "size": frame["size"]
                    })

            # populate globs.assets
            globs.assets[key] = sheet[key]
            if key[-6:] == "-right":
                globs.assets[key[:-6]+"-left"] = flipped_frames


    # load HUD elements, note window is 800x640
    for element in globs.hud_elements:
        hud_asset = load_png(element["sprite"])
        hud_asset["size"] = Vec(element["size"]["x"], element["size"]["y"]) / globs.cam["pixels_per_unit"] # 16 pixels per unit in the camera
        hud_array = QuadArray(hud_asset)
        hud_array.quads.append(Vec(element["location"]["x"], element["location"]["y"], 0.5))  # +z draws on top of -z
        hud_array.update()
        globs.hud_quadarrays.append(hud_array)

if __name__ == "__main__": main()
