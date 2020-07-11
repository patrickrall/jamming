
from math import sqrt, copysign, sin, cos, pi
from swyne.node import Vector2
import globs
import pyglet

from pyglet.gl import *

def init_physics(w):
    w.launch_listener(ball_spawning)
    w.launch_listener(frame)


def circle_intersect_rect(cpos,cr,rpos,rdims):

    # center is inside rectangle
    if rpos.x < cpos.x and cpos.x < rpos.x + rdims.x and\
        rpos.y < cpos.y and cpos.y < rpos.y + rdims.y: return True

    # center is too far from rectangle (quick escapes to avoid complex math)
    if True:
        if cpos.x + cr*1.5 < rpos.x: return False
        if cpos.y + cr*1.5 < rpos.y: return False
        if rpos.x < rpos.x - cr*1.5 : return False
        if rpos.y < rpos.y - cr*1.5 : return False

    def intersect_line_segment_x(x1,x2,y0):
        # x = (1-t) * x1 + t * x2
        # (x - cpos.x)**2 + (y0 - cpos.y)**2 = cr**2

        if cr**2 - (y0 - cpos.y)**2 < 0: return False

        t1 = (sqrt(cr**2 - (y0 - cpos.y)**2) + cpos.x - x1)/ (x2 - x1)
        t2 = (-sqrt(cr**2 - (y0 - cpos.y)**2) + cpos.x - x1)/ (x2 - x1)

        if 0 <= t1 <= 1: return True
        if 0 <= t2 <= 1: return True
        return False


    def intersect_line_segment_y(y1,y2,x0):
        # y = (1-t) * y1 + t * y2
        # (y - cpos.y)**2 + (x0 - cpos.x)**2 = cr**2

        if cr**2 - (x0 - cpos.x)**2 < 0: return False

        t1 = (sqrt(cr**2 - (x0 - cpos.x)**2) + cpos.y - y1)/ (y2 - y1)
        t2 = (-sqrt(cr**2 - (x0 - cpos.x)**2) + cpos.y - y1)/ (y2 - y1)

        if 0 <= t1 <= 1: return True
        if 0 <= t2 <= 1: return True
        return False


    if intersect_line_segment_x(rpos.x, rpos.x+rdims.x, rpos.y): return True
    if intersect_line_segment_x(rpos.x, rpos.x+rdims.x, rpos.y+rdims.y): return True

    if intersect_line_segment_y(rpos.y, rpos.y+rdims.y, rpos.x): return True
    if intersect_line_segment_y(rpos.y, rpos.y+rdims.y, rpos.x+rdims.x): return True

    return False


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
        for i in range(magy):
            yield Vector2(0,sy)
        return
    if delta.y == 0:
        for i in range(magx):
            yield Vector2(sx,0)
        return

    y = 0
    m = magx/magy
    for x in range(1,magx+1):
        yield Vector2(sx,0)
        for i in range(int(x*m)-y):
            yield Vector2(0,sy)
        y = int(x*m)


def frame():
    balls = globs.balls
    key_rects = globs.key_rects

    keys = globs.keys
    keys_pressed = globs.keys_pressed

    trapped_balls = globs.trapped_balls
    ctrl_rect = globs.ctrl_rect

    while True:
        _, dt = yield "on_frame"
        level = globs.level

        dimsx,dimsy,boty = 960,320,60


        for ball in trapped_balls:

            delta = ball["vel"]*dt

            delta.x = int(delta.x)
            delta.y = int(delta.y)

            for nudge in split_delta(delta):
                pos = ball["pos"]

                r = ball["dia"]/2

                if pos.x + r + nudge.x > ctrl_rect["x"]+ctrl_rect["w"]:
                    ball["vel"].x *= -1
                    break
                if pos.x - r + nudge.x < ctrl_rect["x"]:
                    ball["vel"].x *= -1
                    break
                if pos.y + r + nudge.y > ctrl_rect["y"]+ctrl_rect["h"]:
                    ball["vel"].y *= -1
                    break
                if pos.y - r + nudge.y < ctrl_rect["y"]:
                    ball["vel"].y *= -1
                    break

                ball["pos"] += nudge


        dimsx,dimsy,boty = 960,320,60

        dead_balls = []
        for ball in balls:


            delta = ball["vel"]*dt
            delta.x = int(delta.x)
            delta.y = int(delta.y)
            radius = ball["dia"]/2

            for nudge in split_delta(delta):
                pos = ball["pos"]

                if True:
                    # check against walls of level
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


                if True:
                    # check against rectangles
                    anyCollide = False

                    for key in keys:

                        if key in level: kind = level[key]
                        else: kind = level["default"]
                        if keys_pressed[key] and len(kind) > 1: kind = kind[1]
                        else: kind = kind[0]

                        if kind == "none": continue

                        rect = key_rects[key]
                        rpos = Vector2(rect["x"],rect["y"])
                        rdims = Vector2(rect["w"],rect["h"])

                        r = ball["dia"]/2

                        if circle_intersect_rect(pos+nudge, r, rpos, rdims):

                            if kind == "hazard":
                                if ball not in dead_balls:
                                    dead_balls.append(ball)
                                continue

                            if kind == "goal":
                                globs.next_level()

                            if kind in ["wall", "goal"]:
                                if (nudge.x == 0): ball["vel"].y *= -1
                                if (nudge.y == 0): ball["vel"].x *= -1

                                ball["vel"].x = int(ball["vel"].x)
                                ball["vel"].y = int(ball["vel"].y)
                            anyCollide = True
                            break
                    if anyCollide:
                        break
                ball["pos"] += nudge


        for dead_ball in dead_balls:
            level["dead-balls"].append(balls.remove(dead_ball))
        dead_ball_indices = []


def ball_spawning():
    balls = globs.balls
    key_rects = globs.key_rects
    level = globs.level
    key_sounds = globs.key_sounds
    trapped_balls = globs.trapped_balls
    launch_sounds = globs.launch_sounds

    # I dont think this needs to be global, right?
    ball_spawner = {
        "ctrl_held": False, "ctrl_frames": 0,
        "speed_min": 60, "speed_scale": 10, "speed_reset": 30,
        "angle_min": 20, "angle_limit": 240, "angle_reset": 200,
        "dia": 28, "bot_left": [key_rects["LSHIFT"]["x"], \
            key_rects["LSHIFT"]["y"], key_rects["LSHIFT"]["w"]]}

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
                        len(balls) >= level["simultaneous-balls"] or \
                        len(balls) + len(level["dead-balls"]) > level["max-balls"]:
                    launch_sounds[1].play()
                else:
                    # call all params now for concise equations later
                    vp = [ball_spawner["ctrl_frames"], ball_spawner["dia"],
                    ball_spawner["speed_min"], ball_spawner["speed_scale"],
                    ball_spawner["speed_reset"], ball_spawner["angle_min"],
                    ball_spawner["angle_limit"], ball_spawner["angle_reset"]]
                    bl_corner = ball_spawner["bot_left"]
                    # calculate speed and angle of velocity, and position
                    sp = 200
                    th = pi/6
                    pos = [bl_corner[0] + bl_corner[2]/2, bl_corner[1]]
                    # add new ball!
                    balls.append({"pos":Vector2(pos[0], pos[1]), \
                        "vel": Vector2(sp*cos(th), sp*sin(th)),\
                        "caught": "none", "dia":vp[1], "extratime":0})
                    #print(balls[-1]["vel"])
                    launch_sounds[0].play()
                    # reset control key counter
                    ball_spawner["ctrl_held"] = False
                    ball_spawner["ctrl_frames"] = 0
                    trapped_balls.pop()


