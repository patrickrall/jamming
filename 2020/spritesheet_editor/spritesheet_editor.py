
import pyglet
import pyglet.window.key as key
from pyglet.gl import *

from swyne.node import *
from swyne.layout import *
from swyne.dialog import *

import math
import os
import json

from spritesheet_utils import *

# Just a dummy that keeps track of position
# and defers drawing to the window
class SpriteSheetLayoutNode(AbstractNode):

    def __init__(self):
        super().__init__()
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)

    def set_layout(self,pos,dims):
        self.pos = pos
        self.dims = dims

    def layout_hints(self):
        return Vector2(0,0),Vector2(float('inf'),float('inf'))

    def draw(self):
        self.window.draw_spritesheet(self.pos,self.dims)


class SpritesheetEditorWindow(NodeWindow):

    untagged = "Untitled tag" # Temporary tags name

    def __init__(self, fname=None):
        super().__init__(resizable=True)

        # model
        self.frames = []
        self.images = []
        self.tags = []

        # program_state
        self.mode = "frame"
        self.selected = []
        self.mouse_pos = None
        self.dialog_open = False
        self.translate = Vector2(0,0)
        self.scale = 2

        # file
        self.path = None
        self.is_dirty = False

        # node
        self.node, keys = deserialize_node("""
        ColsLayoutNode
        -PaddingLayoutNode 5
        --sheetnode SpriteSheetLayoutNode
        -ForceMinLayoutNode "X"
        --HintedLayoutNode [200,"*","*","*"]
        ---RowsLayoutNode
        ----taglistnode RowsLayoutNode
        ----PaddingLayoutNode "*"
        ----hintsnode RowsLayoutNode
        """)

        self.sheetnode = keys["sheetnode"]
        self.taglistnode = keys["taglistnode"]
        self.hintsnode = keys["hintsnode"]

        # deal with fname
        if fname is not None:
            ext = os.path.splitext(fname)[1]
            if ext == ".json":
                self.path = os.path.abspath(fname)

        if self.path is None:
            self.set_caption("Untitled Sprite Sheet")
            self.tags.append({"name":self.untagged, "length":0})
            self.is_dirty = True

            # must be an image image
            if fname is not None: add_file(self,fname)

            rebuild_menu(self)
        else:
            add_file(self, self.path)
            self.is_dirty = False
            self.set_caption(os.path.basename(self.path))

        rebuild_hints(self)

        # enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    @listener
    def on_close(self):
        if self.dialog_open: return

        if not self.is_dirty:
            super().on_close()
            return

        self.dialog_open = True
        s = "The spritesheet is not saved. Really close?"
        should_close = yield from confirm_dialog(self, s)

        if should_close: super().on_close()

        self.dialog_open = False


    def new_window(self, fname):
        return SpritesheetEditorWindow(fname=fname)

    ############### DRAWING ##############

    def draw_spritesheet(self,pos,dims):

        glEnable(GL_DEPTH_TEST)

        # set up stencil
        glEnable(GL_STENCIL_TEST)
        glClearStencil(0)
        glClear(GL_STENCIL_BUFFER_BIT)

        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glDepthMask(GL_FALSE)

        glStencilMask(0xFF);

        glStencilFunc(GL_ALWAYS, 0xFF, 0xFF)
        glStencilOp(GL_REPLACE, GL_REPLACE, GL_REPLACE)

        glColor4f(0.0,1.0,0.0,1.0)
        glRectf(pos.x,pos.y,pos.x+dims.x,pos.y+dims.y)

        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glDepthMask(GL_TRUE)

        glStencilFunc(GL_EQUAL, 0xFF, 0xFF)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

        # draw light checkers
        glColor4f(0.8,0.8,0.8,1.0)
        stride = 16*self.scale
        odd = False
        x = pos.x + self.translate.x
        y = pos.y+dims.y- self.translate.y-stride

        while y + stride > pos.y :
            x = pos.x + self.translate.x
            if odd: x += stride

            while x < pos.x + dims.x:
                glRectf(x,y,x+stride,y+stride)
                x += stride*2
            y -= stride
            odd = not odd

        # draw dark checkers (all one rect)
        x = max(pos.x, pos.x+self.translate.x)
        y = min(pos.y+dims.y, pos.y+dims.y-self.translate.y)
        glColor4f(0.7,0.7,0.7,1.0)
        glRectf(x,y-dims.y,x+dims.x,y)

        # draw background
        glColor4f(0.4,0.4,0.4,1.0)
        glRectf(pos.x,pos.y,pos.x+dims.x,pos.y+dims.y)

        # draw the images and frames
        glPushMatrix()
        glTranslatef(pos.x, pos.y+dims.y,0)
        glTranslatef(self.translate.x, -self.translate.y,0)

        # Backgrounds: z = 0
        # Image data: z = 0.5
        # Image highlight (green): 0.60
        # Image borders (green): 0.65

        # Frame highlight (red): 0.70
        # Frame borders (red): 0.75

        sc = self.scale

        for i in range(len(self.images)):

            pos = self.images[i]["pos"]
            verts = self.images[i]["vertices"]
            texture = self.images[i]["image"].get_texture()

            glPushMatrix()
            glTranslatef(pos.x*sc,-pos.y*sc,0)

            glBindTexture(texture.target, texture.id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

            glEnable(texture.target)
            glPushAttrib(GL_COLOR_BUFFER_BIT)

            glColor4f(1.0,1.0,1.0,1.0)

            glPushMatrix()
            glScalef(sc,sc,1.0)
            verts.draw(GL_TRIANGLES)
            glPopMatrix()

            glPopAttrib()

            glDisable(texture.target)

            w,h = texture.width*sc, texture.height*sc

            if self.mode == "image" and i in self.selected:
                glPushMatrix()
                glTranslatef(0,0,0.6)
                glColor4f(0.0,1.0,0.0,0.2)
                glRectf(1,0,w,-h)
                glPopMatrix()

            glColor4f(0.0,1.0,0.0,1.0)

            glBegin(GL_LINE_STRIP)
            glVertex3f(1, 0,0.65)
            glVertex3f(w,0,0.65)
            glVertex3f(w,-h,0.65)
            glVertex3f(1,-h,0.65)
            glVertex3f(1,0,0.65)
            glEnd()

            glPopMatrix()

        for i in range(len(self.frames)):
            frame = self.frames[i]

            glPushMatrix()
            glTranslatef(frame["x"]*sc,-frame["y"]*sc,0)
            w,h = frame["w"]*sc,frame["h"]*sc

            if self.mode == "frame" and i in self.selected:
                glPushMatrix()
                glTranslatef(0,0,0.7)
                glColor4f(1.0,0.0,0.0,0.2)
                glRectf(1,0,w,-h)
                glPopMatrix()

            glColor4f(1.0,0.0,0.0,1.0)

            glBegin(GL_LINE_STRIP)
            glVertex3f(1, 0,0.75)
            glVertex3f(w,0,0.75)
            glVertex3f(w,-h,0.75)
            glVertex3f(1,-h,0.75)
            glVertex3f(1,0,0.75)
            glEnd()

            glPopMatrix()

        glPopMatrix()

        glDisable(GL_STENCIL_TEST)
        glDisable(GL_DEPTH_TEST)

        glColor4f(1.0,1.0,1.0,1.0) # reset color



    ############ MOUSE EVENTS ###########

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        # RIGHT: panning
        # LEFT: move via call move_selected_?

        if self.dialog_open: return

        pos,dims = self.sheetnode.pos, self.sheetnode.dims

        if not (x > pos.x and x <= pos.x + dims.x\
                and y > pos.y and y <= pos.y + dims.y):
            return

        if (buttons & pyglet.window.mouse.RIGHT):
            self.translate.x += dx
            self.translate.y -= dy

        if (buttons & pyglet.window.mouse.LEFT):
            if self.mouse_pos is not None:
                new_mouse_pos = Vector2(int(x/self.scale),int(y/self.scale))
                diff = new_mouse_pos - self.mouse_pos

                func = None
                if self.mode == "frame": func = move_selected_frames
                if self.mode == "image":

                    if (key.MOD_ALT & modifiers) or (key.MOD_OPTION & modifiers):
                        func = move_selected_images_sticky
                    else:
                        func = move_selected_images

                if func is not None:
                    good = func(self,diff.x,0)
                    if good: self.mouse_pos.x = new_mouse_pos.x
                    good = func(self,0,-diff.y)
                    if good: self.mouse_pos.y = new_mouse_pos.y

    def on_mouse_scroll(self,x, y, scroll_x, scroll_y):
        if self.dialog_open: return

        sh = self.sheetnode

        pos,dims = self.sheetnode.pos, self.sheetnode.dims

        if (x > pos.x and x <= pos.x + dims.x\
                and y > pos.y and y <= pos.y + dims.y):
            # on sheet: zoom

            prvscale = self.scale

            if (scroll_y > 0):
                self.scale += 1
            if (scroll_y < 0 and self.scale > 1):
                self.scale -= 1

            if prvscale != self.scale:
                self.translate.x = x - self.scale*(x - self.translate.x)/prvscale
                ybar = pos.y + dims.y - y
                self.translate.y = ybar - self.scale*(ybar - self.translate.y)/prvscale
        else:
            # in frame menu: duration

            idx = 0
            for tag in self.tags:
                tagname = tag["name"]

                for i in range(tag["length"]):
                    iter = idx + i
                    node = tag["framenodes"][i].parent.parent
                    if (node.pos.x < x and x < node.pos.x + node.dims.x \
                            and node.pos.y < y and y < node.pos.y + node.dims.y):

                        if (scroll_y > 0):
                            self.frames[iter]["duration"] += 10
                        if (scroll_y < 0 and self.frames[iter]["duration"] > 10):
                            self.frames[iter]["duration"] -= 10

                        tag["framenodes"][i].document.text = str(self.frames[iter]["duration"]) + " ms"
                        dirty(self)
                        break

                idx += 1


    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.dialog_open: return

        if not (buttons & pyglet.window.mouse.LEFT) == 1: return

        pos,dims = self.sheetnode.pos, self.sheetnode.dims
        sc = self.scale

        self.mouse_pos = Vector2(int(x/sc),int(y/sc))


        if (x > pos.x and x <= pos.x + dims.x\
                and y > pos.y and y <= pos.y + dims.y):

            # click into spritesheet area

            if self.mode == "tag":
                self.mode = "frame"

            hit = None
            xbar = x - self.translate.x
            ybar = pos.y + dims.y - y - self.translate.y

            if self.mode == "frame":
                for i in range(len(self.frames)):
                    frame = self.frames[i]
                    if frame["x"]*sc <= xbar and xbar <= (frame["x"]+frame["w"])*sc:
                        if frame["y"]*sc <= ybar and ybar <= (frame["y"]+frame["h"])*sc:
                            hit = i
                            break

            if self.mode == "image":
                for i in range(len(self.images)):
                    pos = self.images[i]["pos"]
                    img = self.images[i]["image"]

                    if pos.x*sc <= xbar and xbar <= (pos.x+img.width)*sc:
                        if pos.y*sc <= ybar and ybar <= (pos.y+img.height)*sc:
                            hit = i
                            break

            if key.MOD_SHIFT & modifiers:
                if hit not in self.selected and hit is not None:
                    self.selected.append(hit)
            else:
                if hit is None:
                    self.selected = []
                else:
                    self.selected = [hit]

            rebuild_hints(self)
        else:
            # click into menu area

            idx = 0
            for j in range(len(self.tags)):
                tag = self.tags[j]
                tagname = tag["name"]

                node = tag["node"].parent.parent
                if (node.pos.x < x and x < node.pos.x + node.dims.x \
                        and node.pos.y < y and y < node.pos.y + node.dims.y):
                    self.mode = "tag"
                    self.selected = [j]
                    rebuild_hints(self)
                    break

                for i in range(tag["length"]):
                    iter = i + idx
                    node = tag["framenodes"][i].parent.parent
                    if (node.pos.x < x and x < node.pos.x + node.dims.x \
                            and node.pos.y < y and y < node.pos.y + node.dims.y):

                        if self.mode != "frame":
                            self.mode = "frame"
                            self.selected = [iter]
                            rebuild_hints(self)
                        else:
                            if key.MOD_SHIFT & modifiers:
                                if iter not in self.selected:
                                    self.selected.append(iter)
                            else:
                                self.selected = [iter]

                        break

                idx += tag["length"]

        set_selection(self)


    ############ KEY EVENTS ###########

    def on_key_press(self, symbol, modifiers):
        if self.dialog_open: return

        if symbol == key.LEFT: dx,dy = -1,0
        elif symbol == key.RIGHT: dx,dy = 1,0
        elif symbol == key.UP: dx,dy = 0,-1
        elif symbol == key.DOWN: dx,dy = 0,1
        else: dx,dy = None,None

        def keys(symb,ctrl=False,alt=False,shift=False):
            if symb == "dir":
                if dx == None: return False
            elif symb != symbol: return False
            if ctrl != (key.MOD_CTRL & modifiers > 0): return False
            if alt != ((key.MOD_OPTION & modifiers > 0) or (key.MOD_ALT & modifiers > 0)): return False
            if shift != (key.MOD_SHIFT & modifiers > 0): return False
            return True

        if keys(key.O, ctrl=True): open_file_dialog(self)
        if keys(key.I, ctrl=True): insert_file_dialog(self)
        if keys(key.S, ctrl=True): save(self)
        if keys(key.S, ctrl=True, shift=True): save_as(self)
        if keys(key.N, ctrl=True): new_file(self)
        if keys(key.TAB): mode_switch(self)

        if self.mode == "tag":
            if keys(key.R, alt=True): rename_tag(self)
            if keys("dir", alt=True): rearrange_tag(self,dx,dy)

            if self.selected[0] > 0 or self.tags[self.selected[0]]["length"] == 0:
                if keys(key.DELETE): delete_tag(self)

            if keys(key.ENTER, alt=True): insert_tag(self)

        if self.mode == "frame":
            if len(self.selected) < 2:
                if keys(key.ENTER, alt=True): insert_frame(self)
            if len(self.selected) == 1:
                if keys("dir", alt=True): rearrange_frame(self,dx,dy)

                if keys("dir", ctrl=True): shrink_frame(self,False,dx,dy)
                if keys("dir", ctrl=True,alt=True): shrink_frame(self,True,dx,dy)

                if keys("dir", shift=True): grow_frame(self,False,dx,dy)
                if keys("dir", shift=True,alt=True): grow_frame(self,True,dx,dy)

            if len(self.selected) > 0:
                if keys(key.DELETE): delete_frames(self)
                if keys("dir"): move_selected_frames(self,dx,dy)

        if self.mode == "image":
            if len(self.selected) == 1:
                if keys(key.ENTER, alt=True): duplicate_image(self)
                if keys(key.S, alt=True): split_image(self)
            if len(self.selected) > 0:
                if keys(key.DELETE): delete_images(self)
                if keys("dir"): move_selected_images(self,dx,dy)
                if keys("dir",alt=True): move_selected_images_sticky(self,dx,dy)


