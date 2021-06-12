
def level3():

    s = 1.0
    t = s * np.sqrt(3)/2

    globs.polydata["origin"] = Vec(-0.3,-1.2)
    globs.polydata["nx"] = 4
    globs.polydata["ny"] = 2

    cs = []
    cs.append(Vec(1.0, 0.0, 0.0)) # red 0
    cs.append(Vec(0.0, 1.0, 0.0)) # green 1
    cs.append(Vec(0.0, 0.0, 1.0)) # blue 2
    cs.append(Vec(1.0, 0.0, 1.0)) # pink 3
    cs.append(Vec(1.0, 1.0, 0.0)) # yellow 4
    globs.polydata["colors"] = cs

    polys = {}
    polys["sa"] = Polygon(cs[0], [Vec(t,-s/2), Vec(t,s/2), Vec(s+t,-s/2), Vec(s+t,-s/2)])

    polys["tb"] = Polygon(cs[3], [Vec(t,s/2), Vec(t+s/2, t+s/2), Vec(t+s, s/2)])
    
    polys["tc"] = Polygon(cs[2], [Vec(s+t, -s/2), Vec(s+t, s/2), Vec(0, (2*t)+s)])
    
    polys["td"] = Polygon(cs[1], [Vec(s+t, s/2), Vec(s+(2*t), s), Vec(s+(2*t), 0)])

    polys["se"] = Polygon(cs[4], [Vec(s+t,s/2), Vec(t+s/2, s+t/2), Vec((s/2)+(2*t),s+t), Vec((2*t)+s,s)])

    polys["tf"] = Polygon(cs[2], [Vec(t+s/2,s/2+t), Vec(t+s/2, (1.5*s)+t), Vec((2*t)+(s/2),s+t)])

    polys["tg"] = Polygon(cs[1], [Vec(s/2,s+t), Vec(t+s/2,(1.5*s)+(t/2)), Vec((s/2)+t,(1.5*s)+(t/2))])

    polys["sh"] = Polygon(cs[4], [Vec(0,s), Vec(s/2,s+t), Vec(t+s/2,t+s/2), Vec(t,s/2)])

    polys["ti"] = Polygon(cs[2], [Vec(0,0), Vec(0,s), Vec(t,s)])

    polys["tj"] = Polygon(cs[1], [Vec(0,0), Vec(t,s/2), Vec(t,-s/2)])

    polys["tk"] = Polygon(cs[3], [Vec((2*t)+(s/2),s+t), Vec((2*t)+s,s+t), Vec((2*t)+s,s)])
 
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

    return repeat_cell(2, 3, Vec((2*s)+t,0), Vec((s+t/2),(1.5*s)+(t)), polys)