
import globs
from patpygl.vector import *

def mode_switch():
    globs.grid.autoupdate = False

    for (x,y) in globs.grid:
        if "light" in globs.grid[x,y]:
            globs.grid[x,y] = globs.grid[x,y].replace("light","dark")
        elif "dark" in globs.grid[x,y]:
            globs.grid[x,y] = globs.grid[x,y].replace("dark","light")

    if globs.world_state == "light":
        globs.world_state = "dark"
        globs.fpsbox.color = Vec(1,1,1,1.0)
    else:
        globs.world_state = "light"
        globs.fpsbox.color = Vec(0,0,0,1.0)

    globs.grid.autoupdate = True
    globs.grid.update()
