import glfw
import json, os

from patpygl import listen
from patpygl.quadarray import *

import globs


def edit_init():
    globs.mode = "grid_edit"
    listen.launch(grid_editor_loop())

# listen for clicks on the triangle grid
def grid_editor_loop():

    while True:
        events = yield from listen.any(
                enter=listen.on_cursor_enter(globs.window),
                pos=listen.on_cursor_pos(globs.window),
                scroll=listen.on_scroll(globs.window),
                button=listen.on_mouse_button(globs.window)
                )

        if globs.mode != "grid_edit": continue

        if "button" in events:
            _, button, action, mods = events["button"]
            # left click
            if (button == glfw.MOUSE_BUTTON_LEFT and\
                    action == glfw.PRESS):
                x,y = glfw.get_cursor_pos(globs.window)
                i, j, isUpper = position_to_grid_index(x, y)
                p1, p2, p3 = position_to_triangle_points(x, y)
                #print(p1, p2, p3)
                #print(i, j, isUpper)
                # click on a grid tile: make that tile the cursor tile
                if p1.x + p1.y > 0:
                    poly_i = get_polygon_index(p1, p2, p3, isUpper)
                    #print("clicked polygon at index=", poly_i)
                    #poly_p1, poly_p2, poly_p3 = globs.polygons[poly_i].get_points()
                    #print("polygon at index=", poly_i, " at points ", poly_p1, poly_p2, poly_p3)
                    if poly_i > -1:
                        globs.numberClicksThisLevel += 1 # related to score
                        globs.tri["updatedNeighbors"] = [] # reset color change tally
                        change_polygon_color_cascade(poly_i)
                        increment_color_index()

# change the color of this polygon and any polygons who share edges and have the same color
def change_polygon_color_cascade(poly_i):
    globs.tri["updatedNeighbors"].append(poly_i) # mark this triangle as updated
    oldColor = globs.polygons[poly_i].get_color()
    newColor = globs.colors[globs.colorIndex]
    # update the clicked triangle
    globs.polygons[poly_i].set_color(newColor)
    points = globs.polygons[poly_i].get_points()
    neighbors_i = get_neighbors_from_centroid(points[0], points[1], points[2]) # assumes equilateral triangles
    #print(neighbors_i)
    for k in neighbors_i:
        if k == poly_i or k in globs.tri["updatedNeighbors"]:
            continue # skip triangles that have already been updated
        neighborColor = globs.polygons[k].get_color()
        if (neighborColor.x != oldColor.x or neighborColor.y != oldColor.y or neighborColor.z != oldColor.z):
            continue
        else:
            change_polygon_color_cascade(k)
            #print("Changing color of neighbor at index=", k)

def increment_color_index():
    globs.colorIndex += 1
    if globs.colorIndex >= len(globs.colors):
        globs.colorIndex = 0

def get_polygon_index(p1, p2, p3, isUpper):
    for k in range(0, globs.tri["i_max"] * globs.tri["j_max"] * 2):
        points = globs.polygons[k].get_points()
        diffX = p1.x - points[0].x + p2.x - points[1].x + p3.x - points[2].x
        diffY = p1.y - points[0].y + p2.y - points[1].y + p3.y - points[2].y
        if abs(diffX) < .1 and abs(diffY) < .1:
            return k
    print("No polygon found")
    return -1

def get_neighbors_from_centroid(p1, p2, p3):
    # warning: assumes all polygons are equilateral triangles with the same edge length
    limit = globs.tri["scaleX"] * 2 # a rough measurement of how close a neihgbor's centroid must be to qualify as a neighbor
    neighbors = []
    centroid = Vec((p1.x + p2.x + p3.x)/3, (p1.y + p2.y + p3.y)/3)
    for k in range(0, len(globs.polygons)):
        points = globs.polygons[k].get_points()
        n_centroid = Vec((points[0].x + points[1].x + points[2].x)/3, (points[0].y + points[1].y + points[2].y)/3)
        if abs(centroid.x - n_centroid.x) + abs(centroid.y - n_centroid.y) < limit:
            neighbors.append(k)
    return neighbors

# which side of the line segment is a point on
def sign ( p1,  p2,  p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

# determine if the point pt within the triangle formed by points v1, v2 and v3
def is_point_in_triangle( pt,  v1,  v2,  v3):
    d1 = sign(pt, v1, v2)
    d2 = sign(pt, v2, v3)
    d3 = sign(pt, v3, v1)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)

# get the indices and orientation of the triangle given an x, y position
def position_to_grid_index(x, mouse_y):
    y = globs.h - mouse_y
    j = int((y - globs.tri["offsetY"])/(2 * globs.tri["scaleY"])) # row
    for i in range(0, globs.tri["i_max"]): # examine all the triangles in the row
        p1, p2, p3 = grid_index_to_position(i, j, True)
        if is_point_in_triangle(Vec(x, y), p1, p2, p3):
            return i, j, True
        p1, p2, p3 = grid_index_to_position(i, j, False)
        if is_point_in_triangle(Vec(x, y), p1, p2, p3):
            return i, j, False
    return -1, -1, False

# get the indices and orientation of the triangle given an x, y position
def position_to_triangle_points(x, mouse_y):
    y = globs.h - mouse_y
    j = int((y - globs.tri["offsetY"])/(2 * globs.tri["scaleY"])) # row
    for i in range(0, 7): # examine all the triangles in the row
        p1, p2, p3 = grid_index_to_position(i, j, True)
        if is_point_in_triangle(Vec(x, y), p1, p2, p3):
            return p1, p2, p3
        p1, p2, p3 = grid_index_to_position(i, j, False)
        if is_point_in_triangle(Vec(x, y), p1, p2, p3):
            return p1, p2, p3
    return Vec(0,0), Vec(0,0), Vec(0,0)

# determine if this row is staggered (downward pointing triange is the leftmost) or not (upward point triangle is the leftmost)
def is_staggered(i,j):
    return (j % 2 == 1)

# determine if this row is staggered based on the triangle points
def is_staggered_from_points(p1, p2, p3):
    avg_y = (p1.y + p2.y + p3.y)/3
    j = (avg_y - globs.tri["offsetY"])/globs.tri["scaleY"]/2 # row
    return is_staggered(-1, j)

# determine what the triangle points are for a triangle at the given indices
def grid_index_to_position(i, j, isPointingUp):
    offsetX = globs.tri["offsetX"]
    offsetY = globs.tri["offsetY"]
    scaleX = globs.tri["scaleX"]
    scaleY = globs.tri["scaleY"]
    if is_staggered(i, j):
        if isPointingUp:
            return  Vec(offsetX + (3 + 2 * i) * scaleX, offsetY + 2 * scaleY * j, 0),\
                    Vec(offsetX + (2 + 2 * i) * scaleX, offsetY + 2 * scaleY + 2 * scaleY * j, 0),\
                    Vec(offsetX + (1 + 2 * i) * scaleX, offsetY + 2 * scaleY * j, 0)
        else:
            return  Vec(offsetX + (1 + 2 * i) * scaleX, offsetY + 2 * scaleY * j, 0),\
                    Vec(offsetX + (2 + 2 * i) * scaleX, offsetY + 2 * scaleY + 2 * scaleY * j, 0),\
                    Vec(offsetX + (0 + 2 * i) * scaleX, offsetY + 2 * scaleY + 2 * scaleY * j, 0)
    else:
        if isPointingUp:
            return  Vec(offsetX + (2 + 2 * i) * scaleX, offsetY + 2 * scaleY * j, 0),\
                    Vec(offsetX + (1 + 2 * i) * scaleX, offsetY + 2 * scaleY + 2 * scaleY * j, 0),\
                    Vec(offsetX + 2 * scaleX * i,       offsetY + 2 * scaleY * j, 0)
        else:
            return Vec(offsetX + (2 + 2 * i) * scaleX, offsetY + 2 * scaleY * j, 0), \
                   Vec(offsetX + (3 + 2 * i) * scaleX, offsetY + 2 * scaleY + 2 * scaleY * j, 0),\
                   Vec(offsetX + (1 + 2 * i) * scaleX, offsetY + 2 * scaleY + 2 * scaleY * j, 0)
