import glfw

from patpygl import listen
from patpygl.vector import *

import globs
from levels import next_level

def play_init():
    listen.launch(play_loop())

def play_loop():

    while True:
        _, button, action, mods = yield from listen.on_mouse_button(globs.window)


        if button != glfw.MOUSE_BUTTON_LEFT: continue
        if action != glfw.PRESS: continue

        x,y = glfw.get_cursor_pos(globs.window)
        pt = mouse_coords(x, y)


        found = None
        for x in range(globs.polydata["nx"]):
            if found: break
            for y in range(globs.polydata["ny"]):
                delta = globs.polydata["origin"].xy
                delta += x*globs.polydata["unit_dx"]
                delta += y*globs.polydata["unit_dy"]
                for polygon in globs.polygons:
                    if is_point_in_poly(pt-delta, polygon):
                        found = polygon
                        break

        polygons_to_update = [found]
        while True:
            done = True
            for polygon in polygons_to_update:
                for neighbor in polygon.neighbors:
                    if neighbor in polygons_to_update: continue
                    if polygon.color == neighbor.color:
                        polygons_to_update.append(neighbor)
                        done = False
            if done: break

        # update the polygons
        for polygon in polygons_to_update:
            polygon.color = globs.polydata["colors"][globs.selected_color]

        # check if all the colors on the map are the same
        done = True
        for polygon in globs.polygons:
            if polygon.color != globs.polydata["colors"][globs.selected_color]:
                done = False
                break

        if done:
            print("Level complete!")
            listen.launch(next_level())

        else:
            globs.selected_color += 1
            globs.selected_color %= len(globs.polydata["colors"])





##########################################################################3

# given x,y in pixels on screen, output point in game coordinates
def mouse_coords(x, y):
    x = 2 * x / globs.cam["w"] - 1
    y = -(2 * y / globs.cam["h"] - 1)
    s = Vec(x, y, 1, 1)

    m = globs.cam["projection-inv"]
    s @= m
    s = s.xy / s.w

    return s


def is_point_in_poly(pt, poly):
    for i in range(len(poly.points)-2):
        if is_point_in_triangle(pt, poly.points[0], poly.points[1+i], poly.points[2+i]):
            return True
    return False


def is_point_in_triangle(pt, v1, v2, v3):
    d1 = sign(pt, v1, v2)
    d2 = sign(pt, v2, v3)
    d3 = sign(pt, v3, v1)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)

def sign(p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)
