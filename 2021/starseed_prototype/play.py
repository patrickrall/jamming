
import glfw
from patpygl import listen
from patpygl.quadarray import *
import globs
import math
from render import mouse_coords
from patpygl.vector import *
from patpygl.animator import *
import numpy as np
from mode import mode_switch


from patpygl.textbox import *

def play_init():
    # globs.playerarray renders the player
    animator = Animator()
    animator.enqueue(globs.assets["dino-idle-right"], loop=True, label="idle-right")
    globs.playerarray = QuadArray(animator)
    globs.quadarrays.append(globs.playerarray)

    globs.circlearray = QuadArray(globs.assets["circle"])
    globs.quadarrays.append(globs.circlearray)

    globs.boxcounttext = TextBox("IBMPlexSans-Regular.ttf",
                     size=30,
                     color=Vec(1,0,0),
                     pos=Vec(globs.cam["w"]-30,5,0.9))
    globs.textboxes.append(globs.boxcounttext)
    globs.boxcounttext.text = "0"
    globs.boxcount = 0

    listen.launch(play_loop())
    listen.launch(escape_loop())
    listen.launch(camera_move_loop())
    listen.launch(play_mouse_loop())


def camera_move_loop():
    while True:
        _, dt = yield from listen.event("on_frame")
        if globs.mode != "play": continue
        if globs.cam["pos"] == globs.cam["target_pos"]: continue

        distance = 5*dt

        delta = globs.cam["target_pos"] - globs.cam["pos"]
        length = np.sqrt(dot(delta,delta))
        if length < distance:
            globs.cam["pos"] -= globs.cam["pos"]
            globs.cam["pos"] += globs.cam["target_pos"]
        else:
            globs.cam["pos"] += delta*distance/length


# to be called by the editor
def place_player(x,y):
    assert len(globs.playerarray.quads) == 0
    globs.playerarray.quads.append(Vec(x,y,0.5))
    globs.circlearray.quads.append(Vec(x,y,0.6))
    globs.playerarray.update()
    globs.circlearray.update()

# press escape to exit play mode, delete the player quad
def escape_loop():
    while True:
        _, key, _, action, _ = yield from listen.on_key(globs.window)
        if key != glfw.KEY_ESCAPE: continue
        if action != glfw.PRESS: continue

        if len(globs.playerarray.quads) == 1:
            del globs.playerarray.quads[0]
            globs.playerarray.update()

            del globs.circlearray.quads[0]
            globs.circlearray.update()

        globs.mode = "grid_edit"


# give this thing a vector, and it'll keep it up to date
# with the direction of the dpad
def dpad_loop(dpad):
    keys = {
        glfw.KEY_W: False,
        glfw.KEY_A: False,
        glfw.KEY_S: False,
        glfw.KEY_D: False,
    }
    while True:
        _, key, _, action, _ = yield from listen.on_key(globs.window)
        if key in keys:
            if action == glfw.PRESS: keys[key] = True
            if action == glfw.RELEASE: keys[key] = False

        dpad.x = 0
        dpad.y = 0
        if keys[glfw.KEY_W]: dpad += Vec(0,1)
        if keys[glfw.KEY_A]: dpad += Vec(-1,0)
        if keys[glfw.KEY_S]: dpad += Vec(0,-1)
        if keys[glfw.KEY_D]: dpad += Vec(1,0)

        if False:
            # don't bother normalizing
            norm = np.sqrt(dot(dpad,dpad))
            if norm != 0:
                dpad /= norm


def play_loop():
    velocity = Vec(0,0)
    dpad = Vec(0,0)
    listen.launch(dpad_loop(dpad))
    direction = "right"

    collision_prec = 0.01
    collision_radius = 2

    playersize = globs.playerarray.asset["size"]
    gridsize = Vec(1,1)

    recent_portal = None

    while True:
        events = yield from listen.any(
            frame=listen.event("on_frame"),
        )

        if globs.mode != "play": continue
        _, dt = events["frame"]

        playerpos = globs.playerarray.quads[0]

        # is the player touching something?
        touch = {"top": Vec(0,1,0), "bot": Vec(0,-1,0), "left": Vec(-1,0,0), "right": Vec(1,0,0)}
        for key in touch:
            found = False
            for (x,y) in grid_positions_nearby(playerpos,collision_radius):
                if "dark" not in globs.grid[x,y]: continue
                if rects_intersect(Vec(x,y),playerpos + touch[key]*collision_prec,gridsize,playersize):
                    found = True
                    break
            touch[key] = found # replace dict entry with boolean

        if touch["bot"]:
            # if grounded, make the vertical velocity 0
            velocity.y = 0

            # if the player is pressing up, make them jump
            if dpad.y == 1:
                velocity.y = 3
        else:
            # otherwise apply gravity
            velocity.y -= 3*dt

        # horizontal movement
        velocity.x = dpad.x*3

        # head bonk
        if touch["top"] and velocity.y > 0:
            velocity.y = 0

        # bonk on sides
        if touch["right"] and velocity.x > 0: velocity.x = 0
        if touch["left"] and velocity.x < 0: velocity.x = 0

        # compute the delta, and apply it with collision detection
        delta = velocity*dt

        # move the player. split the delta into lots of tiny nudges
        # and then apply as many as you can before we collide
        for nudge in split_delta(delta,collision_prec):
            any_collisions = False
            for (x,y) in grid_positions_nearby(playerpos,collision_radius):
                if "dark" not in globs.grid[x,y]: continue
                if rects_intersect(Vec(x,y),playerpos+nudge.xy0,gridsize,playersize,):
                    any_collisions = True
                    break

            if any_collisions: break
            playerpos += nudge.xy0

        # finalize playerpos
        globs.playerarray.update()
        globs.circlearray.quads[0] = Vec(0,0,0)+playerpos
        globs.circlearray.quads[0] -= globs.circlearray.asset["size"].xy0/2
        globs.circlearray.quads[0] += globs.playerarray.asset["size"].xy0/2
        globs.circlearray.update()




        for (x,y) in grid_positions_nearby(playerpos,collision_radius):
            if globs.grid[x,y] != "portal": continue
            if not rect_in_rect(playerpos,Vec(x,y),playersize,gridsize): continue
            if (x,y) == recent_portal: continue
            mode_switch()
            velocity = Vec(0,0)
            recent_portal = (x,y)

        if recent_portal is not None:
            if not rects_intersect(playerpos,Vec(*recent_portal),playersize,gridsize):
                recent_portal = None


        # adjust the camera if we are not falling
        if touch["bot"]:
            globs.cam["target_pos"] = -playerpos.xy + globs.cam["dims"]/2


        # adjust the player sprite animation
        # compute the new label
        newlabel = "idle"
        if touch["bot"]:
            if velocity.x != 0: newlabel = "sneak"
            else: newlabel = "idle"
        else: newlabel = "move"

        # compute the direction the player is facing
        if velocity.x != 0:
            if velocity.x > 0: direction = "right"
            else: direction = "left"
        newlabel += "-"+direction

        # update the animator
        if globs.playerarray.asset.label != newlabel:
            globs.playerarray.asset.clear()
            globs.playerarray.asset.enqueue(globs.assets["dino-"+newlabel], loop=True, label=newlabel)



def play_mouse_loop():
    playersize = globs.playerarray.asset["size"]
    gridsize = Vec(1,1)


    while True:
        _, button, action, mods = yield from listen.on_mouse_button(globs.window)
        if action != glfw.PRESS: continue
        if globs.mode != "play": continue

        playerpos = globs.playerarray.quads[0]

        x,y = glfw.get_cursor_pos(globs.window)
        coords = mouse_coords(x,y)
        delta = coords - playerpos.xy
        if np.sqrt(dot(delta,delta)) > globs.circlearray.asset["size"].x/2: continue

        x0,y0 = np.floor(coords.x),np.floor(coords.y)
        while x0 > x: x0 -= 1
        while y0 > y: y0 -= 1
        x,y = x0,y0

        if rects_intersect(Vec(x,y),playerpos,gridsize,playersize): continue

        if "lock" in globs.grid[x,y]: continue
        if "light" in globs.grid[x,y]:
            if globs.boxcount == 0: continue
            globs.boxcount -= 1
            globs.grid[x,y] = globs.grid[x,y].replace("light","dark")
        elif "dark" in globs.grid[x,y]:
            globs.boxcount += 1
            globs.grid[x,y] = globs.grid[x,y].replace("dark","light")
        globs.boxcounttext.text = str(globs.boxcount)


def grid_positions_nearby(pos,r):
    x0,y0,r = np.round(pos.x),np.round(pos.y),np.ceil(r)

    x = x0-r-1
    while x < x0+r:
        x += 1
        y = y0-r-1
        while y < y0+r:
            y += 1
            if (x,y) in globs.grid:
                yield (x,y)


def rects_intersect(p1,p2,d1,d2):
    if p1.x + d1.x <= p2.x: return False
    if p2.x + d2.x <= p1.x: return False
    if p1.y + d1.y <= p2.y: return False
    if p2.y + d2.y <= p1.y: return False
    return True


# if p1+d1 in p2+d2
def rect_in_rect(p1,p2,d1,d2):
    if p2.x + d2.x < p1.x + d1.x: return False
    if p1.x < p2.x: return False
    if p2.y + d2.y < p1.y + d1.y: return False
    if p1.y < p2.y: return False
    return True

# a generator that splits a single vector delta
# into lots of little steps of size at most pl
def split_delta(delta,pl,prec=5):
    l = len(delta)
    if l == 0: return

    # find the largest index
    scaleidx = None
    for i in range(l):
        if delta[i] != 0:
            if scaleidx is None or abs(delta[scaleidx]) < abs(delta[i]):
                scaleidx = i
    if scaleidx is None: return

    # compute nudge
    nudge = zeros(l)
    for i in range(l):
        nudge[i] = math.copysign(pl*abs(delta[i])/abs(delta[scaleidx]),delta[i])

    # step through delta[scaleidx] in steps of pl
    tally = zeros(l)
    while abs(tally[scaleidx]) + pl < abs(delta[scaleidx]):
        tally += nudge
        yield nudge

    # if delta[scaleidx] doesn't divide evenly by pl
    # we may need to take one extra step
    if delta != tally:
        yield delta - tally


