import time, json, os
from OpenGL.GL import *
from PIL import Image
from .vector import Vec


# turns an image into a frame dictionary
def load_png(fname):
    img = Image.open(fname)
    width, height = img.size

    pixels = img.tobytes()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    if img.mode not in ["RGB", "RGBA"]:
        img = img.convert("RGBA")
    if img.mode == "RGB":
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixels)
    else:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels)

    glBindTexture(GL_TEXTURE_2D, 0)

    return {
        "texture": texture,
        "duration": 1, # 1 second
        "w": width, "h": height,
        "texcoords": { "tl": Vec(0,0), "tr": Vec(1,0),
                        "bl": Vec(0,1),"br": Vec(1,1),
        },
    }


# Returns a list of frames, each is a dict with
# {
#  "w": 100
#  "h": 100
#  "duration": 100 (in ms)
#  "texture": number pointing to the opengl texture
#  "texcoords": {"tl":Vec(2), "tr":Vec(2), "bl":Vec(2), "br":Vec(2)}
# }
# And also a dictionary for the sheet
#   where the keys are the names of FrameTags#
#   and the values are a list of frames

def load_spritesheet(fname):
    with open(fname) as f:
        data = json.loads(f.read())

    assert int(data["meta"]["scale"]) == 1
    assert "frameTags" in data["meta"]

    # load the texture

    image_path = os.path.join(os.path.dirname(fname), data["meta"]["image"])
    img = Image.open(image_path)
    width, height = img.size

    assert width == data["meta"]["size"]["w"]
    assert height == data["meta"]["size"]["h"]

    pixels = img.tobytes()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    if img.mode not in ["RGB", "RGBA"]:
        img = img.convert("RGBA")

    if img.mode == "RGB":
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixels)
    else:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels)

    glBindTexture(GL_TEXTURE_2D, 0)

    # load the texture coordinates

    frames = []
    for key in data["frames"].keys():
        ksig = " "+str(len(frames))+"."
        assert ksig in key

        x,y,w,h = [data["frames"][key]["frame"][k] for k in "xywh"]
        frame = {
            "texture": texture,
            "duration": data["frames"][key]["duration"]/1000,
            "w": w,
            "h": h,
            "texcoords": {},
        }

        frame["texcoords"]["tl"] = Vec((x)/width,(y)/height)
        frame["texcoords"]["tr"] = Vec((x+w)/width,(y)/height)
        frame["texcoords"]["bl"] = Vec((x)/width,(y+h)/height)
        frame["texcoords"]["br"] = Vec((x+w)/width,(y+h)/height)

        frames.append(frame)

    sheet = {}
    for tag in data["meta"]["frameTags"]:
        # no support for direction tag
        assert tag["direction"] == "forward"

        animframes = []
        i = tag["from"]
        while i <= tag["to"]:
            animframes.append(frames[i])
            i += 1

        sheet[tag["name"]] = animframes

    return frames, sheet

############################################################################################
from .listen import *
from collections import deque



global animator_counter
animator_counter = 0

class Animator():

    def __init__(self):
        self._queue = deque()
        self._paused = False
        self._loop = None # or a list

        global animator_counter
        animator_counter += 1
        self._id = "animator_"+str(animator_counter)+"_"

        launch(self._listener())

    def _event(self, name):
        event, *data = yield [self._id + name]
        return data

    def _listener(self):

        t = None

        while True:

            if len(self._queue) == 0:
                t = None
                yield from self._event("reset")
                continue
            else:
                if t == None:
                    t = self._queue[0]["data"]["duration"]

            if self._paused:
                while True:
                    events = yield from any(
                        unpause=self._event("unpause"),
                        reset=self._event("reset"))

                    if "unpause" in events:
                        break

                    if "reset" in events: t = None

                continue

            t0 = time.time()

            events = yield from any(
                        time=wait(t),
                        pause=self._event("pause"),
                        reset=self._event("reset"))

            if "pause" in events:
                t -= time.time() - t0
                continue

            if "reset" in events:
                t = None
                continue

            if "time" in events:
                t = None

                label_now = self._queue[0]["label"]

                self._queue.popleft()

                if len(self._queue) == 0 and self._loop != None:
                    for frame in self._loop:
                        self._queue.append(frame)
                    dispatch(self._id+"loop")
                elif len(self._queue) == 0:
                    dispatch(self._id+"end")
                else:
                    dispatch(self._id+"change")

                if len(self._queue) == 0:
                    if label_now != None:
                        dispatch(self._id+"label_change")
                else:
                    if label_now != self._queue[0]["label"]:
                        dispatch(self._id+"label_change")



    def __getitem__(self, key):
        if len(self._queue) == 0: raise KeyError
        return self._queue[0]["data"][key]

    def enqueue(self, frames, label=None, loop=False):
        assert len(frames) > 0

        if self._loop is not None:
            # we'll never get to these frames
            raise ValueError("Enqueued frames on looping animator.")

        if loop: self._loop = []

        should_emit_label_change = len(self._queue) == 0

        for frame in frames:
            assert "duration" in frame

            to_add = {
                "data": frame,
                "label": label
                }

            self._queue.append(to_add)
            if loop: self._loop.append(to_add)

        if should_emit_label_change:
            dispatch(self._id+"label_change")


        dispatch(self._id+"reset")

    def clear(self):
        self._queue.clear()
        self._loop = None
        dispatch(self._id+"reset")


    #######

    @property
    def label(self):
        if len(self._queue) == 0: return None
        return self._queue[0]["label"]

    @property
    def paused(self): return self._paused

    @paused.setter
    def paused(self,paused):
        if self._paused == paused: return
        self._paused = paused

        if paused: dispatch(self._id+"_pause")
        else: dispatch(self._id+"_unpause")

    #######

    # triggers immediately after we go to frame that changes the label
    def on_label_change(self): return self._event("label_change")

    # triggers before the start of any frame
    def on_change(self): return self._event("change")

    # triggers after the final frame is played
    def on_end(self): return self._event("end")

    # triggers after the final frame of a looping animation is played
    def on_loop(self): return self._event("loop")



