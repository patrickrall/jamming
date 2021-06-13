import numpy as np

from patpygl.vector import *
from patpygl import listen

from level6 import *

import globs
from polygon import Polygon
from hud import update_hud

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



def rotate(vect, center, angle):
    dx,dy = center.xy
    x,y = vect.xy
    px = ((x - dx) * cos(angle)) - ((y - dy) * sin(angle)) + dx
    py = ((x - dx) * sin(angle)) + ((y - dy) * cos(angle)) + dy
    return Vec(px,py)

def level6():

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
    globs.polydata["colors"] = [cs[0], cs[2], cs[4], cs[3], cs[2], cs[5], cs[1]]


    polys = {}

    s = 1.0
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
            [rotate(Vec(xr[3],yr[3]),cen,th), rotate(Vec(xr[4],yr[5]),cen,th), \
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
                                [(x,y,c("sj",z)) for x,y,z in [b][cut]][0]]

        polys[c("sf")].neighbors = [(0,0,c("tc")), (0,0,c("te")), (0,0,c("th")), (0,0,c("tg"))]

        polys[c("tg")].neighbors = [(0,0,c("sf")), (0,0,c("sj")), (0,0,p("td"))]

        polys[c("th")].neighbors = [(0,0,c("sf")), (0,0,c("ti")), \
                                [(x,y,c("ti",z)) for x,y,z in [b][cut]][0]]

        polys[c("ti")].neighbors = [(0,0,c("th")), (0,0,c("sj")), \
                                [(x,y,c("th",z)) for x,y,z in [b][cut]][0]]

        polys[c("sj")].neighbors = [(0,0,c("ti")), (0,0,c("tg")), \
                                [(x,y,c("te",z)) for x,y,z in [b][cut]][1],
                                [(x,y,c("sj",z)) for x,y,z in [b][cut]][2]]


    return repeat_cell(2, 3, Vec((2*t)+s,0), Vec((t+s/2),(1.5*s)+(t)), polys)


































