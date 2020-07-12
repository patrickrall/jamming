
from math import sqrt, copysign, sin, cos, pi, degrees, radians
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

    sx = int(copysign(1,delta.x))
    sy = int(copysign(1,delta.y))
    magx = int(abs(delta.x))
    magy = int(abs(delta.y))

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
    m = magy/magx
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
    dead_beachball_sprites = globs.dead_beachball_sprites
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

        balls_to_kill = [[],[],[]]
        for n, ball in enumerate(balls):

            s = level["speed"]

            # gravity
            for key in keys:

                if key in level: kind = level[key]
                else: kind = level["default"]
                if keys_pressed[key] and len(kind) > 1: kind = kind[1]
                else: kind = kind[0]

                if kind != "gravity-on": continue

                rect = key_rects[key]
                x,y = rect["x"] + rect["w"]/2, rect["y"]+rect["h"]/2

                dv = Vector2(x,y) - ball["pos"]
                d2 = dv.x*dv.x + dv.y*dv.y

                mind = 10
                if d2 < mind: d2 = mind

                G = 1e3
                dv = dv * (G / sqrt(d2)) * dt

                ball["vel"] += dv

            current_v = sqrt(ball["vel"].x*ball["vel"].x + ball["vel"].y*ball["vel"].y)

            ball["vel"] = ball["vel"] * (s / current_v)

            ball["vel"].x = round(ball["vel"].x)
            ball["vel"].y = round(ball["vel"].y)

            # slowness
            v = Vector2(ball["vel"].x, ball["vel"].y)
            for key in keys:

                if key in level: kind = level[key]
                else: kind = level["default"]
                if keys_pressed[key] and len(kind) > 1: kind = kind[1]
                else: kind = kind[0]

                if kind != "soda": continue

                rect = key_rects[key]
                rpos = Vector2(rect["x"],rect["y"])
                rdims = Vector2(rect["w"],rect["h"])

                r = ball["dia"]/2

                if circle_intersect_rect(ball["pos"], r, rpos, rdims):
                    v = v*0.5
                    v.x = int(v.x)
                    v.y = int(v.y)

                    break

            delta = v*dt
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
                                if n not in balls_to_kill[1]:
                                    balls_to_kill[0].append(ball)
                                    balls_to_kill[1].append(n)
                                    balls_to_kill[2].append(rpos + rdims*0.5)
                                continue

                            if kind in ["wall", "goal", "goal-nomoth"]:
                                if (nudge.x == 0): ball["vel"].y *= -1
                                if (nudge.y == 0): ball["vel"].x *= -1

                                ball["vel"].x = int(ball["vel"].x)
                                ball["vel"].y = int(ball["vel"].y)

                                anyCollide = True

                            if kind == "goal":
                                globs.launch_moth(key)

                            if anyCollide:
                                break

                    if anyCollide:
                        break
                ball["pos"] += nudge

        dead_balls = globs.dead_balls
        for i in range(len(balls_to_kill[1])):
            dead_ball = balls_to_kill[1][i]
            level["dead-balls"]+= 1
            dead_balls.append(balls.pop(dead_ball))
            dead_balls[-1]["target"] = balls_to_kill[2][i]
        balls_to_kill = []

        moths = globs.moths
        moths_to_delete = []
        for moth in moths:
            delta = moth.velocity * dt * 3
            moth.x += delta.x
            moth.y += delta.y

            tol = 50
            if moth.x > dimsx + tol or moth.x < -tol or\
                    moth.y > dimsy + tol or moth.y < -tol:
                moths_to_delete.append(moth)

        for moth in moths_to_delete:
            moths.remove(moth)

        if len(moths) == 0:
            any_moths = False
            for key in keys:
                if key not in level: continue
                if level[key][0] == "goal":
                    any_moths = True
                    break
            if not any_moths:
                globs.next_level()

        dead_beachball_sprites = globs.dead_beachball_sprites
        for sprite in dead_beachball_sprites:
            delta = sprite.target - Vector2(sprite.x, sprite.y)
            if delta.x != 0 or delta.y != 0:
                delta = delta * (1/sqrt(delta.x*delta.x + delta.y*delta.y)) * dt * 100

            sprite.x += int(delta.x)
            sprite.y += int(delta.y)


def ball_spawning():
    balls = globs.balls
    key_rects = globs.key_rects
    level = globs.level
    launcher_state = globs.launcher_state
    key_sounds = globs.key_sounds
    trapped_balls = globs.trapped_balls
    launch_sounds = globs.launch_sounds
    ctrl_rect = globs.ctrl_rect

    import math
    import random

    # I dont think this needs to be global, right?
    ball_diameter = 28
    bl_corner = [key_rects["LSHIFT"]["x"], key_rects["LSHIFT"]["y"], \
                                    key_rects["LSHIFT"]["w"]]

    while True:
        event, *args = yield ["on_key_press", "on_key_release", "on_frame"]

        if event == "on_frame":
            if launcher_state[0]:
                launcher_state[1] += 1

        elif globs.menuActive == 0:
            symbol, modifiers = args

            # handle ball spawning
            if getattr(pyglet.window.key, "LCTRL") == symbol:
                if event == "on_key_press":
                    launcher_state[0] = True
                # control was already held a little bit
                elif launcher_state[1] <= 30 or \
                        len(balls) >= level["simultaneous-balls"]:
                    launch_sounds[1].play()
                else:
                    if len(trapped_balls) <= 1:
                        while len(trapped_balls) < level["max-balls"]:
                            r = ball_diameter/2.
                            v, th = random.uniform(50,100), random.uniform(0, math.pi*2)
                            x = random.uniform(ctrl_rect["x"]+r, ctrl_rect["x"]+ctrl_rect["w"]-r)
                            y = random.uniform(ctrl_rect["y"]+r, ctrl_rect["y"]+ctrl_rect["h"]-r)
                            trapped_balls.append({"pos":Vector2(x,y),
                                "vel": Vector2(v*math.cos(th), v*math.sin(th)),
                                "dia": r, "caught": "none", "extratime": 0})


                    # calculate speed and angle of velocity, and position
                    if "speed" in level: sp = level["speed"]
                    elif "speed-min" in level and "speed-max" in level:
                        sp = random.uniform(level["speed-min"], level["speed-max"])
                        level["speed"] = sp
                    else: level["speed"], sp = 250, 250

                    if "angle" in level: th = radians(level["angle"])
                    elif "angle-min" in level and "angle-max" in level:
                        th = radians(random.uniform(level["angle-min"], level["angle-max"]))
                    else: th = radians(45)

                    pos = [bl_corner[0] + bl_corner[2]/2, bl_corner[1]]
                    vx, vy = sp*sin(th), sp*cos(th)

                    # add new ball!
                    balls.append({"pos":Vector2(pos[0], pos[1]), \
                        "vel": Vector2(vx, vy), "caught": "none",
                        "dia":ball_diameter, "extratime":0})
                    #print("%f deg, %f x, %f y, %d frames" % \
                    #    (degrees(th), vx, vy, launcher_state[1]))
                    #print(balls[-1]["vel"])
                    launch_sounds[0].play()
                    # reset control key counter
                    launcher_state[0] = False
                    launcher_state[1] = 0
                    trapped_balls.pop()


