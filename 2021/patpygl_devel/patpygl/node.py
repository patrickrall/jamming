from math import floor,ceil
import glfw
from .listen import *
from .matrix import *
from OpenGL.GL import *

# Node
# PaddingNode
# HintedNode
# RowsNode
# ColsNode

###########################################################

# set the window's maximum and minimum size according to the node's requirements
# also build the node's layout according to the current window size.
def node_window_fit(node,window):
    minw, minh, maxw, maxh = node.layout_hints()

    def maxproc(x):
        if x == float('inf'): return 10000
        return floor(x)

    glfw.set_window_size_limits(window, ceil(minw), ceil(minh), maxproc(maxw),maxproc(maxh))

    w,h = glfw.get_framebuffer_size(window)
    dimx = max(min(w,maxw),minw)
    dimy = max(min(h,maxh),minh)
    node.set_layout(0,0,dimx,dimy)

###########################################################

global node_counter
node_counter = 0

class Node():

    def __init__(self, key=None, children=[]):

        global node_counter
        self.count = str(node_counter)+"_"
        node_counter += 1

        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.key = key

        assert isinstance(children,list)
        self.children = children


    def __getitem__(self, key):
        if self.key == key: return self

        for child in self.children:
            node = child[key]
            if node is not None: return node

        return None


    def draw(self):
        dispatch(self.count+"on_draw")

        for child in self.children:
            child.draw()

    def layout_hints(self,mydims=None):
        # mydims is a tuple of minw, minh, maxw, maxh
        # will be taken into consideration as if it were another child

        minw, minh, maxw, maxh = 0,0,float('inf'),float('inf')

        child_max_dims_list = []

        # make minw,minh the largest of the children's minima
        for child in self.children:
            cminw,cminh,cmaxw,cmaxh = child.layout_hints()
            child_max_dims_list.append((cmaxw,cmaxh))
            if cminw > minw: minw = cminw
            if cminh > minh: minh = cminh

        if mydims is not None:
            myminw,myminh,mymaxw,mymaxh = mydims
            minw = max(myminw,minw)
            minh = max(myminh,minh)

        # make maxw,maxh be the smallest of the children's maxima,
        # privided those maxima are not already smaller than the minimum
        for (cmaxw,cmaxh) in child_max_dims_list:
            if cmaxw < maxw and cmaxw >= minw: maxw = cmaxw
            if cmaxh < maxh and cmaxh >= minh: maxh = cmaxh

        if mydims is not None:
            if mymaxw < maxw and mymaxw >= minw: maxw = mymaxw
            if mymaxh < maxh and mymaxh >= minh: maxh = mymaxh

        return minw, minh, maxw, maxh

    def _update_dimensions_with_events(self,x,y,width,height):
        should_move = self.x != x or self.y != y
        should_resize = self.width != width or self.height != height
        self.x, self.y, self.width, self.height = x,y,width,height
        if should_move: dispatch(self.count+"on_move",x,y)
        if should_resize: dispatch(self.count+"on_resize",width,height)


    def set_layout(self,x,y,width,height,onlychildren=False):
        # sometimes subclasses call set_layout just to set the children's dimensions.
        if not onlychildren:
            self._update_dimensions_with_events(x,y,width,height)

        for child in self.children:
            _, _, cmaxw, cmaxh = child.layout_hints()
            cw = min(cmaxw, width)

            sy = 0
            ch = height
            if ch > cmaxh:
                sy += int(ch - cmaxh)
                ch = cmaxh

            child.set_layout(x,y+sy,cw,ch)


    ############### Events

    def on_draw(self):
        event, *data = yield [self.count + "on_draw"]
        return data

    def on_resize(self):
        event, *data = yield [self.count + "on_resize"]
        return data

    def on_move(self):
        event, *data = yield [self.count + "on_move"]
        return data

##################################################################

class PaddingNode(Node):

    def __init__(self, all=None,
                       top=None, bottom=None,
                       left=None, right=None,
                       horizontal=None, vertical=None, **kwargs):
        super().__init__(**kwargs)

        self.padding = {"top": "*", "bottom":"*", "left":"*", "right":"*"}

        if all is not None:
            assert isinstance(all,int) or all == "*"
            self.padding = {"top": all, "bottom":all, "left":all, "right":all}
            assert top is None
            assert bottom is None
            assert right is None
            assert left is None
            assert horizontal is None
            assert vertical is None

        if vertical is not None:
            assert isinstance(vertical,int) or vertical == "*"
            self.padding["top"] = vertical
            self.padding["bottom"] = vertical
            assert top is None
            assert bottom is None

        if top is not None:
            assert isinstance(top,int) or top == "*"
            self.padding["top"] = top

        if bottom is not None:
            assert isinstance(bottom,int) or bottom == "*"
            self.padding["bottom"] = bottom

        if horizontal is not None:
            assert isinstance(horizontal,int) or horizontal == "*"
            self.padding["left"] = horizontal
            self.padding["right"] = horizontal
            assert left is None
            assert right is None

        if left is not None:
            assert isinstance(left,int) or left == "*"
            self.padding["left"] = left

        if right is not None:
            assert isinstance(right,int) or right == "*"
            self.padding["right"] = right


    def set_layout(self,set_x,set_y,set_width,set_height):

        minw, minh, maxw, maxh = super().layout_hints()

        w = set_width
        x = 0

        if self.padding["left"] != "*":
            w -= self.padding["left"]
            x = self.padding["left"]
        if self.padding["right"] != "*":
            w -= self.padding["right"]

        if maxw < w:
            if self.padding["left"] == "*" and self.padding["right"] == "*":
                x += int((w-maxw)/2)
            elif self.padding["left"] == "*":
                x += w-maxw

            if self.padding["left"] == "*" or self.padding["right"] == "*":
                w = maxw

        h = set_height
        y = 0

        if self.padding["bottom"] != "*":
            h -= self.padding["bottom"]
            y = self.padding["bottom"]
        if self.padding["top"] != "*":
            h -= self.padding["top"]

        if maxh < h:
            if self.padding["bottom"] == "*" and self.padding["top"] == "*":
                y += int((h-maxh)/2)
            elif self.padding["bottom"] == "*":
                y += h-maxh

            if self.padding["bottom"] == "*" or self.padding["top"] == "*":
                h = maxh

        self._update_dimensions_with_events(set_x,set_y,set_width,set_height)
        super().set_layout(set_x+x, set_y+y, w, h,onlychildren=True)

    def layout_hints(self):
        minw, minh, maxw, maxh = super().layout_hints()

        if self.padding["left"] == "*" or self.padding["right"] == "*":
            maxw = float('inf')

        if self.padding["top"] == "*" or self.padding["bottom"] == "*":
            maxh = float('inf')

        def de_star(x):
            if x == "*": return 0
            return x

        extraw = de_star(self.padding["left"]) + de_star(self.padding["right"])
        extrah = de_star(self.padding["top"]) + de_star(self.padding["bottom"])
        return minw+extraw, minh+extrah, maxw+extraw, maxh+extrah

##################################################################

class HintedNode(Node):
    def __init__(self,  minw=None, maxw=None, minh=None, maxh=None, width=None, height=None,**kwargs):
        super().__init__(**kwargs)

        self.dims = {"minw": "*", "maxw":"*", "minh":"*", "maxh":"*"}

        if width is not None:
            assert isinstance(width,int) or width == "*"
            self.dims["minw"] = width
            self.dims["maxw"] = width
            assert minw is None
            assert maxw is None

        if maxw is not None:
            assert isinstance(maxw,int) or maxw == "*"
            self.dims["maxw"] = maxw

        if minw is not None:
            assert isinstance(minw,int) or minw == "*"
            self.dims["minw"] = minw

        if height is not None:
            assert isinstance(height,int) or height == "*"
            self.dims["minh"] = height
            self.dims["maxh"] = height
            assert minh is None
            assert maxh is None

        if maxh is not None:
            assert isinstance(maxh,int) or maxh == "*"
            self.dims["maxh"] = maxh

        if minh is not None:
            assert isinstance(minh,int) or minh == "*"
            self.dims["minh"] = minh


    def layout_hints(self):
        def inherit(v,w):
            if v == "*": return w
            return v

        minw, minh, maxw, maxh = super().layout_hints()

        return inherit(self.dims["minw"], minw), inherit(self.dims["minh"], minh),\
               inherit(self.dims["maxw"], maxw), inherit(self.dims["maxh"], maxh)


##################################################################

# helper function that distributes a bunch of elements in one dimension
# according to their minimum and maximum lengths
def _distribute_layout(mins,maxs,length):
    n = len(mins)
    lengths = [mins[i] for i in range(n)]
    length -= sum(lengths)

    if length == 0: return lengths

    diffs = set([maxs[i] - mins[i] for i in range(n)])

    while True:
        if len(diffs) == 0: break
        size = min(diffs)
        diffs.remove(size)

        if size == 0: continue

        num = len([i for i in range(len(mins)) if maxs[i]-lengths[i] >= size])

        if num*size < length:
            for i in range(n):
                if maxs[i]-lengths[i] >= size: lengths[i] += size
            length -= num*size
        else:
            to_add = floor(length/num)
            for i in range(n):
                if maxs[i]-lengths[i] >= size: lengths[i] += to_add
            break

    return lengths


class RowsNode(Node):

    def set_layout(self,x,y,width,height):
        self._update_dimensions_with_events(x,y,width,height)

        mins = []
        maxs = []
        widths = []

        children = list(reversed(self.children))

        for child in children:
            cminw, cminh, cmaxw, cmaxh = child.layout_hints()
            mins.append(cminh)
            maxs.append(cmaxh)
            widths.append(min(width,cmaxw))

        heights = _distribute_layout(mins,maxs,height)

        cheight = 0
        for i in range(len(children)):
            children[i].set_layout(x,y+cheight,widths[i],heights[i])
            cheight += heights[i]


    def layout_hints(self):
        minw, minh, maxw, maxh = 0,0,float('inf'),0
        maxs = []

        for child in self.children:
            cminw,cminh,cmaxw,cmaxh = child.layout_hints()

            if cminw > minw: minw = cminw
            maxs.append(cminw)

            minh += cminh
            maxh += cmaxh

        for cmaxw in maxs:
            if cmaxw < maxw and cmaxw >= minw:
                maxw = maxw

        return minw, minh, maxw, maxh



class ColsNode(Node):

    def set_layout(self,x,y,width,height):
        self._update_dimensions_with_events(x,y,width,height)

        mins = []
        maxs = []
        heights = []

        children = self.children

        for child in children:
            cminw, cminh, cmaxw, cmaxh = child.layout_hints()
            mins.append(cminw)
            maxs.append(cmaxw)
            heights.append(min(height,cmaxh))

        widths = _distribute_layout(mins,maxs,width)

        cwidth = 0
        for i in range(len(self.children)):
            children[i].set_layout(x+cwidth,y+height-heights[i],widths[i],heights[i])
            cwidth += widths[i]


    def layout_hints(self):
        minw, minh, maxw, maxh = 0,0,0,float('inf')
        maxs = []

        for child in self.children:
            cminw,cminh,cmaxw,cmaxh = child.layout_hints()

            if cminh > minh: minh = cminh
            maxs.append(cminh)

            minw += cminw
            maxw += cmaxw

        for cmaxh in maxs:
            if cmaxh < maxh and cmaxh >= minh:
                maxh = maxh

        return minw, minh, maxw, maxh



