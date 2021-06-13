
import numpy as np

from patpygl.vector import *
from patpygl import listen

import globs
from polygon import Polygon

from colors import colors

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
    globs.levels = [level1,level0,level2,level4,level3,level5,level7]
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
    globs.move_count = 7 # optimized

    globs.polydata["origin"] = Vec(-0.3,-1.2)
    globs.polydata["nx"] = 2
    globs.polydata["ny"] = 2

    cs = []
    cs.append(colors["maroon"])
    cs.append(colors["goldenrod"])
    globs.polydata["colors"] = cs

    polys = {}

    polys["t1"] = Polygon(cs[0],[Vec(0,0), Vec(0,1), Vec(1,0)])
    polys["t2"] = Polygon(cs[1],[Vec(1,1), Vec(0,1), Vec(1,0)])

    polys["t1"].neighbors = [(0,0,"t2"),(-1,0,"t2"),(0,-1,"t2")]
    polys["t2"].neighbors = [(0,0,"t1"),(1,0,"t1"),(0,1,"t1")]

    return repeat_cell(5, 5, Vec(1,0), Vec(0,1), polys)


def level2():
    globs.move_count = 8 # optimized

    globs.polydata["origin"] = Vec(-0.3,-1.2)
    globs.polydata["nx"] = 2
    globs.polydata["ny"] = 2

    cs = []
    cs.append(colors["mediumseagreen"])
    cs.append(colors["crimson"])
    cs.append(colors["indigo"])
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
    globs.move_count = 9

    s = 1.0
    t = s * np.sqrt(3)/2

    globs.polydata["origin"] = Vec(-10,0)
    globs.polydata["nx"] = 5
    globs.polydata["ny"] = 4

    cs = []
    cs.append(colors["skyblue"])
    cs.append(colors["lightslategray"])
    cs.append(colors["burlywood"])
    cs.append(colors["tomato"])
    cs.append(colors["palegreen"])
    globs.polydata["colors"] = [cs[x] for x in [3, 2, 1, 2, 3, 4, 1, 2, 4]]

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

    return repeat_cell(2, 1, Vec((2*t)+s,0), Vec((t+s/2),(1.5*s)+(t)), polys)



def level4():
    globs.move_count = 10 # optimized

    r3 = np.sqrt(3)
    globs.polydata["origin"] = Vec(-1,-5.5)
    globs.polydata["nx"] = 2
    globs.polydata["ny"] = 2

    cs = []
    cs.append(colors["crimson"])
    cs.append(colors["darkturquoise"])
    cs.append(colors["slategray"])
    cs.append(colors["honeydew"])
    globs.polydata["colors"] = cs

    polys = {}

    delta1 = Vec(r3/2,0.5) - Vec(0,1)
    delta2 = Vec(-delta1.y, delta1.x)
    polys["s1"] = Polygon(cs[3],[Vec(0,1) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])


    delta1 = Vec(delta1.x,-delta1.y)
    delta2 = Vec(delta2.x,-delta2.y)
    polys["s2"] = Polygon(cs[3],[Vec(0,2+r3) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    delta1 = Vec(1,0)
    delta2 = Vec(0,1)
    polys["s3"] = Polygon(cs[3],[Vec(0.5+r3,1+r3/2) + v for v in [Vec(0,0), delta1, delta2+delta1, delta2]])

    # lolwut no 4
    polys["d5"] = Polygon(cs[0],[Vec(r3/2 + 0.5, 2.5+r3/2), Vec(r3/2, 2.5+r3), Vec(r3/2, 3.5+r3),
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
    globs.move_count = 7 # optimized

    r3 = np.sqrt(3)
    globs.polydata["origin"] = Vec(-3,-5)
    globs.polydata["nx"] = 3
    globs.polydata["ny"] = 3

    cs = []
    cs.append(colors["crimson"]) # red
    cs.append(colors["khaki"]) # yellow
    cs.append(colors["royalblue"]) # blue
    globs.polydata["colors"] = cs

    polys = {}

    polys["t1"] = Polygon(cs[1],[Vec(0,0), Vec(3,0), Vec(1.5, 3*r3/2)])
    polys["t2"] = Polygon(cs[0],[Vec(1, 2*r3/2), Vec(0.5, 3*r3/2), Vec(1.5, 3*r3/2)])
    polys["t3"] = Polygon(cs[2],[Vec(2.5, r3/2), Vec(1.5, 3*r3/2), Vec(3.5, 3*r3/2)])

    polys["t1"].neighbors = [(0,0,"t2"),(0,-1,"t2"),(1,-1,"t2"),(0,0,"t3"),(0,-1,"t3"),(-1,0,"t3")]
    polys["t2"].neighbors = [(0,0,"t1"),(0,1,"t1"),(-1,1,"t1")]
    polys["t3"].neighbors = [(0,0,"t1"),(0,1,"t1"),(1,0,"t1")]

    s = 0.5
    for key in polys.keys():
        polys[key].points = [p*s for p in polys[key].points]

    return repeat_cell(4, 4, s*Vec(2.5, r3/2), s*Vec(0.5, 3*r3/2), polys)

    
def rotate(vect, center, angle):
    dx,dy = center.xy
    x,y = vect.xy
    px = ((x - dx) * np.cos(angle)) - ((y - dy) * np.sin(angle)) + dx
    py = ((x - dx) * np.sin(angle)) + ((y - dy) * np.cos(angle)) + dy
    return Vec(px,py)

def level6():

    globs.move_count = 9
    globs.polydata["origin"] = Vec(-5,-2)
    globs.polydata["nx"] = 5
    globs.polydata["ny"] = 4

    cs = []
    cs.append(Vec(0.0, 1.0, 1.0)) # cyan 0
    cs.append(Vec(0.0, 1.0, 0.0)) # green 1
    cs.append(Vec(0.0, 0.0, 1.0)) # blue 2
    cs.append(Vec(1.0, 0.0, 1.0)) # pink 3
    cs.append(Vec(1.0, 1.0, 0.0)) # yellow 4
    cs.append(Vec(0.0, 0.0, 0.0)) # black 5
    globs.polydata["colors"] = [cs[0], cs[2], cs[4], cs[3], cs[2], cs[5], cs[2], cs[4], cs[2]]


    polys = {}

    s = 0.5
    t = s * np.sqrt(3.0)/2.0
    xr = [0, s/2, t, t+(s/2), t+s, (s/2)+(2*t), (2*t)+s, (1.5*s) + (2*t), (2*t) + (2*s)]
    yr = [0, s/2, s, (s/2)+t, s+t, (1.5*s)+t]

    for cut in range(6):
        th, cen = np.radians(cut*60), Vec(0,0)

        def n(tile): return tile + str((cut + 1) % 6) # tile name with id for next cut (ccw)
        def p(tile): return tile + str((cut - 1) % 6) # tile name with id for previous cut (cw)
        def c(tile, a_cut=cut): return tile + str(a_cut) # tile+id: arbitrary cut (default active)

        polys[c("ta")] = Polygon(cs[2], [rotate(Vec(xr[0],yr[0]),cen,th), \
            rotate(Vec(xr[0],yr[2]),cen,th), rotate(Vec(xr[2],yr[1]),cen,th)])

        polys[c("sb")] = Polygon(cs[0], \
            [rotate(Vec(xr[0],yr[2]),cen,th), rotate(Vec(xr[1],yr[4]),cen,th), \
            rotate(Vec(xr[3],yr[3]),cen,th), rotate(Vec(xr[2],yr[1]),cen,th)])

        polys[c("tc")] = Polygon(cs[4], [rotate(Vec(xr[2],yr[1]),cen,th), \
            rotate(Vec(xr[3],yr[3]),cen,th), rotate(Vec(xr[4],yr[1]),cen,th)])
        
        polys[c("td")] = Polygon(cs[4], [rotate(Vec(xr[1],yr[4]),cen,th), \
            rotate(Vec(xr[3],yr[5]),cen,th), rotate(Vec(xr[3],yr[3]),cen,th)])

        polys[c("te")] = Polygon(cs[3], [rotate(Vec(xr[3],yr[3]),cen,th), \
            rotate(Vec(xr[3],yr[5]),cen,th), rotate(Vec(xr[5],yr[4]),cen,th)])

        polys[c("sf")] = Polygon(cs[5], \
            [rotate(Vec(xr[3],yr[3]),cen,th), rotate(Vec(xr[5],yr[3]),cen,th), \
            rotate(Vec(xr[6],yr[2]),cen,th), rotate(Vec(xr[4],yr[1]),cen,th)])

        polys[c("tg")] = Polygon(cs[3], [rotate(Vec(xr[4],yr[1]),cen,th), \
            rotate(Vec(xr[6],yr[2]),cen,th), rotate(Vec(xr[6],yr[0]),cen,th)])

        polys[c("th")] = Polygon(cs[4], [rotate(Vec(xr[5],yr[4]),cen,th), \
            rotate(Vec(xr[7],yr[4]),cen,th), rotate(Vec(xr[6],yr[2]),cen,th)])

        polys[c("ti")] = Polygon(cs[2], [rotate(Vec(xr[6],yr[2]),cen,th), \
            rotate(Vec(xr[7],yr[4]),cen,th), rotate(Vec(xr[8],yr[2]),cen,th)])

        polys[c("sj")] = Polygon(cs[1], \
            [rotate(Vec(xr[6],yr[0]),cen,th), rotate(Vec(xr[6],yr[2]),cen,th), \
            rotate(Vec(xr[8],yr[2]),cen,th), rotate(Vec(xr[8],yr[0]),cen,th)])

        # (b[my cut][which border] = (neighbor unit x, neighbor unit y, neighbor cut))
        b = [[(0,1,4), (1,0,2), (1,0,3)], [(1,-1,5), (0,1,3), (0,1,4)], \
        [(-1,0,0), (1,-1,4), (1,-1,5)], [(0,-1,1), (-1,0,5), (-1,0,0)], \
        [(1,-1,2), (0,-1,0), (0,-1,1)], [(1,0,3), (1,-1,1), (1,-1,2)]]

        polys[c("ta")].neighbors = [(0,0,n("ta")), (0,0,c("sb")), (0,0,p("ta"))]
        
        polys[c("sb")].neighbors = [(0,0,c("ta")), (0,0,c("tc")), (0,0,n("tc")), (0,0,c("td"))]

        polys[c("tc")].neighbors = [(0,0,c("sf")), (0,0,c("sb")), (0,0,p("sb"))]

        polys[c("td")].neighbors = [(0,0,c("te")), (0,0,c("sb")), (0,0,n("tg"))]


        polys[c("te")].neighbors = [(0,0,c("sf")), (0,0,c("td")), \
                                [(x,y,c("sj",z)) for x,y,z in [b][0][cut]][0]]

        polys[c("sf")].neighbors = [(0,0,c("tc")), (0,0,c("te")), (0,0,c("th")), (0,0,c("tg"))]

        polys[c("tg")].neighbors = [(0,0,c("sf")), (0,0,c("sj")), (0,0,p("td"))]

        polys[c("th")].neighbors = [(0,0,c("sf")), (0,0,c("ti")), \
                                [(x,y,c("ti",z)) for x,y,z in [b][0][cut]][0]]

        polys[c("ti")].neighbors = [(0,0,c("th")), (0,0,c("sj")), \
                                [(x,y,c("th",z)) for x,y,z in [b][0][cut]][0]]


        polys[c("sj")].neighbors = [(0,0,c("ti")), (0,0,c("tg")), \
                                [(x,y,c("te",z)) for x,y,z in [b][0][cut]][1],
                                [(x,y,c("sj",z)) for x,y,z in [b][0][cut]][2]]


    return repeat_cell(1, 1, Vec((4*t)+(3*s),0), Vec((2*t) + (1.5*s),(3*s)+(3*t)), polys)

def level7():
    globs.move_count = 11

    r3 = np.sqrt(3) #
    h = np.sqrt(0.75)
    globs.polydata["origin"] = Vec(-5,-1)
    globs.polydata["nx"] = 6 #tiling of units
    globs.polydata["ny"] = 4

    cs = []
    red = colors["firebrick"]#red
    green = colors["limegreen"]#green
    blue = colors["dodgerblue"]#blue
    purple = colors["purple"]#purple
    yellow = colors["lemonchiffon"]#yellow
    cs = [red, green, blue, purple, yellow]
    globs.polydata["colors"] = cs

    polys = {}

    # green triangles
    polys["t1"] = Polygon(green,[Vec(0,0),         Vec(1,0),         Vec(0.5, h)])
    polys["t2"] = Polygon(green,[Vec(1+h,0.5),     Vec(h+1.5,h+0.5), Vec(h+0.5,h+0.5)])
    polys["t3"] = Polygon(green,[Vec(h+3,0.5), Vec(h+3.5,h+0.5), Vec(h+2.5,h+0.5)])
    polys["t4"] = Polygon(green,[Vec(h+2.5,h+1.5), Vec(h+3.5,h+1.5), Vec(h+3,2*h+1.5)])
    polys["t5"] = Polygon(green,[Vec(h+0.5,h+1.5), Vec(h+1.5,h+1.5), Vec(h+1, 2*h+1.5)])
    polys["t6"] = Polygon(green,[Vec(0.5,h+2), Vec(1,2*h+2), Vec(0,2*h+2)])

    #blue squares
    polys["t9"] = Polygon(blue,[Vec(1,0), Vec(1+h,0.5), Vec(h+0.5,h+0.5), Vec(0.5,h)])
    polys["t10"] = Polygon(blue,[Vec(h+0.5,h+0.5), Vec(1.5+h,h+0.5), Vec(h+1.5,h+1.5), Vec(h+0.5,h+1.5)])
    polys["t11"] = Polygon(blue, [Vec(h+0.5,h+1.5), Vec(h+1,2*h+1.5),Vec(1,2*h+2), Vec(0.5,h+2)])
    polys["t12"] = Polygon(blue,[Vec(h+3, 0.5), Vec(2*h+3,0), Vec(2*h+3.5,h), Vec(h+3.5,h+0.5)])
    polys["t13"] = Polygon(blue,[Vec(h+2.5, h+0.5), Vec(h+3.5,h+0.5), Vec(h+3.5,h+1.5), Vec(h+2.5,h+1.5)])
    polys["t14"] = Polygon(blue,[Vec(h+3.5, h+1.5), Vec(2*h+3.5,h+2), Vec(2*h+3,2*h+2), Vec(h+3,2*h+1.5)])
    # polys["t15"] = Polygon(blue,[Vec(h+1.5, 3*h+1.5), Vec(h+2,4*h+1.5), Vec(2,4*h+2), Vec(1.5,3*h+2.5)])

    #purple squares
    polys["t18"] = Polygon(purple,[Vec(h+1.5, h+0.5), Vec(h+2.5,h+0.5), Vec(h+2.5,h+1.5), Vec(h+1.5,h+1.5)])

    polys["t19"] = Polygon(purple,[Vec(h+1, 2*h+1.5), Vec(h+1.5,3*h+1.5), Vec(1.5,3*h+2), Vec(1,2*h+2)])
    polys["t20"] = Polygon(purple,[Vec(h+3, 2*h+1.5), Vec(2*h+3,2*h+2), Vec(2*h+2.5,3*h+2), Vec(h+2.5,3*h+1.5)])

    #yellow hex
    polys["t23"] = Polygon(yellow,[Vec(h+1.5, h+1.5), Vec(h+2.5,h+1.5), Vec(h+3,2*h+1.5),
                                   Vec(h+2.5,3*h+1.5), Vec(h+1.5,3*h+1.5), Vec(h+1,2*h+1.5)])
    #red hex
    polys["t25"] = Polygon(red,[Vec(2*h+3.5, h), Vec(3*h+3.5,h+0.5), Vec(3*h+3.5,h+1.5),
                                Vec(2*h+3.5,h+2),Vec(h+3.5,h+1.5), Vec(h+3.5,h+0.5)])

    polys["t30"] = Polygon(red,[Vec(0, 2*h+2), Vec(1,2*h+2), Vec(1.5, 3*h+2),
                                Vec(1, 4*h+2), Vec(0, 4*h+2), Vec(-0.5, 3*h+2)])

    polys["t1"].neighbors = [(0,0,"t9"),(0,-1,"t23"),(-1,0,"t12")]
    polys["t9"].neighbors = [(0,0,"t1"),(0,0,"t2"),(0,-1,"t20"),(0,-1,"t20"),(-1,0,"t25")]
    polys["t2"].neighbors = [(0,0,"t9"),(0,0,"t10"),(1,-1,"t30")]
    polys["t10"].neighbors = [(0, 0, "t2"), (0, 0, "t18"),(0,0,"t5"),(-1,0,"t25")]
    polys["t5"].neighbors = [(0, 0, "t10"), (0, 0, "t23"),(0,0,"t11")]
    polys["t11"].neighbors = [(0,0, "t5"),(0,0,"t19"), (0,0, "t6"),(-1,0,"t25")]
    polys["t6"].neighbors = [(0,0,"t11"), (0,0,"t30"),(-1,0,"t14")]
    polys["t30"].neighbors = [(0, 0, "t6"), (0, 0, "t19"),(-1,0,"t20"),(-1,1,"t2"),(-1,1,"t18"),(-1,1,"t3")]
    polys["t19"].neighbors = [(0,0,"t11"),(0,0,"t23"),(0,0,"t30"),(-1,1,"t12")]
    polys["t23"].neighbors = [(0,0,"t18"),(0,0,"t4"), (0,0,"t20"), (0,0, "t19"),(0,0, "t5"),(0,1,"t1")]
    polys["t18"].neighbors = [(0,0,"t10"),(0,0,"t13"),(0,0,"t23"),(1,-1,"t30")]
    polys["t13"].neighbors = [(0,0, "t18"),(0,0,"t3"),(0,0,"t25"),(0,0,"t4")]
    polys["t3"].neighbors = [(0,0,"t12"),(0,0,"t13"),(1,-1,"t30")]
    polys["t12"].neighbors = [(0, 0, "t3"), (0, 0, "t25"),(1,-1,"t19"),(1,0,"t1")]
    polys["t25"].neighbors = [(0, 0, "t12"), (0, 0, "t14"),(0,0,"t13"),(1,0,"t11"),(1,0,"t10"),(1,0,"t9")]
    polys["t4"].neighbors =  [(0, 0, "t13"), (0, 0, "t14"), (0, 0, "t23")]
    polys["t14"].neighbors = [(0, 0, "t25"), (0, 0, "t20"), (0, 0, "t4"),(1,0,"t6")]
    polys["t20"].neighbors = [(0, 0, "t14"), (0, 0, "t23"),(0,1,"t9"),(1,0,"t30")]


    s = 0.5
    for key in polys.keys():
        polys[key].points = [p*s for p in polys[key].points]

    return repeat_cell(1,2, s*Vec(2*h+3,0), s*Vec(h+1.5,3*h+1.5), polys)


def level0():
    globs.move_count = 6

    globs.polydata["origin"] = Vec(-3.5,0)
    globs.polydata["nx"] = 4
    globs.polydata["ny"] = 4

    cs = []
    cs.append(colors["aquamarine"])
    cs.append(colors["sienna"])
    cs.append(colors["lightcoral"])
    globs.polydata["colors"] = cs

    sqrt = np.sqrt

    polys = {}

    polys["s1"] = Polygon(cs[0],[Vec(0, 0), Vec(1, 0), Vec(3/4, sqrt(3)/4), Vec(1/4, sqrt(3)/4)])
    polys["s2"] = Polygon(cs[1], [Vec(0, 0), Vec(1/2, sqrt(3)/2), Vec(0, sqrt(3)/2), Vec(-(1/4), sqrt(3)/4)])
    polys["s3"] = Polygon(cs[2], [Vec(0, 0), Vec(-(1/2), sqrt(3)/2), Vec(-(3/4), sqrt(3)/4), Vec(-(1/2), 0)])
    polys["s4"] = Polygon(cs[0], [Vec(0, 0), Vec(-1, 0), Vec(-(3/4), -(sqrt(3)/4)), Vec(-(1/4), -(sqrt(3)/4))])
    polys["s5"] = Polygon(cs[1], [Vec(0, 0), Vec(-(1/2), -(sqrt(3)/2)), Vec(0, -(sqrt(3)/2)), Vec(1/4, -(sqrt(3)/4))])
    polys["s6"] = Polygon(cs[2], [Vec(0, 0), Vec(1/2, -(sqrt(3)/2)), Vec(3/4, -(sqrt(3)/4)), Vec(1/2, 0)])

    polys["s1"].neighbors = [(0,0,"s2"),(0,0,"s6"),(1,0,"s3"),(1,0,"s4"),(0,1,"s5")]
    polys["s2"].neighbors = [(0,0,"s1"),(0,0,"s3"),(0,1,"s4"),(0,1,"s5"),(-1,1,"s6")]
    polys["s3"].neighbors = [(0,0,"s2"),(0,0,"s4"),(-1,1,"s5"),(-1,1,"s6"),(-1,0,"s1")]
    polys["s4"].neighbors = [(0,0,"s3"),(0,0,"s5"),(-1,0,"s1"),(-1,0,"s6"),(0,-1,"s2")]
    polys["s5"].neighbors = [(0,0,"s4"),(0,0,"s6"),(0,-1,"s1"),(0,-1,"s2"),(1,-1,"s3")]
    polys["s6"].neighbors = [(0,0,"s5"),(0,0,"s1"),(1,-1,"s2"),(1,-1,"s3"),(1,0,"s4")]

    return repeat_cell(3, 3, Vec(3/2,0), Vec(3/4,3*sqrt(3)/4), polys)





























