
from .node import *
import math
from pyglet.gl import *

######### Contains various useful nodes for layout

# BackgroundNode
# ListenerNode
# HintedLayoutNode
# PaddingLayoutNode
# ForceMinLayoutNode
# RowsLayoutNode
# ColsLayoutNode
# ScrollLayoutNode
# BlocksLayoutNode

###################################################

class BackgroundNode(AbstractNode):
    def __init__(self):
        super().__init__()
        self.color = (255,255,255,255)
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)

    def serialize(self):
        return list(self._color)

    def deserialize(self,data):
        self.color = tuple(data)

    def draw(self):
        if self.color[3] != 255:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(self.color[0]/255, self.color[1]/255, self.color[2]/255, self.color[3]/255)
        glRectf(self.pos.x,self.pos.y,self.pos.x+self.dims.x,self.pos.y+self.dims.y)

        default_draw(self)

    def set_layout(self,pos,dims):
        default_set_layout(self,pos,dims)
        self.pos = pos
        self.dims = dims

    def layout_hints(self):
        return default_layout_hints(self)



#################################################

# a node that can keep a listener up to date
class ListenerNode(AbstractNode):
    def __init__(self):
        super().__init__()
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)
        self._listener = None
        self._listening_for = []

    @property
    def listener(self): return self._listener

    @listener.setter
    def listener(self, func, *args, **kwargs):
        self._listener = None

        gen = func(*args,**kwargs)
        if isinstance(gen, types.GeneratorType):
            try:
                event = next(gen)
                self._listener = gen
                self._listening_for = event

                # send an on_layout event on init so the listener can know
                self.dispatch("on_layout",self.pos.x,self.pos.y,self.dims.x,self.dims.y)
            except StopIteration:
                pass

    def dispatch(self, event_name,*args):
        event = self._listening_for

        good = isinstance(event,str) and event_name == event
        good = good or isinstance(event,list) and event_name in event
        good = good or (event is None)

        if good:
            try:
                next_event = self._listener.send((event_name,*args))
                self._listening_for = next_event
            except StopIteration:
                self._listener = None
                self._listening_for = []

    def draw(self):
        self.dispatch("on_draw")
        default_draw(self)

    def set_layout(self,pos,dims):
        default_set_layout(self,pos,dims)
        self.pos = pos
        self.dims = dims

        self.dispatch("on_layout",pos.x,pos.y,dims.x,dims.y)

    def layout_hints(self):
        return default_layout_hints(self)

###################################################

# a node where you can specify mindims and maxdims
# type "*" to inherit the propertyy from the children
class HintedLayoutNode(AbstractNode):
    def __init__(self):
        super().__init__()
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)
        self.mindims = Vector2("*","*")
        self.maxdims = Vector2("*","*")

    def serialize(self):
        return [self.mindims.x,self.maxdims.x,self.mindims.y,self.maxdims.y]

    def deserialize(self,data):
        if isinstance(data,int):
            self.mindims.x = data
            self.maxdims.x = data
            self.mindims.y = data
            self.maxdims.y = data
        else:
            assert(isinstance(data,list))
            if len(data) == 2:
                self.mindims.x = data[0]
                self.maxdims.x = data[0]
                self.mindims.y = data[1]
                self.maxdims.y = data[1]
            elif len(data) == 4:
                self.mindims.x = data[0]
                self.maxdims.x = data[1]
                self.mindims.y = data[2]
                self.maxdims.y = data[3]
            else:
                raise ValueError("Bad data for layout hints: "+str(data))

    def set_layout(self,pos,dims):
        default_set_layout(self,pos,dims)
        self.pos = pos
        self.dims = dims

    def layout_hints(self):
        def inherit(v,w):
            if v == "*": return w
            return v

        c_mindims, c_maxdims = default_layout_hints(self)

        mindims = Vector2(inherit(self.mindims.x, c_mindims.x), inherit(self.mindims.y, c_mindims.y))
        maxdims = Vector2(inherit(self.maxdims.x, c_maxdims.x), inherit(self.maxdims.y, c_maxdims.y))
        return mindims,maxdims


# padding can be a positive number or "*"
# if "*", then the max_width is infinite in that direction
# and padding fills in the rest of the space
class PaddingLayoutNode(AbstractNode):
    def __init__(self):
        super().__init__()
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)
        self.padding = {"top":"*", "bottom":"*", "left":"*", "right":"*"}

    def serialize(self):
        return self.padding

    def deserialize(self,data):
        if isinstance(data,dict):
            self.padding = data
        elif isinstance(data,int) or isinstance(data,str):
            self.padding = {"top":data, "bottom":data, "left":data, "right":data}
        else:
            assert(isinstance(data,list))
            if len(data) == 2:
                self.padding = {"top":data[0], "bottom":data[0], "left":data[1], "right":data[1]}
            elif len(data) == 4:
                # top right bottom left. HTML convention.
                self.padding = {"top":data[0], "right":data[1], "bottom":data[2], "left":data[3]}
            else:
                raise ValueError("Bad data for padding: "+str(data))


    def set_layout(self,pos,dims):
        self.pos = pos
        self.dims = dims

        min_dims, max_dims = default_layout_hints(self)

        w = dims.x
        x = 0

        if self.padding["left"] != "*":
            w -= self.padding["left"]
            x = self.padding["left"]
        if self.padding["right"] != "*":
            w -= self.padding["right"]

        if max_dims.x < w:
            if self.padding["left"] == "*" and self.padding["right"] == "*":
                x += int((w-max_dims.x)/2)
            elif self.padding["left"] == "*":
                x += w-max_dims.x

            if self.padding["left"] == "*" or self.padding["right"] == "*":
                w = max_dims.x

        h = dims.y
        y = 0

        if self.padding["bottom"] != "*":
            h -= self.padding["bottom"]
            y = self.padding["bottom"]
        if self.padding["top"] != "*":
            h -= self.padding["top"]

        if max_dims.y < h:
            if self.padding["bottom"] == "*" and self.padding["top"] == "*":
                y += int((h-max_dims.y)/2)
            elif self.padding["bottom"] == "*":
                y += h-max_dims.y

            if self.padding["bottom"] == "*" or self.padding["top"] == "*":
                h = max_dims.y

        default_set_layout(self, pos+Vector2(x,y), Vector2(w,h))

    def layout_hints(self):
        min_dims, max_dims = default_layout_hints(self)

        if self.padding["left"] == "*" or self.padding["right"] == "*":
            max_dims.x = float('inf')

        if self.padding["top"] == "*" or self.padding["bottom"] == "*":
            max_dims.y = float('inf')

        def de_star(x):
            if x == "*": return 0
            return x

        extraw = de_star(self.padding["left"]) + de_star(self.padding["right"])
        extrah = de_star(self.padding["top"]) + de_star(self.padding["bottom"])
        extra = Vector2(extraw,extrah)
        return min_dims + extra, max_dims+extra


class ForceMinLayoutNode(AbstractNode):
    def __init__(self):
        super().__init__()
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)
        self.which_dims = "XY"

    def serialize(self):
        return self.which_dims

    def deserialize(self,data):
        self.which_dims = data

    def set_layout(self,pos,dims):
        self.pos = pos
        self.dims = dims
        default_set_layout(self,pos,dims)

    def layout_hints(self):
        c_min_dims, c_max_dims = default_layout_hints(self)
        max_dims = Vector2(0,0)
        if "X" in self.which_dims: max_dims.x = c_min_dims.x
        else: max_dims.x = c_max_dims.x

        if "Y" in self.which_dims: max_dims.y = c_min_dims.y
        else: max_dims.y = c_max_dims.y

        return c_min_dims, max_dims

####################################################


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
            to_add = math.floor(length/num)
            for i in range(n):
                if maxs[i]-lengths[i] >= size: lengths[i] += to_add
            break

    return lengths


class RowsLayoutNode(AbstractNode):
    def __init__(self):
        super().__init__()
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)

    def set_layout(self,pos,dims):
        self.pos = pos
        self.dims = dims

        mins = []
        maxs = []
        widths = []

        children = list(reversed(self.children_with_attr("set_layout")))

        for child in children:
            if hasattr(child, "layout_hints"):
                child_min_dims, child_max_dims = child.layout_hints()
            else:
                child_min_dims, child_max_dims = default_layout_hints(self)

            mins.append(child_min_dims.y)
            maxs.append(child_max_dims.y)
            widths.append(min(dims.x,child_max_dims.x))

        heights = _distribute_layout(mins,maxs,dims.y)

        height = 0
        for i in range(len(children)):
            children[i].set_layout(Vector2(pos.x,pos.y+height),Vector2(widths[i],heights[i]))
            height += heights[i]


    def layout_hints(self):
        min_dims = Vector2(0,0)
        max_dims = Vector2(float('inf'),0)
        maxs = []

        for child in self.children_with_attr("layout_hints"):
            child_min_dims, child_max_dims = child.layout_hints()

            if child_min_dims.x > min_dims.x: min_dims.x = child_min_dims.x
            maxs.append(child_max_dims.x)

            min_dims.y += child_min_dims.y
            max_dims.y += child_max_dims.y

        for maxx in maxs:
            if maxx < max_dims.x and maxx >= min_dims.x:
                max_dims.x = maxx

        return min_dims, max_dims





class ColsLayoutNode(AbstractNode):

    def __init__(self):
        super().__init__()
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)

    def set_layout(self,pos,dims):
        self.pos = pos
        self.dims = dims

        mins = []
        maxs = []
        heights = []

        children = self.children_with_attr("set_layout")

        for child in children:
            child_min_dims, child_max_dims = child.layout_hints()
            mins.append(child_min_dims.x)
            maxs.append(child_max_dims.x)
            heights.append(min(dims.y,child_max_dims.y))

        widths = _distribute_layout(mins,maxs,dims.x)

        width = 0
        for i in range(len(children)):
            children[i].set_layout(Vector2(pos.x+width,pos.y),Vector2(widths[i],heights[i]))
            width += widths[i]


    def layout_hints(self):
        min_dims = Vector2(0,0)
        max_dims = Vector2(0,float('inf'))
        maxs = []
        for child in self.children_with_attr("layout_hints"):
            child_min_dims, child_max_dims = child.layout_hints()

            if child_min_dims.y > min_dims.y: min_dims.y = child_min_dims.y
            maxs.append(child_max_dims.y)

            min_dims.x += child_min_dims.x
            max_dims.x += child_max_dims.x

        for maxy in maxs:
            if maxy < max_dims.y and maxy >= min_dims.y:
                max_dims.y = maxy

        return min_dims, max_dims


############################ Scrolling

# assumes node has pos,dims,translate properties
def draw_with_stencil(node):

    glEnable(GL_STENCIL_TEST)
    glClearStencil(0)
    glClear(GL_STENCIL_BUFFER_BIT)

    glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
    glDepthMask(GL_FALSE)

    glStencilMask(0xFF)

    glStencilFunc(GL_ALWAYS, 0xFF, 0xFF)
    glStencilOp(GL_REPLACE, GL_REPLACE, GL_REPLACE)

    glColor4f(1.0,1.0,1.0,1.0)
    glRectf(node.pos.x,node.pos.y,node.pos.x+node.dims.x,node.pos.y+node.dims.y)

    glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
    glDepthMask(GL_TRUE)

    glStencilFunc(GL_EQUAL, 0xFF, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

    glPushMatrix()
    glTranslatef(-node.translate.x, node.translate.y,0)

    default_draw(node)

    glPopMatrix()

    glDisable(GL_STENCIL_TEST)


class ScrollLayoutNode(AbstractNode):
    def __init__(self):
        super().__init__()
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)
        self.which_dims = "XY"
        self.translate = Vector2(0,0)
        self.max_translate = Vector2(0,0)

    def serialize(self):
        return self.which_dims

    def deserialize(self,data):
        self.which_dims = data

    def draw(self):
        draw_with_stencil(self)

    def set_layout(self,pos,dims):
        self.pos = pos
        self.dims = dims

        c_min_dims, c_max_dims = default_layout_hints(self)
        c_pos = Vector2(pos.x,pos.y)
        c_dims = Vector2(dims.x,dims.y)

        if "X" in self.which_dims:
            if c_max_dims.x == float('inf'):
                c_dims.x = max(c_min_dims.x, dims.x)
            else:
                c_dims.x = c_max_dims.x
            self.max_translate.x = max(0, c_dims.x-dims.x)

        if "Y" in self.which_dims:
            if c_max_dims.y == float('inf'):
                c_dims.y = max(c_min_dims.y, dims.y)
            else:
                c_dims.y = c_max_dims.y

            c_pos.y += dims.y - c_dims.y # regardless of if dimsy < dims.y

            self.max_translate.y = max(0, c_dims.y-dims.y)

        self.translate.x = min(self.translate.x, self.max_translate.x)
        self.translate.y = min(self.translate.y, self.max_translate.y)

        default_set_layout(self,c_pos,c_dims)

    def layout_hints(self):
        c_min_dims, c_max_dims = default_layout_hints(self)

        min_dims = Vector2(10,10)
        max_dims = Vector2(float('inf'),float('inf'))


        if "X" not in self.which_dims:
            min_dims.x, max_dims.x = c_min_dims.x, c_max_dims.x

        if "Y" not in self.which_dims:
            min_dims.y, max_dims.y = c_min_dims.y, c_max_dims.y

        return min_dims, max_dims


class BlocksLayoutNode(AbstractNode):

    def __init__(self):
        super().__init__()
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)
        self.translate = Vector2(0,0)
        self.max_translate = Vector2(0,0)

    def draw(self):
        draw_with_stencil(self)

    def set_layout(self,pos,dims):
        self.pos = pos
        self.dims = dims

        line_x = 0
        line_y = dims.y
        line_h = 0

        children = self.children_with_attr("set_layout")
        for child in children:
            cdims, _ = child.layout_hints()

            if cdims.x + line_x > dims.x:
                line_x = 0
                line_y -= line_h
                line_h = cdims.y
            else:
                if line_h < cdims.y: line_h = cdims.y

            child.set_layout(pos+Vector2(line_x, line_y-cdims.y),cdims)
            line_x += cdims.x

        self.max_translate.y = max(0, -line_y+line_h)
        self.translate.y = min(self.translate.y, self.max_translate.y)


    def layout_hints(self):
        min_w = 0
        min_h = 0

        children = self.children_with_attr("layout_hints")
        for child in children:
            cdims, _ = child.layout_hints()
            if cdims.x > min_w: min_w = cdims.x
            if cdims.y > min_h: min_h = cdims.y

        min_dims = Vector2(min_w,min_h)
        max_dims = Vector2(float('inf'),float('inf'))
        return min_dims, max_dims
