
import pyglet
from pyglet.gl import *

from swyne.node import *
from swyne.text import LabelNode
from swyne.images import load_spritesheet

import random

@listener
def draw(w):

    sprites = load_spritesheet("pat_asteroids.json")

    def get_texture_and_vertices(key):
        img = sprites[key].frames[0].image
        texture = img.get_texture()
        w,h = img.width, img.height
        vertices = -w/2,-h/2,0,w/2,-h/2,0,w/2,h/2,0,-w/2,h/2,0
        vertex_list = pyglet.graphics.vertex_list_indexed(4,
            [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', texture.tex_coords))
        return texture, vertex_list

    alive_player_texture, alive_player_vertices = get_texture_and_vertices("player")
    dead_player_texture, dead_player_vertices = get_texture_and_vertices("dead-player")
    asteroid_texture, asteroid_vertices = get_texture_and_vertices("asteroid")

    global player
    global asteroids

    while True:
        yield "on_draw"

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


        # draw player
        if player["alive"]:
            player_texture, player_vertices = alive_player_texture, alive_player_vertices
        else:
            player_texture, player_vertices = dead_player_texture, dead_player_vertices

        glEnable(player_texture.target)
        glBindTexture(player_texture.target, player_texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)

        glPushMatrix()
        glTranslatef(player["x"],player["y"],0)
        player_vertices.draw(GL_TRIANGLES)
        glPopMatrix()

        glPopAttrib()
        glDisable(player_texture.target)

        # draw asteroids
        glEnable(asteroid_texture.target)
        glBindTexture(asteroid_texture.target, asteroid_texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)

        for asteroid in asteroids:

            glPushMatrix()
            glTranslatef(asteroid["x"],asteroid["y"],0)
            asteroid_vertices.draw(GL_TRIANGLES)
            glPopMatrix()

        glPopAttrib()
        glDisable(asteroid_texture.target)


@listener
def keystate(w):
    global wasd_keys
    wasd_keys = {key:False for key in ["W","A","S","D"]}

    while True:
        event, symbol, modifiers = yield ["on_key_press", "on_key_release"]

        for key in ["W","A","S","D"]:
            if getattr(pyglet.window.key,key) == symbol:
                if event == "on_key_press": wasd_keys[key] = True
                if event == "on_key_release": wasd_keys[key] = False



@listener
def frame(w):

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
        while len(asteroids) < 10:

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
                    player["alive"] = False
                    player["respawn_timer"] = 3
                    player["lives"] -= 1
                    lives_node.document.text = "Remaining lives: "+str(player["lives"])
                    if player["lives"] > 0: lives_node.document.text += ". Respawning..."
                    else:
                        lives_node.document.text = "Game Over!"

                    break

        elif player["lives"] > 0:
            player["respawn_timer"] -= dt

            if player["respawn_timer"] < 0:

                x,y = window_dims["width"]/2,  100

                no_asteroids_nearby = True

                for asteroid in asteroids:
                    dx = asteroid["x"] - x
                    dy = asteroid["y"] - y

                    r = 150
                    if dx*dx + dy*dy < r*r:
                        no_asteroids_nearby = False
                        break

                if no_asteroids_nearby:
                    player["alive"] = True
                    player["x"] = x
                    player["y"] = y

                    lives_node.document.text = "Remaining lives: "+str(player["lives"])


def run_game():


    w = NodeWindow()
    w.fps = 30 # yield "on_draw" and "on_frame" events 30 times per second

    # text business
    w.node, keys = deserialize_node("""
    hint HintedLayoutNode
    -PaddingLayoutNode [5,"*","*","*"]
    --label LabelNode "{color (255,255,255,255)} placeholder"
    """)

    global window_dims
    window_dims = {"width": 800, "height":600}
    keys["hint"].mindims.x = window_dims["width"]
    keys["hint"].maxdims.x = window_dims["width"]
    keys["hint"].mindims.y = window_dims["height"]
    keys["hint"].maxdims.y = window_dims["height"]

    global player
    player = {"x":100, "y":100, "alive":True, "respawn_timer": 0, "lives":3}

    global lives_node
    lives_node = keys["label"]
    lives_node.document.text = "Remaining lives: "+str(player["lives"])

    global asteroids
    asteroids = [{"x":50, "y":150, "vx":100, "vy":100}]

    frame(w)

    keystate(w)

    draw(w)

    pyglet.app.run()

if __name__ == "__main__":
    run_game()

