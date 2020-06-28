
import pyglet
from pyglet.gl import *

from swyne.node import *
from swyne.text import LabelNode
from swyne.images import load_spritesheet

import random


# TODO:
# add support for animation
# make menu screen using node graph



def run_game():

    w = NodeWindow()
    w.fps = 30 # yield "on_draw" and "on_frame" events 30 times per second

    # global variables for gameplay
    global player
    player = {"x":100, "y":100, "alive":True, "respawn_timer": 0, "lives":3}

    # initialize the player's animation information
    global player_display
    player_display = {"should_draw": True, "key":"player", "frame":0, "frame_clock":0}

    global asteroids
    asteroids = [{"x":50, "y":150, "vx":100, "vy":100}]


    # node graph for menu system
    w.node, keys = deserialize_node("""
    hint HintedLayoutNode
    -PaddingLayoutNode [5,"*","*","*"]
    --label LabelNode "{color (255,255,255,255)} placeholder"
    """)

    # global variables for menu system
    global window_dims
    window_dims = {"width": 800, "height":600}
    keys["hint"].mindims.x = window_dims["width"]
    keys["hint"].maxdims.x = window_dims["width"]
    keys["hint"].mindims.y = window_dims["height"]
    keys["hint"].maxdims.y = window_dims["height"]

    global lives_node
    lives_node = keys["label"]
    lives_node.document.text = "Remaining lives: "+str(player["lives"])

    # load the spritesheet
    global sprites
    sprites = load_spritesheet("pat_asteroids.json")

    # attach the listeners
    w.launch_listener(frame)
    w.launch_listener(keystate)
    w.launch_listener(player_animation)
    w.launch_listener(draw)

    pyglet.app.run()


def player_animation():
    global player
    global player_display
    global sprites

    while True:
        _, dt = yield "on_frame"

        if player["alive"]:
            # alive player: loop the player idle animation

            # reset animation if needed
            if player_display["key"] != "player":
                player_display["frame"] = 0
                player_display["frame_clock"] = 0
                player_display["should_draw"] = True
                player_display["key"] = "player"

            # tick animation
            player_display["frame_clock"] += dt

            if player_display["frame_clock"] > sprites["player"].frames[player_display["frame"]].duration:
                player_display["frame_clock"] -= sprites["player"].frames[player_display["frame"]].duration
                player_display["frame"] += 1

            # loop animation
            if player_display["frame"] >= len(sprites["player"].frames):
                player_display["frame"] = 0

        else:
            # dead player: play explosion animation once

            # reset animation if needed
            if player_display["key"] != "dead-player":
                player_display["frame"] = 0
                player_display["frame_clock"] = 0
                player_display["should_draw"] = True
                player_display["key"] = "dead-player"

            if player_display["frame"] >= len(sprites["dead-player"].frames):
                continue # animation has ended

            # tick animation
            player_display["frame_clock"] += dt

            if player_display["frame_clock"] > sprites["dead-player"].frames[player_display["frame"]].duration:
                player_display["frame_clock"] -= sprites["dead-player"].frames[player_display["frame"]].duration
                player_display["frame"] += 1

            if player_display["frame"] >= len(sprites["dead-player"].frames):
                 # animation has ended, disable drawing
                player_display["should_draw"] = False

def draw():

    global sprites

    # modify the spritesheet a bit:
    # anchor the images at their center. This informs the image.blit function.
    for key in sprites.keys():
        for frame in sprites[key].frames:
            frame.image.anchor_x = frame.image.width/2
            frame.image.anchor_y = frame.image.height/2

    # pre_compute asteroid data
    img = sprites["asteroid"].frames[0].image
    w,h = img.width, img.height
    vertices = -w/2,-h/2,0,w/2,-h/2,0,w/2,h/2,0,-w/2,h/2,0

    # creating a vertex_list pre-loads the vertices onto the GPU
    asteroid_texture = img.get_texture()
    asteroid_vertex_list = pyglet.graphics.vertex_list_indexed(4,
            [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', asteroid_texture.tex_coords))

    # cleanup
    del img,w,h,vertices

    global player
    global asteroids

    while True:
        yield "on_draw"

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # draw player via image.blit
        if player_display["should_draw"]:
            sprites[player_display["key"]].frames[player_display["frame"]].image.blit(player["x"],player["y"])

        # https://github.com/pyglet/pyglet/blob/master/pyglet/image/__init__.py
        # line 1596 defines what actually happens when a texture is blit
        # a little bit inefficient if you are drawing the same texture lots of times

        # draw asteroids using a method built for drawing the same thing lots of times

        # asteroid texture only needs to be enabled once
        glEnable(asteroid_texture.target)
        glBindTexture(asteroid_texture.target, asteroid_texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)

        for asteroid in asteroids:

            glPushMatrix()

            # specify position via translation
            glTranslatef(asteroid["x"],asteroid["y"],0)

            # vertex array is already stored on GPU. just draw those.
            asteroid_vertex_list.draw(GL_TRIANGLES)

            glPopMatrix()

        # asteroid texture needs to only be disabled once
        glPopAttrib()
        glDisable(asteroid_texture.target)


def keystate():
    # records key state in the wasd_keys dictionary

    global wasd_keys
    wasd_keys = {key:False for key in ["W","A","S","D"]}

    while True:
        event, symbol, modifiers = yield ["on_key_press", "on_key_release"]

        for key in ["W","A","S","D"]:
            if getattr(pyglet.window.key,key) == symbol:
                if event == "on_key_press": wasd_keys[key] = True
                if event == "on_key_release": wasd_keys[key] = False



def frame():

    global asteroids
    global window_dims
    global lives
    global lives_node
    global wasd_keys

    while True:
        event, dt = yield "on_frame"

        to_delete = []
        for asteroid in asteroids:

            # move asteroids
            asteroid["x"] += asteroid["vx"]*dt
            asteroid["y"] += asteroid["vy"]*dt

            # check if this asteroid is offscreen and needs to be deleted
            offset = 100
            if asteroid["x"] < -offset\
                    or asteroid["x"] > window_dims["width"]+offset\
                    or asteroid["y"] < -offset\
                    or asteroid["y"] > window_dims["height"]+offset:
                to_delete.append(asteroid)

        for deleted_asteroid in to_delete:
            asteroids.remove(deleted_asteroid)

        # put more asteroids on screen
        while len(asteroids) < 20:

            new_asteroid = {
                    "x": random.random()*window_dims["width"],
                    "y": window_dims["height"], # start at the top
                    "vx": 40*(random.random() - 0.5),
                    "vy": - (80 + 100*random.random())
                }

            asteroids.append(new_asteroid)

        if player["alive"]:
            #  move player
            v = 200
            dx,dy = 0,0
            if wasd_keys["W"]: dy += v
            if wasd_keys["S"]: dy -= v
            if wasd_keys["A"]: dx -= v
            if wasd_keys["D"]: dx += v
            player["x"] += dx*dt
            player["y"] += dy*dt

            # check if the player is hit
            for asteroid in asteroids:
                dx = asteroid["x"] - player["x"]
                dy = asteroid["y"] - player["y"]

                r = 50
                if dx*dx + dy*dy < r*r:
                    # player is hit

                    player["alive"] = False
                    player["respawn_timer"] = 3
                    player["lives"] -= 1

                    lives_node.document.text = "Remaining lives: "+str(player["lives"])
                    if player["lives"] > 0: lives_node.document.text += ". Respawning..."
                    else:
                        lives_node.document.text = "Game Over!"

                    break

        elif player["lives"] > 0: # player is dead but has remaining lives

            player["respawn_timer"] -= dt

            if player["respawn_timer"] < 0:
                # try to respawn player at this location:
                x,y = window_dims["width"]/2,  100

                no_asteroids_nearby = True
                for asteroid in asteroids:
                    dx = asteroid["x"] - x
                    dy = asteroid["y"] - y

                    r = 150
                    if dx*dx + dy*dy < r*r:
                        no_asteroids_nearby = False
                        break

                # only spawn player if that spot is free of asteroids
                if no_asteroids_nearby:
                    player["alive"] = True
                    player["x"] = x
                    player["y"] = y

                    lives_node.document.text = "Remaining lives: "+str(player["lives"])



if __name__ == "__main__":
    run_game()

