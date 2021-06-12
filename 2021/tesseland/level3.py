def level3():

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
