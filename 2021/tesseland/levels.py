
import numpy as np

from patpygl.vector import *
from patpygl import listen

import globs
from polygon import Polygon

def levels_init():
    globs.play_disabled = True

    globs.selected_color = 0
    globs.bgcolor = Vec(0.0,0.0,0)

    globs.polydata = {
        "unit_dx": Vec(1,0),
        "unit_dy": Vec(0,1),
        "nx": 10,
        "ny": 10,
        "origin": Vec(0,0),
        "colors":[],
    }

    globs.level_idx = -1
    globs.levels = [level1,level2,level3,level4,level5]

    globs.polygons = []

    listen.launch(next_level_loop())
    listen.launch(reset_level_loop())

def next_level_loop():
    while True:
        yield from listen.event("next_level")

        globs.play_disabled = True
        yield from listen.wait(0.1)
        if globs.level_idx+1 < len(globs.levels):
            globs.selected_color = 0

            globs.level_idx += 1
            print("Loading level",globs.level_idx+1,"of",len(globs.levels))

            polys = globs.levels[globs.level_idx]()
            idxs = list(range(len(polys)))
            np.random.shuffle(idxs)
            globs.polygons = []
            for i in idxs:
                yield from listen.wait(2/len(polys))
                globs.polygons.append(polys[i])

            globs.polygons = polys # to reset the order
            globs.play_disabled = False

            listen.dispatch("update_hud")
        else:
            globs.level_idx = -1
            listen.dispatch("ending_screen")


def reset_level_loop():
    while True:
        yield from listen.event("reset_level")
        globs.play_disabled = True

        polys = globs.levels[globs.level_idx]()
        idxs = list(range(len(polys)))
        np.random.shuffle(idxs)

        for i in idxs:
            if globs.polygons[i].color != polys[i].color:
                yield from listen.wait(2/len(polys))
            globs.polygons[i].color = polys[i].color

        globs.selected_color = 0
        listen.dispatch("update_hud")

        globs.play_disabled = False


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
    globs.move_count = 7

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
    globs.move_count = 8

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


def level3():
    globs.move_count = 5

    s = 1.0
    t = s * np.sqrt(3)/2

    globs.polydata["origin"] = Vec(-10,0)
    globs.polydata["nx"] = 5
    globs.polydata["ny"] = 4

    cs = []
    cs.append(Vec(1.0, 0.0, 0.0)) # red 0
    cs.append(Vec(0.0, 1.0, 0.0)) # green 1
    cs.append(Vec(0.0, 0.0, 1.0)) # blue 2
    cs.append(Vec(1.0, 0.0, 1.0)) # pink 3
    cs.append(Vec(1.0, 1.0, 0.0)) # yellow 4
    globs.polydata["colors"] = cs

    polys = {}
    polys["sa"] = Polygon(cs[0], [Vec(t,-s/2), Vec(t,s/2), Vec(s+t,s/2), Vec(s+t,-s/2)])

    polys["tb"] = Polygon(cs[3], [Vec(t,s/2), Vec(t+(s/2), t+(s/2)), Vec(t+s, s/2)])

    polys["tc"] = Polygon(cs[2], [Vec(s+t, -s/2), Vec(s+t, s/2), Vec((2*t)+s, 0)])

    polys["td"] = Polygon(cs[1], [Vec(s+t, s/2), Vec(s+(2*t), s), Vec(s+(2*t), 0)])

    polys["se"] = Polygon(cs[4], [Vec(s+t,s/2), Vec(t+(s/2), (s/2)+t), Vec((s/2)+(2*t),s+t), Vec((2*t)+s,s)])

    polys["tf"] = Polygon(cs[2], [Vec(t+s/2,s/2+t), Vec(t+s/2, (1.5*s)+t), Vec((2*t)+(s/2),s+t)])

    polys["tg"] = Polygon(cs[1], [Vec(s/2,s+t),Vec(t+(s/2),(1.5*s)+t),Vec((s/2)+t,(s/2)+t)])

    polys["sh"] = Polygon(cs[4], [Vec(0,s), Vec(s/2,s+t), Vec(t+s/2,t+s/2), Vec(t,s/2)])

    polys["ti"] = Polygon(cs[2], [Vec(0,0), Vec(0,s), Vec(t,s/2)])

    polys["tj"] = Polygon(cs[1], [Vec(0,0), Vec(t,s/2), Vec(t,-s/2)])

    polys["tk"] = Polygon(cs[3], [Vec((2*t)+(s/2),s+t), Vec((2*t)+(1.5*s),s+t), Vec((2*t)+s,s)])

    #####
    polys["sa"].neighbors = [(0,0,"tc"), (0,0,"tb"), (0,0,"tj"), (0,-1,"tk")]
    polys["tb"].neighbors = [(0,0,"sa"),(0,0,"se"),(0,0,"sh")]
    polys["tc"].neighbors = [(0,0,"sa"),(0,0,"td"),(1,-1,"tg")]
    polys["td"].neighbors = [(0,0,"tc"),(0,0,"se"),(1,0,"ti")]
    polys["se"].neighbors = [(0,0,"td"),(0,0,"tb"),(0,0,"tk"),(0,0,"tf")]
    polys["tf"].neighbors = [(0,0,"se"),(0,0,"tg"),(0,1,"tj")]
    polys["tg"].neighbors = [(0,0,"sh"),(0,0,"tf"),(-1,1,"tc")]
    polys["sh"].neighbors = [(0,0,"tb"),(0,0,"ti"),(0,0,"tg"),(-1,0,"tk")]
    polys["ti"].neighbors = [(0,0,"tj"),(0,0,"sh"),(-1,0,"td")]
    polys["tj"].neighbors = [(0,0,"sa"),(0,0,"ti"),(0,-1,"tf")]
    polys["tk"].neighbors = [(0,0,"se"),(0,1,"sa"),(1,0,"sh")]

    return repeat_cell(2, 3, Vec((2*t)+s,0), Vec((t+s/2),(1.5*s)+(t)), polys)



def level4():
    globs.move_count = 5

    r3 = np.sqrt(3)
    globs.polydata["origin"] = Vec(-1,-5.5)
    globs.polydata["nx"] = 2
    globs.polydata["ny"] = 2

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


    polys["t6"] = Polygon(cs[1],[Vec(0,0), Vec(0,1), Vec(r3/2,0.5)])
    polys["t7"] = Polygon(cs[2],[Vec(1.5*r3 + 1.5, 4.5+r3*1.5), Vec(1.5*r3 + 1.5, 3.5+r3*1.5), Vec(1*r3 + 1.5, 4.0+r3*1.5)])

    polys["t8"] = Polygon(cs[1],[Vec(0,r3+3), Vec(0,r3+2), Vec(r3/2,r3+2.5) ])
    polys["t9"] = Polygon(cs[2],[Vec(0,r3+3), Vec(r3/2,r3+3.5), Vec(r3/2,r3+2.5) ])

    polys["t10"] = Polygon(cs[1],[Vec(1.5*r3 + 1.5, 1.5+r3/2),Vec(1*r3 + 1.5, 1+r3/2), Vec(1*r3 + 1.5, 2+r3/2)])
    polys["t11"] = Polygon(cs[2],[Vec(1.5*r3 + 1.5, 1.5+r3/2),Vec(1.5*r3 + 1.5, 2.5+r3/2), Vec(1*r3 + 1.5, 2+r3/2)])


    polys["t12"] = Polygon(cs[1],[Vec(0.5, 1+ r3/2),Vec(0.5+r3/2, 1.5+ r3/2),Vec(0.5+r3/2, 0.5+ r3/2)])
    polys["t13"] = Polygon(cs[2],[Vec(0.5, 1+ r3/2),Vec(0.5, 2+ r3/2),Vec(0.5+r3/2, 1.5 +r3/2)])


    polys["t14"] = Polygon(cs[1],[Vec(0.5+r3/2, 2.5+ r3/2),Vec(0.5, 2+ r3/2),Vec(0.5+r3/2, 1.5 +r3/2)])
    polys["t15"] = Polygon(cs[2],[Vec(0.5+r3/2, 2.5+ r3/2),Vec(0.5+r3, 2+ r3/2),Vec(0.5+r3/2, 1.5 +r3/2)])
    polys["t16"] = Polygon(cs[1],[Vec(0.5+r3, 1+r3/2),Vec(0.5+r3, 2+ r3/2),Vec(0.5+r3/2, 1.5 +r3/2)])


    polys["t17"] = Polygon(cs[2],[Vec(0.5+r3, 1+ r3/2),Vec(0.5+r3/2, 1.5+ r3/2),Vec(0.5+r3/2, 0.5+ r3/2)])

    polys["s1"].neighbors = [(0,0,"t6"),(0,0,"t12"),(0,-1,"d5"),(-1,0,"d5")]
    polys["s2"].neighbors = [(0,0,"t14"),(0,0,"t8"),(-1,0,"d5"),(0,0,"d5")]
    polys["s3"].neighbors = [(0,0,"t16"),(0,0,"t10"),(0,-1,"d5"),(0,0,"d5")]

    polys["d5"].neighbors = [(0,0,"s3"),(0,0,"t15"),(0,0,"s2"),(0,0,"t9"),
                             (0,1,"s1"),(0,1,"t17"),(0,1,"s3"),(0,0,"t7"),
                             (1,0,"s2"),(1,0,"t13"),(1,0,"s1"),(0,0,"t11"),]


    polys["t6"].neighbors = [(0,-1,"t9"),(-1,0,"t11"),(0,0,"s1")]
    polys["t7"].neighbors = [(0,1,"t10"),(1,0,"t8"),(0,0,"d5")]


    polys["t8"].neighbors = [(0,0,"t9"),(-1,0,"t7"),(0,0,"s2")]
    polys["t9"].neighbors = [(0,0,"t8"),(0,1,"t6"),(0,0,"d5")]

    polys["t10"].neighbors = [(0,0,"t11"),(0,-1,"t7"),(0,0,"s3")]
    polys["t11"].neighbors = [(0,0,"t10"),(1,0,"t6"),(0,0,"d5")]

    polys["t12"].neighbors = [(0,0,"t13"),(0,0,"t17"),(0,0,"s1")]
    polys["t13"].neighbors = [(0,0,"t12"),(0,0,"t14"),(-1,0,"d5")]

    polys["t14"].neighbors = [(0,0,"t13"),(0,0,"t15"),(0,0,"s2")]
    polys["t15"].neighbors = [(0,0,"t14"),(0,0,"t16"),(0,0,"d5")]

    polys["t16"].neighbors = [(0,0,"t17"),(0,0,"t15"),(0,0,"s3")]

    polys["t17"].neighbors = [(0,0,"t12"),(0,0,"t16"),(0,-1,"d5")]

    s = 0.5
    for key in polys.keys():
        polys[key].points = [p*s for p in polys[key].points]

    return repeat_cell(3, 3, s*Vec(1.5*r3 + 1.5, 1.5+r3/2), s*Vec(0,r3+3), polys)


def level5():
    globs.move_count = 5

    r3 = np.sqrt(3)
    globs.polydata["origin"] = Vec(-3,-5)
    globs.polydata["nx"] = 3
    globs.polydata["ny"] = 3

    cs = []
    cs.append(Vec(1.0, 0.0, 1.0)) # red
    cs.append(Vec(0.0, 1.0, 1.0)) # yellow
    cs.append(Vec(1.0, 1.0, 0.0)) # blue
    globs.polydata["colors"] = cs

    polys = {}

    polys["t1"] = Polygon(cs[0],[Vec(0,0), Vec(3,0), Vec(1.5, 3*r3/2)])
    polys["t2"] = Polygon(cs[1],[Vec(1, 2*r3/2), Vec(0.5, 3*r3/2), Vec(1.5, 3*r3/2)])
    polys["t3"] = Polygon(cs[2],[Vec(2.5, r3/2), Vec(1.5, 3*r3/2), Vec(3.5, 3*r3/2)])

    polys["t1"].neighbors = [(0,0,"t2"),(0,-1,"t2"),(1,-1,"t2"),(0,0,"t3"),(0,-1,"t3"),(-1,0,"t3")]
    polys["t2"].neighbors = [(0,0,"t1"),(0,1,"t1"),(-1,1,"t1")]
    polys["t3"].neighbors = [(0,0,"t1"),(0,1,"t1"),(1,0,"t1")]

    s = 0.5
    for key in polys.keys():
        polys[key].points = [p*s for p in polys[key].points]

    return repeat_cell(4, 4, s*Vec(2.5, r3/2), s*Vec(0.5, 3*r3/2), polys)
