
from math import sqrt, copysign, sin, cos, pi
from swyne.node import Vector2
import globs
import pyglet

def init_physics(w):
    w.launch_listener(ball_spawning)
    w.launch_listener(frame)

def ball_spawning():
    balls = globs.balls
    key_rects = globs.key_rects
    level = globs.level
    key_sounds = globs.key_sounds

    # I dont think this needs to be global, right?
    ball_spawner = {
        "ctrl_held": False, "ctrl_frames": 0,
        "speed_min": 20, "speed_scale": 10, "speed_reset": 30,
        "angle_min": 20, "angle_limit": 240, "angle_reset": 200,
        "dia": 10, "bot_left": [key_rects["LSHIFT"]["x"], \
                key_rects["LSHIFT"]["y"]]}

    while True:
        event, *args = yield ["on_key_press", "on_key_release", "on_frame"]

        if event == "on_frame":
            if ball_spawner["ctrl_held"]:
                ball_spawner["ctrl_frames"] += 1

        else:
            symbol, modifiers = args

            # handle ball spawning
            if getattr(pyglet.window.key, "LCTRL") == symbol:
                if event == "on_key_press":
                    ball_spawner["ctrl_held"] = True
                # control was already held a little bit
                elif ball_spawner["ctrl_frames"] <= 10 or \
                        len(balls) > level["simultaneous-balls"] or \
                        len(balls) + level["dead-balls"] > level["max-balls"]:
                    key_sounds[2].play()
                else:
                    # call all params now for concise equations later
                    vp = [ball_spawner["ctrl_frames"], ball_spawner["dia"],
                    ball_spawner["speed_min"], ball_spawner["speed_scale"],
                    ball_spawner["speed_reset"], ball_spawner["angle_min"],
                    ball_spawner["angle_limit"], ball_spawner["angle_reset"]]
                    bl_corner = ball_spawner["bot_left"]
                    # calculate speed and angle of velocity, and position
                    sp = vp[3] * (vp[0] % vp[4]) + vp[2]
                    th = ((vp[0] % vp[7]) + vp[5]) * (pi / (2*vp[6]))
                    pos = [bl_corner[0] + vp[1], bl_corner[1] + vp[1]]
                    # add new ball!
                    balls.append({"pos":Vector2(pos[0], pos[1]), \
                        "vel": Vector2(sp*cos(th), sp*sin(th)),\
                        "caught": "none", "dia":vp[1], "extratime":0})
                    key_sounds[4].play()
                    # reset control key counter
                    ball_spawner["ctrl_held"] = False
                    ball_spawner["ctrl_frames"] = 0


# splits an integer translation into lots of little translations
# that add up to the provided translation.
def split_delta(delta):
    assert delta.x == int(delta.x)
    assert delta.y == int(delta.y)

    sx = copysign(1,delta.x)
    sy = copysign(1,delta.y)
    magx = abs(delta.x)
    magy = abs(delta.y)

    # deal with case where things are zero
    if delta.x == 0 and delta.y == 0: return
    if delta.x == 0:
        for i in range(magx):
            yield Vector2(0,sy)
        return
    if delta.y == 0:
        for i in range(magy):
            yield Vector2(sx,0)
        return

    y = 0
    m = magx/magy
    for x in range(1,magx+1):
        yield Vector2(sx,0)
        for i in range(int(x*m)-y):
            yield Vector2(0,sy)
        y = int(x*m)


def ball_touching_rect(center, radius, rect_pos, rect_size):
    # center, rect_pos, and rect_size are Vector2, radius is float
    # left
    if center.x + radius < rect_pos.x:
        if center.y + radius < rect_pos.y:
            #top left
            return sqrt((center.x - rect_pos.x) + \
                (center.y - rect_pos.y)**2 ) <= radius
        elif center.y - radius > rect_pos.y + rect_size.y:
            # top right
            return sqrt((center.x - rect_pos.x) + \
                (center.y - (rect_pos.y + rect_size.y))**2 ) <= radius
        else: return False # securely to the left, can't hit
    #right
    elif center.x - radius > rect_pos.x + rect_size.x:
        if center.y + radius < rect_pos.y:
            # bottom left
            return sqrt((center.x - (rect_pos.x + rect_size.x)) + \
                (center.y - rect_pos.y)**2 ) <= radius
        elif center.y - radius > rect_pos.y + rect_size.y:
            # bottom right
            return sqrt((center.x - (rect_pos.x + rect_size.x)) + \
                (center.y - rect_pos.y + rect_size.y)**2 ) <= radius
        else: return False # securely to the right
    else:
        #secturely to the top or bottom
        return False


def frame():
    balls = globs.balls
    key_rects = globs.key_rects

    level = globs.level
    keys = globs.keys
    keys_pressed = globs.keys_pressed


    while True:
        _, dt = yield "on_frame"

        for ball in balls:
            dimsx,dimsy,boty = 960,320,60

            delta = ball["vel"]*(dt + ball["extratime"])
            ball["extratime"] = (delta.x - int(delta.x))/ball["vel"].x
            delta.x = int(delta.x)
            delta.y = int(delta.y)

            pos = ball["pos"]


            for nudge in split_delta(delta):

                if True:
                    if pos.x + nudge.x > dimsx:
                        ball["vel"].x *= -1
                        break
                    if pos.x + nudge.x < 0:
                        ball["vel"].x *= -1
                        break
                    if pos.y + nudge.y > dimsy:
                        ball["vel"].y *= -1
                        break
                    if pos.y + nudge.y < boty:
                        ball["vel"].y *= -1
                        break

                pos += nudge
            ball["pos"] = pos



