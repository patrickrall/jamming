
import glfw
from patpygl import listen
from patpygl.quadarray import *
import globs
import math
from patpygl.vector import *
from patpygl.animator import *
import numpy as np

def play_init():
    # globs.playerarray renders the player
    animator = Animator()
    animator.enqueue(globs.assets["dino-idle-right"], loop=True, label="idle-right")
    globs.playerarray = QuadArray(animator)
    globs.quadarrays.append(globs.playerarray)

    listen.launch(play_loop())
    listen.launch(escape_loop())

# to be called by the editor
def place_player(x,y):
    assert len(globs.playerarray.quads) == 0
    globs.playerarray.quads.append(Vec(x,y,0.5))
    globs.playerarray.update()

# press escape to exit play mode, delete the player quad
def escape_loop():
    while True:
        _, key, _, action, _ = yield from listen.on_key(globs.window)
        if key != glfw.KEY_ESCAPE: continue
        if action != glfw.PRESS: continue

        if len(globs.playerarray.quads) == 1:
            del globs.playerarray.quads[0]
            globs.playerarray.update()

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
            for (x,y) in globs.grid:
                if squares_intersect(Vec(x,y),playerpos + touch[key]/16):
                    found = True
                    break
            touch[key] = found # replace dict entry with boolean

        if touch["bot"]:
            # if grounded, make the vertical velocity 0
            velocity.y = 0

            # if the player is pressing up, make them jump
            if dpad.y == 1:
                velocity.y = 5
        else:
            # otherwise apply gravity
            velocity.y -= 5*dt

        # head bonk
        if touch["top"] and velocity.y > 0:
            velocity.y = 0

        # horizontal movement
        velocity.x = dpad.x*3

        # bonk on sides
        if touch["right"] and velocity.x > 0: velocity.x = 0
        if touch["left"] and velocity.x < 0: velocity.x = 0

        # compute the delta, and apply it with collision detection
        delta = velocity*dt

        # move the player. split the delta into lots of tiny nudges
        # and then apply as many as you can before we collide
        for nudge in split_delta(delta,1/16):
            any_collisions = False
            for (x,y) in globs.grid:
                if squares_intersect(Vec(x,y),playerpos+nudge.xy0):
                    any_collisions = True
                    break

            if any_collisions: break
            playerpos += nudge.xy0

        # finalize playerpos
        globs.playerarray.update()

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


# two squares of size 1x1
def squares_intersect(p1,p2):
    if p1.x + 1 <= p2.x: return False
    if p2.x + 1 <= p1.x: return False
    if p1.y + 1 <= p2.y: return False
    if p2.y + 1 <= p1.y: return False
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


