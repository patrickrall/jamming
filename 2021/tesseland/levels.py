
import numpy as np

from patpygl.vector import *
from patpygl import listen

import globs
from polygon import Polygon
from hud import update_hud

def levels_init():
    globs.play_disabled = True

    globs.selected_color = 0
    globs.bgcolor = Vec(1.0,1.0,0)

    globs.polydata = {
        "unit_dx": Vec(1,0),
        "unit_dy": Vec(0,1),
        "nx": 10,
        "ny": 10,
        "origin": Vec(0,0),
        "colors":[],
    }

    globs.level_idx = -1
    globs.levels = [level4]

    globs.polygons = []

    # load the first level
    listen.launch(next_level())

def next_level():
    globs.play_disabled = True
    yield from listen.wait(0.1)
    if globs.level_idx+1 < len(globs.levels):
        globs.selected_color = 0

        globs.level_idx += 1
        print("Loading level",globs.level_idx+1,"of",len(globs.levels))

        polys = globs.levels[globs.level_idx]()

        np.random.shuffle(polys)
        globs.polygons = []
        for poly in polys:
            yield from listen.wait(0.03)
            globs.polygons.append(poly)
        globs.play_disabled = False

        update_hud()
    else:
        print("Game complete!")


def repeat_cell(repeat_x, repeat_y, unit_dx, unit_dy, polys):
    globs.polydata["unit_dx"] = unit_dx * repeat_x
    globs.polydata["unit_dy"] = unit_dy * repeat_y

    out = {}
    out_list = []

    for rx in range(repeat_x):
        for ry in range(repeat_y):
            out[rx,ry] = {}
            delta = rx * unit_dx + ry * unit_dy
            for key in polys.keys():
                new_points = [delta + v for v in polys[key].points]
                out[rx,ry][key] = Polygon(polys[key].color, new_points)
                out_list.append(out[rx,ry][key])


    for rx in range(repeat_x):
        for ry in range(repeat_y):
            for key in polys.keys():
                for dx,dy,nkey in polys[key].neighbors:
                    nx,ny = rx+dx,ry+dy
                    if nx < 0: nx += repeat_x
                    if nx >= repeat_x: nx -= repeat_x
                    if ny < 0: ny += repeat_y
                    if ny >= repeat_y: ny -= repeat_y

                    neighbor = out[nx,ny][nkey]
                    out[rx,ry][key].neighbors.append(neighbor)

    return out_list


def level1():
    globs.polydata["origin"] = Vec(-0.3,-1.2)
    globs.polydata["nx"] = 2
    globs.polydata["ny"] = 2

    cs = []
    cs.append(Vec(1.0, 0.0, 1.0))
    cs.append(Vec(0.0, 1.0, 1.0))
    globs.polydata["colors"] = cs

    polys = {}

    polys["t1"] = Polygon(cs[0],[Vec(0,0), Vec(0,1), Vec(1,0)])
    polys["t2"] = Polygon(cs[1],[Vec(1,1), Vec(0,1), Vec(1,0)])

    polys["t1"].neighbors = [(0,0,"t2"),(-1,0,"t2"),(0,-1,"t2")]
    polys["t2"].neighbors = [(0,0,"t1"),(1,0,"t1"),(0,1,"t1")]

    return repeat_cell(5, 5, Vec(1,0), Vec(0,1), polys)


def level2():
    globs.polydata["origin"] = Vec(-0.3,-1.2)
    globs.polydata["nx"] = 2
    globs.polydata["ny"] = 2

    cs = []
    cs.append(Vec(1.0, 0.0, 1.0))
    cs.append(Vec(0.0, 1.0, 1.0))
    cs.append(Vec(0.5, 0.5, 1.0))
    globs.polydata["colors"] = cs

    r3 = np.sqrt(3)

    polys = {}

    polys["t1"] = Polygon(cs[0],[Vec(0,0), Vec(0,1), Vec(r3/2,0.5)])

    polys["t2"] = Polygon(cs[0],[Vec(r3/2,0.5), Vec(1+r3/2,0.5), Vec(0.5+r3/2,0.5-r3/2)])

    polys["t3"] = Polygon(cs[1],[Vec(r3/2,0.5), Vec(1+r3/2,0.5), Vec(0.5+r3/2,0.5+r3/2)])

    polys["t4"] = Polygon(cs[1],[ Vec(1+r3/2,0.5),  Vec(1+r3,0.0),Vec(1+r3,1.0)])

    delta1 = Vec(r3/2,0.5) - Vec(0,1)
    delta2 = Vec(0.5,1+r3/2) - Vec(0,1)
    polys["s5"] = Polygon(cs[2],[Vec(0,1) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    polys["s6"] = Polygon(cs[2],[Vec(0.5+r3/2,1.5+r3/2) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    polys["t7"] = Polygon(cs[0],[Vec(0,1), Vec(0.5,1+r3/2), Vec(-0.5,1+r3/2)])

    polys["t8"] = Polygon(cs[1],[Vec(0,1+r3), Vec(0.5,1+r3/2), Vec(-0.5,1+r3/2)])

    polys["t9"] = Polygon(cs[1],[Vec(0.5,1+r3/2), Vec(0.5+r3/2,1+r3/2+0.5), Vec(0.5+r3/2,1+r3/2-0.5)])

    polys["t10"] = Polygon(cs[0],[Vec(0.5+r3,1+r3/2), Vec(0.5+r3/2,1+r3/2+0.5), Vec(0.5+r3/2,1+r3/2-0.5)])

    delta1 = Vec(delta1.x,-delta1.y)
    delta2 = Vec(-delta2.x,delta2.y)
    polys["s11"] = Polygon(cs[2],[Vec(1+r3/2,0.5) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    polys["s12"] = Polygon(cs[2],[Vec(0.5,1+r3/2) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])


    polys["t1"].neighbors = [(-1,0,"t4"),(0,0,"s5"),(0,-1,"s12")]
    polys["t2"].neighbors = [(0,0,"t3"),(0,-1,"s12"),(0,-1,"s6")]
    polys["t3"].neighbors = [(0,0,"t2"),(0,0,"s6"),(0,0,"s11")]
    polys["t4"].neighbors = [(1,0,"t1"),(0,-1,"s6"),(0,0,"s11")]
    polys["s5"].neighbors = [(0,0,"t1"),(0,0,"t7"),(0,0,"t3"),(0,0,"t9")]
    polys["s6"].neighbors = [(0,0,"t10"),(1,0,"t8"),(0,1,"t2"),(0,1,"t4")]
    polys["t7"].neighbors = [(0,0,"s5"),(-1,0,"s11"),(0,0,"t8")]
    polys["t8"].neighbors = [(-1,0,"s6"),(0,0,"s12"),(0,0,"t7")]
    polys["t9"].neighbors = [(0,0,"s5"),(0,0,"s12"),(0,0,"t10")]
    polys["t10"].neighbors = [(0,0,"s11"),(0,0,"s6"),(0,0,"t9")]
    polys["s11"].neighbors = [(0,0,"t3"),(0,0,"t4"),(0,0,"t10"),(1,0,"t7")]
    polys["s12"].neighbors = [(0,0,"t8"),(0,0,"t9"),(0,1,"t2"),(0,1,"t1")]

    return repeat_cell(2, 2, Vec(1+r3,0), Vec(0,1+r3), polys)

def level4():
    r3 = np.sqrt(3)
    globs.polydata["origin"] = Vec(0,0)
    globs.polydata["nx"] = 1
    globs.polydata["ny"] = 1

    cs = []
    cs.append(Vec(1.0, 0.0, 1.0)) # yellow
    cs.append(Vec(0.0, 1.0, 1.0)) # pink
    cs.append(Vec(1.0, 1.0, 0.0)) # cyan
    cs.append(Vec(0.0, 0.0, 1.0)) # red
    globs.polydata["colors"] = cs

    polys = {}

    delta1 = Vec(r3/2,0.5) - Vec(0,1)
    delta2 = Vec(-delta1.y, delta1.x)
    polys["s1"] = Polygon(cs[0],[Vec(0,1) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])


    delta1 = Vec(delta1.x,-delta1.y)
    delta2 = Vec(delta2.x,-delta2.y)
    polys["s2"] = Polygon(cs[0],[Vec(0,2+r3) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    delta1 = Vec(1,0)
    delta2 = Vec(0,1)
    polys["s3"] = Polygon(cs[0],[Vec(0.5+r3,1+r3/2) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    # lolwut no 4

    polys["d5"] = Polygon(cs[3],[Vec(r3/2 + 0.5, 2.5+r3/2), Vec(r3/2, 2.5+r3), Vec(r3/2, 3.5+r3),
                                 Vec(r3/2+0.5, 3.5+1.5*r3), Vec(r3+0.5, 4+1.5*r3), Vec(r3+1.5, 4+1.5*r3),
                                 Vec(r3*1.5+1.5, 3.5+1.5*r3),Vec(r3*1.5+2, 3.5+r3),Vec(r3*1.5+2, 2.5+r3),
                                 Vec(r3*1.5+1.5, 2.5+r3/2), Vec(r3+1.5, 2+r3/2), Vec(r3+0.5, 2+r3/2),])


    polys["t6"] = Polygon(cs[2],[Vec(0,0), Vec(0,1), Vec(r3/2,0.5)])


    #polys["t1"].neighbors = [(0,0,"t2"),(-1,0,"t2"),(0,-1,"t2")]
    #polys["t2"].neighbors = [(0,0,"t1"),(1,0,"t1"),(0,1,"t1")]

    return repeat_cell(2, 2, Vec(1.5*r3 + 1.5, 1.5+r3/2), Vec(0,r3+3), polys)
