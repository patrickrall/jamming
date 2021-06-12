
import numpy as np

from patpygl.vector import *
from patpygl import listen

import globs
from polygon import Polygon

def levels_init():

    globs.level_idx = 0
    globs.levels = [level1,level2]

    globs.selected_color = 0
    globs.polygons = []

    globs.polydata = {
        "unit_dx": Vec(1,0),
        "unit_dy": Vec(0,1),
        "nx": 10,
        "ny": 10,
        "origin": Vec(0,0),
        "colors":[],
    }

    # load the first level
    globs.levels[globs.level_idx]()


def next_level():
    yield from listen.wait(1)
    if globs.level_idx+1 < len(globs.levels):
        globs.polygons = []
        globs.level_idx += 1
        print("Loading level",globs.level_idx+1,"of",len(globs.levels))
        globs.levels[globs.level_idx]()
    else:
        print("Game complete!")



def level1():
    r3 = np.sqrt(3)

    globs.polydata["unit_dx"] = Vec(1,0)
    globs.polydata["unit_dy"] = Vec(0,1)

    globs.polydata["origin"] = Vec(-0.3,-1.2)
    globs.polydata["nx"] = 10
    globs.polydata["ny"] = 10

    cs = []
    cs.append(Vec(1.0, 0.0, 1.0))
    cs.append(Vec(0.0, 1.0, 1.0))
    globs.polydata["colors"] = cs

    t1 = Polygon(cs[0],[Vec(0,0), Vec(0,1), Vec(1,0)])
    t2 = Polygon(cs[1],[Vec(1,1), Vec(0,1), Vec(1,0)])

    globs.polygons = [t1,t2]
    t1.neighbors = [t2]
    t2.neighbors = [t1]





def level2():
    r3 = np.sqrt(3)

    globs.polydata["unit_dx"] = Vec(1+r3,0)
    globs.polydata["unit_dy"] = Vec(0,1+r3)

    globs.polydata["origin"] = Vec(-0.3,-1.2)
    globs.polydata["nx"] = 4
    globs.polydata["ny"] = 4


    cs = []
    cs.append(Vec(1.0, 0.0, 1.0))
    cs.append(Vec(0.0, 1.0, 1.0))
    cs.append(Vec(0.5, 0.5, 1.0))
    globs.polydata["colors"] = cs

    t1 = Polygon(cs[0],[Vec(0,0), Vec(0,1), Vec(r3/2,0.5)])

    t2 = Polygon(cs[0],[Vec(r3/2,0.5), Vec(1+r3/2,0.5), Vec(0.5+r3/2,0.5-r3/2)])

    t3 = Polygon(cs[1],[Vec(r3/2,0.5), Vec(1+r3/2,0.5), Vec(0.5+r3/2,0.5+r3/2)])

    t4 = Polygon(cs[1],[ Vec(1+r3/2,0.5),  Vec(1+r3,0.0),Vec(1+r3,1.0)])

    delta1 = Vec(r3/2,0.5) - Vec(0,1)
    delta2 = Vec(0.5,1+r3/2) - Vec(0,1)
    s5 = Polygon(cs[2],[Vec(0,1) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    s6 = Polygon(cs[2],[Vec(0.5+r3/2,1.5+r3/2) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    t7 = Polygon(cs[0],[Vec(0,1), Vec(0.5,1+r3/2), Vec(-0.5,1+r3/2)])

    t8 = Polygon(cs[1],[Vec(0,1+r3), Vec(0.5,1+r3/2), Vec(-0.5,1+r3/2)])

    t9 = Polygon(cs[1],[Vec(0.5,1+r3/2), Vec(0.5+r3/2,1+r3/2+0.5), Vec(0.5+r3/2,1+r3/2-0.5)])

    t10 = Polygon(cs[0],[Vec(0.5+r3,1+r3/2), Vec(0.5+r3/2,1+r3/2+0.5), Vec(0.5+r3/2,1+r3/2-0.5)])

    delta1 = Vec(delta1.x,-delta1.y)
    delta2 = Vec(-delta2.x,delta2.y)
    s11 = Polygon(cs[2],[Vec(1+r3/2,0.5) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    s12 = Polygon(cs[2],[Vec(0.5,1+r3/2) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    globs.polygons = [t1,t2,t3,t4,s5,s6,t7,t8,t9,t10,s11,s12]

    t1.neighbors = [t4,s5,s12]
    t2.neighbors = [t3,s12,s6]
    t3.neighbors = [t2,s5,s11]
    t4.neighbors = [t1,s6,s11]
    s5.neighbors = [t1,t7,t3,t9]
    s6.neighbors = [t10,t8,t2,t4]
    t7.neighbors = [s5,s11,t8]
    t8.neighbors = [s6,s12,t7]
    t9.neighbors = [s5,s12,t10]
    t10.neighbors = [s11,s6,t9]
    s11.neighbors = [t3,t4,t10,t7]
    s12.neighbors = [t8,t9,t2,t1]

