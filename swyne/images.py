
import json
import pyglet
from pyglet.gl import *
from .node import *
from .layout import *

# TODO: image animation is using pyglet.clock.schedule
# instead use listener here

def load_spritesheet(sheet_fname):
    data_file = pyglet.resource.file(sheet_fname)
    data = json.loads(data_file.read())

    # TODO: need to pre-process path?
    image = pyglet.resource.image(data["meta"]["image"])
    h = image.height

    frames = []

    for key in data["frames"].keys():
        frame = data["frames"][key]["frame"]

        animframe = pyglet.image.AnimationFrame(
                image.get_region(frame["x"],h-frame["y"]-frame["h"],frame["w"],frame["h"]),
                duration=data["frames"][key]["duration"]/1000) # convert to seconds

        frames.append(animframe)

    out = {}

    for tag in data["meta"]["frameTags"]:
        # no support for direction tag

        animframes = []

        i = tag["from"]
        while i <= tag["to"]:
            animframes.append(frames[i])
            i += 1

        out[tag["name"]] = pyglet.image.Animation(frames=animframes)

    return out


# turn animation into hex data and back
def serialize_image(image):
    imgdata = image.get_image_data()

    hexdata = bytes(imgdata.get_data('RGBA',imgdata.width*4)).hex()


    colors = []
    for i in range(int(len(hexdata)/8)):
        i = i*8
        c = hexdata[i:i+8]
        if c not in colors:
            colors.append(c)
            if len(colors) > 15:
                colors = []
                break

    c_count = '{:1x}'.format(len(colors))

    if len(colors) == 0:
        # give up
        chexdata = hexdata
    else:
        chexdata = "".join(colors)
        current = None
        count = 0
        for i in range(int(len(hexdata)/8)):
            i *= 8
            if hexdata[i:i+8] == current and count < 15:
                count += 1
            else:
                if current is not None:
                    chexdata += ('{:1x}').format(count) + ('{:1x}').format(colors.index(current))
                current = hexdata[i:i+8]
                count = 1
        if current is not None:
            chexdata += ('{:1x}').format(count) + ('{:1x}').format(colors.index(current))

    w = '{:4x}'.format(image.width).replace(" ","0")
    h = '{:4x}'.format(image.height).replace(" ","0")

    return w+h+c_count+chexdata


def deserialize_image(data):
    w = int(data[:4].strip(),16)
    h = int(data[4:8].strip(),16)
    c_count = int(data[8:9].strip(),16)
    chexdata = data[9:]

    if c_count == 0:
        hexdata = chexdata
    else:
        colors = []
        for i in range(c_count):
            i *= 8
            colors.append(chexdata[i:i+8])
        chexdata = chexdata[c_count*8:]

        hexdata = ""
        for i in range(int(len(chexdata)/2)):
            i *= 2
            hexdata += int(chexdata[i],16)*colors[int(chexdata[i+1],16)]

    image = pyglet.image.ImageData(w,h,'RGBA',bytes.fromhex(hexdata))
    return image

def serialize_animation(anim):
    def dur_str(dur):
        if dur is None: return 'None'
        return str(int(dur*1000))
    out = [ dur_str(frame.duration) + ":" + serialize_image(frame.image) for frame in anim.frames]
    return ";".join(out)

def deserialize_animation(data):
    frames = []
    for framedata in data.split(";"):
        spl = framedata.split(":")
        if spl[0] == "None": duration = None
        else: duration = int(spl[0])
        animframe = pyglet.image.AnimationFrame(deserialize_image(framedata.split(":")[1]),
                duration=duration)
        frames.append(animframe)
    return pyglet.image.Animation(frames=frames)

class AnimatedNode(AbstractNode):

    def __init__(self):
        super().__init__()

        self.texture = None
        self._animation = None
        self.pos = Vector2(0,0)
        self.dims = Vector2(0,0)
        self._frame_idx = 0
        self._next_dt = 0
        self._scale = 1
        self.vertex_list = None

    def serialize(self):
        return serialize_animation(self._animation)

    def deserialize(self,data):
        self.animation = deserialize_animation(data)

    @property
    def animation(self):
        return self._animation

    @animation.setter
    def animation(self,newanimation):
        if self._animation:
            pyglet.clock.unschedule(self._animate)

        self._animation = newanimation
        self._frame_idx = 0
        self._next_dt = newanimation.frames[0].duration
        self._set_texture(newanimation.frames[0].image.get_texture())

        if self._next_dt:
            pyglet.clock.schedule_once(self._animate,self._next_dt)

    @property
    def scale(self): return self._scale

    @scale.setter
    def scale(self, newscale):
        self._scale = newscale
        if self.texture is not None:
            self._set_texture(self.texture)


    def set_layout(self,pos,dims):
        self.pos = pos
        self.dims = dims
        default_set_layout(self, pos,dims)
        if self.texture is not None:
            self._set_texture(self.texture)

    def layout_hints(self):
        if self._animation is None:
            dims = Vector2(0,0)
        else:
            dims = Vector2(self._animation.get_max_width()*self._scale,
                    self._animation.get_max_height()*self._scale)
        return dims,dims

    def _set_texture(self,texture):
        x = int(self.pos.x)
        y = int(self.pos.y)
        w = texture.width*self._scale
        h = texture.height*self._scale

        vertices = x,y,0,x+w,y,0,x+w,y+h,0,x,y+h,0

        if self.vertex_list is not None: self.vertex_list.delete()
        self.vertex_list = pyglet.graphics.vertex_list_indexed(4,
                [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', texture.tex_coords))
        self.texture = texture


    def _animate(self,dt):
        self._frame_idx += 1
        if self._frame_idx >= len(self._animation.frames):
            self._frame_idx = 0

        frame = self._animation.frames[self._frame_idx]
        self._set_texture(frame.image.get_texture())

        if frame.duration is not None:
            duration = frame.duration - (self._next_dt - dt)
            duration = min(max(0, duration), frame.duration)
            pyglet.clock.schedule_once(self._animate, duration)
            self._next_dt = duration


    def draw(self):
        if self.vertex_list is None:
            default_draw(self)
            return

        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)


        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.vertex_list.draw(GL_TRIANGLES)

        glPopAttrib()
        glDisable(self.texture.target)

        default_draw(self)
