import glfw
import json, os

from patpygl import listen
from patpygl.quadarray import *
from render import mouse_coords
import numpy as np
from play import place_player

import globs
from mode import mode_switch

def edit_init():

    globs.mode = "grid_edit"
    globs.grid = Grid()

    globs.world_state = "light"
    globs.fpsbox.color = Vec(0,0,0,1.0)
    populate_grid()


    listen.launch(editor_camera_loop())
    listen.launch(editor_key_loop())
    listen.launch(grid_editor_loop())


def editor_camera_loop():
    # keep track of keys in this dictionary
    keys = {
        glfw.KEY_W: False,
        glfw.KEY_A: False,
        glfw.KEY_S: False,
        glfw.KEY_D: False,
        glfw.KEY_LEFT_SHIFT: False,
        glfw.KEY_SPACE: False,
    }
    while True:
        events = yield from listen.any(
                key=listen.on_key(globs.window),
                frame=listen.event("on_frame"))

        # update dictionary
        if "key" in events:
            _, key, _, action, _ = events["key"]
            if key in keys:
                if action == glfw.PRESS: keys[key] = True
                if action == glfw.RELEASE: keys[key] = False

        # must be in grid_edit mode
        if globs.mode != "grid_edit": continue

        # adjust camera position based on key state
        if "frame" in events:
            _, dt = events["frame"]

            v = -10

            dx = 0
            if keys[glfw.KEY_D]: dx += v
            if keys[glfw.KEY_A]: dx -= v
            globs.cam["pos"].x += dt*dx

            dy = 0
            if keys[glfw.KEY_W]: dy += v
            if keys[glfw.KEY_S]: dy -= v
            globs.cam["pos"].y += dt*dy



########################################################################

# Grid class: maintains a bunch of quadarrays, one for each asset
# Can edit grid via globs.grid[x,y] = "terrain-top", automatically does bookkeeping.
# Also handles saving and loading to disk.
# Put this in globs.grid
class Grid():

    def __init__(self):
        # load file from disk, if it exists, into self.data
        # python can handle tuples (x,y) as keys, so self.data can have those.
        # However, JSON doesn't support this, so I make those str(x)+":"+str(y) when I save.
        self.fname = "level.json"
        if os.path.exists(self.fname):
            with open(self.fname) as f:
                self.data = {}
                raw_data = json.loads(f.read())
                for key in raw_data:
                    x,y = key.split(":")
                    self.data[int(x),int(y)] = raw_data[key]
        else:
            self.data = {}
            self.save()

        self.autoupdate = True

        # these assets are supported by the grid.
        self.assets = ["dark","light","dark-locked","light-locked","portal"]

        # make some quadarrays, one for each asset
        self.arrays = {}
        for key in self.assets:
            self.arrays[key] = QuadArray(globs.assets[key])
            globs.quadarrays.append(self.arrays[key])
            self.arrays[key].update()

        # populat the quadarrays with the grid data
        for (x,y) in self.data:
            asset = self.data[(x,y)]
            self.arrays[asset].quads.append(Vec(x,y,0))

        for key in self.assets:
            self.arrays[key].update()

    # helper for forcing the inputs to be integers
    def round(self,pos):
        x,y = pos
        return int(x),int(y)

    # globs.grid[0,0]
    def __getitem__(self,pos):
        x,y = self.round(pos)
        return self.data[(x,y)]

    # (0,0) in globs.grid
    def __contains__(self,pos):
        x,y = self.round(pos)
        return (x,y) in self.data

    # del globs.grid[0,0]
    def __delitem__(self,pos):
        x,y = self.round(pos)

        if (x,y) not in self.data: return
        prv_asset = self.data[(x,y)]
        del self.data[(x,y)]

        idx = None
        for i in range(len(self.arrays[prv_asset].quads)):
            quad = self.arrays[prv_asset].quads[i]
            if quad.x == x and quad.y == y:
                idx = i
                break

        assert idx is not None
        del self.arrays[prv_asset].quads[i]
        if self.autoupdate: self.arrays[prv_asset].update()

    # globs.grid[0,0] = "terrain-top"
    def __setitem__(self,pos,asset):
        x,y = self.round(pos)

        if (x,y) in self.data:
            # if asset is the same, dont do anything
            if self.data[(x,y)] == asset: return

            # delete the asset if it differs
            prv_asset = self.data[(x,y)]
            idx = None
            for i in range(len(self.arrays[prv_asset].quads)):
                quad = self.arrays[prv_asset].quads[i]
                if quad.x == x and quad.y == y:
                    idx = i
                    break
            del self.arrays[prv_asset].quads[i]
            if self.autoupdate: self.arrays[prv_asset].update()

        self.data[(x,y)] = asset
        self.arrays[asset].quads.append(Vec(x,y,0))
        if self.autoupdate: self.arrays[asset].update()

    # for (x,y) in globs.grid
    def __iter__(self):
        for (x,y) in self.data:
            yield (x,y)

    def save(self):
        out = {}
        for (x,y) in self.data:
            out[str(x)+":"+str(y)] = self.data[(x,y)]
        with open(self.fname,"w") as f:
            f.write(json.dumps(out))

    def update(self):
        for key in self.assets:
            self.arrays[key].update()


########################################################################


def populate_grid():
    # size of the viewport in world space
    dims = globs.cam["dims"]

    x0,y0 = np.floor(-globs.cam["pos"].x),np.floor(-globs.cam["pos"].y)
    while x0 > -globs.cam["pos"].x: x0 -= 1
    while y0 > -globs.cam["pos"].y: y0 -= 1
    while x0+1 < -globs.cam["pos"].x: x0 += 1
    while y0+1 < -globs.cam["pos"].y: y0 += 1


    globs.grid.autoupdate = False

    x = x0 - 1
    while x < -globs.cam["pos"].x + dims.x:
        x += 1
        y = y0 - 1
        while y < -globs.cam["pos"].y + dims.y:
            y += 1
            if (x,y) not in globs.grid:
                globs.grid[x,y] = globs.world_state

    globs.grid.autoupdate = True
    globs.grid.update()




def editor_key_loop():
    while True:
        _, key, _, action, _ = yield from listen.on_key(globs.window)

        # must be in grid_edit mode
        if globs.mode != "grid_edit": continue
        if action != glfw.PRESS: continue

        if key == glfw.KEY_TAB:
            print("switch", globs.world_state)
            mode_switch()
            print(globs.world_state)

        if key == glfw.KEY_F:
            print("fill")
            populate_grid()



########################################################################

def grid_editor_loop():

    # currently selected asset
    cursor_asset = 0 # an index in globs.grid.assets

    # a quadarray for the cursor
    cursor_array = QuadArray(globs.assets[globs.grid.assets[cursor_asset]])
    cursor_array.update()
    globs.quadarrays.append(cursor_array)

    # convert mouse coordinates to grid coordinates with rounding
    def mouse_to_grid(x,y):
        coords = mouse_coords(x,y)
        x0,y0 = np.floor(coords.x),np.floor(coords.y)
        while x0 > x: x0 -= 1
        while y0 > y: y0 -= 1
        return x0,y0

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

            # releasing any mouse button saves
            if action == glfw.RELEASE:
                globs.grid.save()

            # middle click
            if button == glfw.MOUSE_BUTTON_MIDDLE and\
                    action == glfw.PRESS:
                x,y = glfw.get_cursor_pos(globs.window)
                x,y = mouse_to_grid(x,y)
                if (x,y) in globs.grid:
                    # click on a grid tile: make that tile the cursor tile
                    asset = globs.grid[x,y]
                    cursor_asset = globs.grid.assets.index(asset)

                    cursor_array.asset.clear()
                    cursor_array.asset.enqueue(globs.assets[globs.grid.assets[cursor_asset]],loop=True)
                    cursor_array.update()


            # right click places the palyer
            if glfw.get_mouse_button(globs.window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
                place_player(x,y)
                # delete the cursor quad if we have it
                if len(cursor_array.quads) > 0:
                    del cursor_array.quads[0]
                    cursor_array.update()
                globs.mode = "play"
                continue

        # editing the terrain on cursor movement or click
        if "button" in events or "pos" in events:
            if "button" in events: x,y = glfw.get_cursor_pos(globs.window)
            else: _,x,y = events["pos"]
            x,y = mouse_to_grid(x,y)

            if glfw.get_mouse_button(globs.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
                # left click places the current asset
                asset = globs.grid.assets[cursor_asset]
                globs.grid[x,y] = asset


        # scrolling changes the cursor asset
        if "scroll" in events:
            _, _, dy = events["scroll"]

            if dy > 0:
                cursor_asset += 1
                if cursor_asset == len(globs.grid.assets):
                    cursor_asset = 0

            if dy < 0:
                cursor_asset -= 1
                if cursor_asset == -1:
                    cursor_asset = len(globs.grid.assets)-1

            cursor_array.asset.clear()
            cursor_array.asset.enqueue(globs.assets[globs.grid.assets[cursor_asset]],loop=True)
            cursor_array.update()

        # remove the cursor quad when the mouse leaves the window
        if "enter" in events:
            _, entered = events["enter"]
            if not entered:
                if len(cursor_array.quads) > 0:
                    del cursor_array.quads[0]
                cursor_array.update()

        # move the cursor quad to the mouse position
        if "pos" in events:
            _,x,y = events["pos"]

            x,y = mouse_to_grid(x,y)

            if len(cursor_array.quads) == 0:
                cursor_array.quads.append(Vec(0,0,0.5))

            cursor_array.quads[0].x = x
            cursor_array.quads[0].y = y
            cursor_array.update()


