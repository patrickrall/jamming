import pyglet
import json
from pyglet.gl import *
import math

from functools import wraps
import types


class NodeWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):

        # add a stencil buffer by default. needed by scroll views
        if "config" not in kwargs:
            kwargs["config"] = pyglet.gl.Config(stencil_size=8, double_buffer=True)

        self.listeners = []

        self._fps = 0

        self._basenode = AbstractNode() # add a top-level node
        self._basenode.window = self

        super().__init__(*args, **kwargs)

        # enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # convenience function
    def redraw(self):
        self.dispatch_event("on_draw")

    @property
    def node(self):
        if len(self._basenode.children) == 0: return self._basenode
        return self._basenode.children[0]

    @node.setter
    def node(self,newnode):
        if len(self._basenode.children) == 0:
             self._basenode.splice(0,0,[newnode])
        else:
             self._basenode.splice(0,1,[newnode])

    @node.deleter
    def node(self):
        self._basenode.splice(0,1)

    def on_expose(self):
        self.clear()
        default_draw(self._basenode)

    def on_draw(self):
        self.clear()
        default_draw(self._basenode)

    def on_show(self):
        rebuild_layout(self)

    def on_resize(self,w,h):
        super().on_resize(w,h) # hard-earned lesson: need to call super here
                               # or else graphics draw in the wrong place
        rebuild_layout(self)

    def on_key_press(self,symbol,modifiers):
        # this usually closes the window if symbol == ESCAPE. Disable that.
        pass


    #####################################

    # decorator
    def listener(self, func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            self.launch_listener(func, *args, **kwargs)
        return wrapper

    def launch_listener(self, func, *args, **kwargs):
        gen = func(*args,**kwargs)
        if isinstance(gen, types.GeneratorType):
            try:
                event = next(gen)
                self.listeners.append((event,gen))
            except StopIteration:
                pass

    def dispatch_event(self, event_name, *args, **kwargs):
        if event_name in super().event_types:
            super().dispatch_event(event_name, *args, **kwargs)


        # done in such a manner that a generator can't
        # invoke dispatch_event and call .send() to itself
        for i in range(len(self.listeners)):
            event,gen = self.listeners[i]

            del self.listeners[i]

            good = isinstance(event,str) and event_name == event
            good = good or isinstance(event,list) and event_name in event
            good = good or (event is None)

            if good:
                try:
                    next_event = gen.send((event_name,*args))
                    self.listeners.insert(i,(next_event,gen))
                except StopIteration:
                    pass
            else:
                self.listeners.insert(i,(event,gen))


        # also tell all the ListenerNodes
        if event_name is not "on_draw":
            for child in self._basenode.children_with_attr("dispatch"):
                child.dispatch(event_name,*args)


    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, new_fps):
        if self._fps != 0: pyglet.clock.unschedule(self.frame)
        self._fps = new_fps
        if self._fps != 0: pyglet.clock.schedule_interval(self.frame, 1/new_fps)

    def frame(self,dt):
        self.dispatch_event("on_frame",dt)


# decorator that uses first argument to get reference to window
def listener(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if not isinstance(args[0],pyglet.window.Window):
            raise ValueError("Listener decorator needs first argument of function to be a window.")
        args[0].launch_listener(func, *args, **kwargs)
    return wrapper

NodeWindow.register_event_type("on_frame")

##############################################


class AbstractNode():

    def __init__(self):
        self.parent = None
        self.children = []
        self._window = None

    @property
    def window(self): return self._window

    @window.setter
    def window(self,newWindow):
        self._window = newWindow
        for child in self.children:
            child.window = newWindow

    # implement these
    # def serialize(self)
    # def deserialize(self,data)

    ###########################

    # this just exists to keep track of self.window and self.parent

    def splice(self,idx,count,newnodes=[]):
        assert(count >= 0)
        assert(idx >= 0)

        # TODO: error handling for duplicates

        popped = []
        for i in range(count):
            popped.append(self.children.pop(idx))

        for p in popped:
            p.parent = None
            p.window = None

        for i in range(len(newnodes)):
            self.children.insert(idx+i, newnodes[i])
            newnodes[i].parent = self
            newnodes[i].window = self.window

        # trigger resizing of layout
        if self.window is not None:
            rebuild_layout(self.window)

    def add_child(self,node):
        self.splice(len(self.children),0,[node])

    ###########################

    def children_with_attr(self, *fnames):
        out = ()
        for child in self.children:
            if any([hasattr(child, fname) for fname in fnames]): out += (child,)
            else: out += child.children_with_attr(*fnames)
        return out

    def parent_with_attr(self, *fnames):
        if self.parent is None: return None
        if any([hasattr(self.parent,fname) in fnames]): return self.parent
        return self.parent.parent_with_attr(*fnames)


#####################

def default_draw(node):
    for child in node.children_with_attr("draw"):
        child.draw()

###################


def serialize_node(node):
    out = node.__class__.__name__
    if hasattr(node,"serialize"):
        out += " " + json.dumps(node.serialize())
    out += "\n"

    for child in node.children:
        childserial = serialize_node(child).split("\n")
        for line in childserial:
            if len(line) == 0: continue
            out += "-" + line + "\n"

    return out


# extra syntax:
# varname NodeClass {<data>} reads the node into a key called varname
# pass function as kwarg for quick assembly

def deserialize_node(text, **kwargs):
    keys = {}
    classes = {cls.__name__:cls  for cls in AbstractNode.__subclasses__()}

    while True:
        anyAdded = False
        for key in list(classes.keys()):
            for cls in classes[key].__subclasses__():
                if cls.__name__ not in classes:
                    classes[cls.__name__] = cls
                    anyAdded = True

        if not anyAdded: break

    classes["AbstractNode"] = AbstractNode

    def parse_line(line):
        if "#" in line: line = line.split("#")[0]
        line = line.strip()

        line = line.split(" ")

        keyname = None
        keyvalue = None

        if line[0] not in classes and line[0] not in kwargs:
            keyname = line[0]
            line = line[1:]


        if len(line) == 0:
            # NOTE: this error can sometimes happen if node.py is autoreloaded
            raise ValueError("No such class or function: '"+keyname+"'")


        if line[0] not in classes:
            if line[0] not in kwargs:
                # NOTE: this error can sometimes happen if node.py is autoreloaded
                raise ValueError("No such class or function: '"+keyname+"'")
            else:
                n_args = []
                n_kwargs = {}
                if len(line) > 1:
                    rest = json.loads(" ".join(line[1:]))
                    if isinstance(rest,dict): n_kwargs = rest
                    elif isinstance(rest,list): n_args = rest
                    else: n_args = [rest]

                out = kwargs[line[0]](*n_args,**n_kwargs)
                if isinstance(out,tuple):
                    node = out[0]
                    keyvalue = out[1]
                else:
                    node = out
                    keyvalue = out

                line = line[1:]
        else:
            node = classes[line[0]]()
            line = line[1:]

            if len(line) > 0:
                rest = " ".join(line)
                node.deserialize(json.loads(rest))
            keyvalue = node

        return node, keyname, keyvalue

    lines = text.split("\n")


    # trim start
    while len(lines[0]) == 0:
        lines = lines[1:]

    top, keyname, keyvalue = parse_line(lines[0])

    if keyname is not None: keys[keyname] = keyvalue

    linebuffer = ""
    for line in lines[1:]:
        line = line.strip()
        if len(line) == 0: continue

        if line[1] == "-":
            linebuffer += line[1:] + "\n"
        else:
            if linebuffer != "":
                node, otherkeys = deserialize_node(linebuffer, **kwargs)
                top.add_child(node)
                for key in otherkeys:
                    if key in keys: raise ValueError("Duplicate keyname '"+key+"'")
                    keys[key] = otherkeys[key]
            linebuffer = line[1:] + "\n"

    if linebuffer != "":
        node, otherkeys = deserialize_node(linebuffer, **kwargs)
        top.add_child(node)
        for key in otherkeys:
            if key in keys: raise ValueError("Duplicate keyname '"+key+"'")
            keys[key] = otherkeys[key]

    return top, keys

#########################


class Vector2():
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __add__(self,other):
        return Vector2(self.x+other.x,self.y+other.y)

    def __sub__(self,other):
        return Vector2(self.x-other.x,self.y-other.y)

    def __eq__(self,other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return "Vector2("+str(self.x)+","+str(self.y)+")"


########################


def rebuild_layout(window):
    min_dims, max_dims = default_layout_hints(window._basenode)
    window.set_minimum_size(math.ceil(min_dims.x),math.ceil(min_dims.y))

    def maxproc(x):
        if x == float('inf'): return 10000
        return math.floor(x)

    window.set_maximum_size(maxproc(max_dims.x),maxproc(max_dims.y))

    w,h = window.get_size()
    dims = Vector2(max(min(w,max_dims.x),min_dims.x),max(min(h,max_dims.y),min_dims.y))

    default_set_layout(window._basenode,Vector2(0,0),dims)
    if hasattr(window.node, "draw"): window.node.draw()
    else: default_draw(window.node)



def default_set_layout(self,pos,dims):

    for child in self.children_with_attr("set_layout"):
        if hasattr(child, "layout_hints"):
            _, child_max_dims = child.layout_hints()
        else:
            _, child_max_dims = default_layout_hints(self)

        shift = Vector2(0,0)
        xdims = min(child_max_dims.x, dims.x)

        # put child in top left corner rather than bottom left
        ydims = dims.y
        if ydims > child_max_dims.y:
            shift.y += int(ydims-child_max_dims.y)
            ydims = child_max_dims.y

        child.set_layout(pos+shift,Vector2(xdims,ydims))


# convenience: provide my_min_dims and my_max_dims as arguments
def default_layout_hints(self,*args):
    min_dims = Vector2(0,0) # max of children
    max_dims = Vector2(float('inf'),float('inf')) # min of children larger than min_dims

    child_max_dims_list = []

    for child in self.children_with_attr("layout_hints"):
        child_min_dims, child_max_dims = child.layout_hints()
        child_max_dims_list.append(child_max_dims)
        if child_min_dims.x > min_dims.x: min_dims.x = child_min_dims.x
        if child_min_dims.y > min_dims.y: min_dims.y = child_min_dims.y

    if len(args) == 2:
        my_min_dims, my_max_dims = args
        min_dims.x = max(my_min_dims.x,min_dims.x)
        min_dims.y = max(my_min_dims.y,min_dims.y)

    for child_max_dims in child_max_dims_list:
        if child_max_dims.x < max_dims.x and child_max_dims.x >= min_dims.x: max_dims.x = child_max_dims.x
        if child_max_dims.y < max_dims.y and child_max_dims.y >= min_dims.y: max_dims.y = child_max_dims.y

    if len(args) == 2:
        my_min_dims, my_max_dims = args

        if my_max_dims.x >= min_dims.x: max_dims.x = min(max_dims.x, my_max_dims.x)
        if my_max_dims.y >= min_dims.y: max_dims.y = min(max_dims.y, my_max_dims.y)

    return min_dims, max_dims



