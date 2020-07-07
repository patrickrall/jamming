
import pyglet
from pyglet.gl import *

from swyne.node import *
from swyne.text import LabelNode
from swyne.images import load_spritesheet

import random


# TODO:
# prevent sliding to the side when atop a block
# faster gravity
# bigger jump
# jump moving up for longer


global collision_layers
collision_layers = [[True, True, True], [True, True, False], [True, False, True]] # player, asteroid, wall

def run_game():
    print("A-D to move sideways, W to jump")
    w = NodeWindow()
    w.fps = 30 # yield "on_draw" and "on_frame" events 30 times per second

    # global variables for gameplay
    global player
    player = {"x":400, "y":400, "vx": 0, "vy": -100, "alive":True, "respawn_timer": 0, "lives":3, "layer": 0, "grounded" : False, "none_static_kinematic": 2, "gravity" : -500}

    # initialize the player's animation information
    global player_display
    player_display = {"should_draw": True, "key":"player", "frame":0, "frame_clock":0}

    global asteroids, base_asteroid
    base_asteroid = {"x":50, "y":150, "vx":100, "vy":100, "layer": 1, "none_static_kinematic": 2, "gravity": 0} #kinematic}
    asteroids = [base_asteroid]
    global walls, base_wall
    base_wall = {"x":50, "y":150, "vx":100, "vy":100, "layer": 2, "none_static_kinematic" : 1, "gravity": 0} #static
    walls = [base_wall] # single wall to start


    # node graph for menu system
    global node_keys
    w.node, node_keys = deserialize_node("""
    hint HintedLayoutNode [800,600]
    -listen ListenerNode
    -PaddingLayoutNode [5,"*","*","*"]
    --lives LabelNode "{color (255,255,255,255)} placeholder"
    """)

    node_keys["hint"] == w.node
    w.node.children[1].children[0] == node_keys["lives"]

    # initialize label
    node_keys["lives"].document.text = "Remaining lives: "+str(player["lives"])

    # load the spritesheet
    global sprites
    sprites = load_spritesheet("pat_asteroids.json")

    # attach the listeners
    w.launch_listener(frame)
    w.launch_listener(keystate)
    w.launch_listener(player_animation)

    # attach draw listener to listener node
    node_keys["listen"].listener = draw

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

    # pre_compute wall data
    img = sprites["wall"].frames[0].image
    w,h = img.width, img.height
    vertices = -w/2,-h/2,0,w/2,-h/2,0,w/2,h/2,0,-w/2,h/2,0

    # creating a vertex_list pre-loads the vertices onto the GPU
    wall_texture = img.get_texture()
    wall_vertex_list = pyglet.graphics.vertex_list_indexed(4,
            [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', wall_texture.tex_coords))

    # cleanup
    del img,w,h,vertices

    global player
    global asteroids
    global walls

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

        # wall texture only needs to be enabled once
        glEnable(wall_texture.target)
        glBindTexture(wall_texture.target, wall_texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)

        for wall in walls:
            glPushMatrix()

            # specify position via translation
            glTranslatef(wall["x"], wall["y"], 0)

            # vertex array is already stored on GPU. just draw those.
            wall_vertex_list.draw(GL_TRIANGLES)

            glPopMatrix()

        # wall texture needs to only be disabled once
        glPopAttrib()
        glDisable(wall_texture.target)


def keystate():
    # records key state in the wasd_keys dictionary2d array python check index within size

    global wasd_keys
    wasd_keys = {key:False for key in ["W","A","S","D"]}

    while True:
        event, symbol, modifiers = yield ["on_key_press", "on_key_release"]

        for key in ["W","A","S","D"]:
            if getattr(pyglet.window.key,key) == symbol:
                if event == "on_key_press": wasd_keys[key] = True
                if event == "on_key_release": wasd_keys[key] = False


def can_collide(dict0, dict1, max_dist=16):
    """Test whether the objects represented by the dictionaries are colliding"""
    global collision_layers
    layer0 = round(dict0["layer"])
    layer1 = round(dict1["layer"])
    assert(
        layer0 > -1 and layer0 < len(collision_layers) and layer1 > -1 and layer1 < len(collision_layers[0]),
        "check_collision function: invalid values for 'layer' key in argument dictionaries compared to size of collision_layers 2D array")
    # if not collision_layers[layer0][layer1]: # no collision possible
    #     return False
    # layers can collide
    dx = dict0["x"] - dict1["x"]
    dy = dict0["y"] - dict1["y"]

    if dx * dx + dy * dy < max_dist * max_dist :
        return True
    return False

def collide_with(dict0, dict1):
    """Perform object 0 reaction to colliding with object 1. Assumes collision is possible."""
    isStatic = dict0["none_static_kinematic"] == 0
    if isStatic: # this object is moved by code or not at all
        pass
    else: # bounce away
        [sign_x, sign_y] = collision_sign(dict0, dict1)
        print(dict0['vx'])
        dict0["x"] = sign_x * 5 + dict0["x"] # move object
        dict0["y"] = sign_y * 5 + dict0["y"]
        if ("vx" in dict0):
            print("bad")

def collision_sign(dict0, dict1, max_dist = 16):
    """Detect which direction objects should move after a collision - this prevents collision direction errors when the player is commanding a velocity"""
    assert("x" in dict0 and "x" in dict1 and "y" in dict0 and "y" in dict1, "collision_sign function: no key 'x' or 'y' found in argument dictionariesdddddddd")
    dx = dict0["x"] - dict1["x"]
    dy = dict0["y"] - dict1["y"]
    sign_x, sign_y = 0, 0
    if (abs(dx) < max_dist):  # collision in x
        sign_x = 1 if dx > 0 else -1
    if (abs(dy) < max_dist):  # collision in y
        sign_y = 1 if dy > 0 else -1
    return [sign_x, sign_y, dx, dy]

def frame():

    global asteroids, base_asteroid
    global walls, base_wall
    global node_keys
    global lives
    global wasd_keys

    window_width = node_keys["hint"].dims.x
    window_height = node_keys["hint"].dims.y
    tilesize = 16

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
                    or asteroid["x"] > window_width+offset\
                    or asteroid["y"] < -offset\
                    or asteroid["y"] > window_height+offset:
                to_delete.append(asteroid)

        for deleted_asteroid in to_delete:
            asteroids.remove(deleted_asteroid)

        # put more asteroids on screen
        while len(asteroids) < 1:
            new_asteroid = {
                "x": random.random()*window_width,
                "y" : window_height, # start at the top
                "vx" : 40*(random.random() - 0.5),
                "vy" : - (80 + 100*random.random()),
                "none_static_kinematic": 2,  # kinematic
                "layer": 1
            }

            asteroids.append(new_asteroid)

        while len(walls) < 200:

            new_wall = {
                    "x": round(random.random() * window_width / tilesize) * tilesize,
                    "y": round(random.random() * window_height / tilesize) * tilesize, # start at the top
                    "vx": 0,
                    "vy": 0,
                    "none_static_kinematic": 1, #static
                    "layer": 2
                }

            walls.append(new_wall)

        if player["alive"]:
            #  move player
            v = 200
            jump = 500
            dx,dy = 0,0

            # Jumping and falling effects
            dx += player["vx"] * dt
            dy += player["vy"] * dt

            if not player["grounded"]:
                player["vy"] = player["gravity"] # fall if in the air
            else:
                player["vy"] = 0
                dy = 0

            if wasd_keys["W"] and player["grounded"]:
                dy += jump # jump
                player["vy"] = 100 #initial velocity up
                player["grounded"] = False

            #if wasd_keys["S"]: dy -= v
            if wasd_keys["A"]: dx -= v
            if wasd_keys["D"]: dx += v

            # check if the player is hit
            for asteroid in asteroids:
                will_collide = can_collide(asteroid, player)
                if will_collide:
                    # player is hit
                    player["alive"] = False
                    player["respawn_timer"] = 3
                    player["lives"] -= 1

                    node_keys["lives"].document.text = "Remaining lives: "+str(player["lives"])
                    if player["lives"] > 0: node_keys["lives"].document.text += ". Respawning..."
                    else:
                        node_keys["lives"].document.text = "Game Over!"

                    break

            # check if the player is hit
            i = 0
            for wall in walls:
                i += 1
                will_collide = can_collide(wall, player, 18)
                if will_collide:
                    #print("hit block")
                    #(player, wall) # player reacts to wall collision - wall doesn't need to react
                    [sign_x, sign_y, diffx, diffy] = collision_sign(player, wall) # 0, -1 or 1
                    dx = sign_x * 16
                    dy = (sign_y if sign_y > 0 else -0.5) * 16
                    if not player["grounded"] and diffy > 0 and diffy < 20: # player pushed up by ground
                        player["grounded"] = True
                    else:
                        player["grounded"] = False # far from ground


            player["x"] += dx*dt
            player["y"] += dy*dt

        elif player["lives"] > 0: # player is dead but has remaining lives

            player["respawn_timer"] -= dt

            if player["respawn_timer"] < 0:
                # try to respawn player at this location:
                x,y = window_width/2,  100

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

                    node_keys["lives"].document.text = "Remaining lives: "+str(player["lives"])



if __name__ == "__main__":
    run_game()

